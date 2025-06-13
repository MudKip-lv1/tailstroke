import os
import logging
import traceback
from flask import Flask, render_template, request, send_file, session, jsonify
from PIL import Image, ImageFilter, ImageEnhance, ExifTags
import uuid
import time
import glob
from datetime import timedelta
import werkzeug
import tempfile
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理用
TMP_DIR = os.path.join('static', 'tmp')
os.makedirs(TMP_DIR, exist_ok=True)

# セッションの有効期限
app.permanent_session_lifetime = timedelta(hours=1)

# 詳細なログを出力
logging.basicConfig(level=logging.DEBUG)

def cleanup_tmp_dir(expire_sec=1800):
    """30分以上前のファイルを削除"""
    now = time.time()
    for f in glob.glob(os.path.join(TMP_DIR, '*')):
        if os.path.isfile(f) and now - os.path.getmtime(f) > expire_sec:
            try:
                os.remove(f)
            except Exception:
                pass

def ensure_tmp_files():
    if 'tmp_files' not in session:
        session['tmp_files'] = []

@app.route('/')
def index():
    session.permanent = True
    ensure_tmp_files()

    sample_images = [
        {
            "title": "SAMPLE",
            "before": "static/sample/sample.png",
            "after": "static/sample/sample_975d6d172f794362b11e1199aca25450.jpg"
        },
        {
            "title": "SAMPLE2",
            "before": "static/sample/sample_2.png",
            "after": "static/sample/sample_2_438f02d3183f4c00af756881401591cf.png"
        }
    ]

    return render_template('index.html', sample_images=sample_images)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        ensure_tmp_files()
        files = request.files.getlist('image')
        if not files or len(files) == 0:
            return "No file uploaded", 400
        if len(files) > 10:
            return "最大10枚までアップロードできます。", 400

        width = int(request.form.get('width', 800))
        height = int(request.form.get('height', 600))
        output_format = request.form.get('format', 'jpg').lower()
        allowed_ext = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
        allowed_formats = {'jpg', 'jpeg', 'png', 'webp'}
        if output_format not in allowed_formats:
            output_format = 'jpg'
        results = []

        for file in files:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext not in allowed_ext:
                continue
            original_name = werkzeug.utils.secure_filename(file.filename.rsplit('.', 1)[0])
            img = Image.open(file)

            # EXIFの回転情報を適用（JPEGのみ有効）
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation, None)
                    if orientation_value == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation_value == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation_value == 8:
                        img = img.rotate(90, expand=True)
            except Exception:
                pass

            # 形式ごとにモードを変換
            if output_format in ['jpg', 'jpeg']:
                img = img.convert("RGB")
            elif output_format == 'png':
                img = img.convert("RGBA")

            # サイズ調整
            if img.width > width or img.height > height:
                img.thumbnail((width, height), Image.LANCZOS)

            # 背景生成・合成
            bg = img.resize((width, height), Image.LANCZOS)
            if bg.mode != "RGB":
                bg = bg.convert("RGB")
            bg = bg.filter(ImageFilter.GaussianBlur(radius=25))
            enhancer = ImageEnhance.Brightness(bg)
            bg = enhancer.enhance(0.5)
            x = (width - img.width) // 2
            y = (height - img.height) // 2
            canvas = bg.copy()
            if output_format == 'png':
                img = img.convert("RGBA")
                canvas = canvas.convert("RGBA")
                canvas.paste(img, (x, y), img)
            else:
                canvas.paste(img, (x, y))

            # セッションに記録
            ensure_tmp_files()
            session['tmp_files'].append(output_filename)

            # 保存処理
            if output_format in ['jpg', 'jpeg']:
                output_ext = 'jpg'
                output_filename = f"{original_name}_{uuid.uuid4().hex}.{output_ext}"
                output_path = os.path.join(TMP_DIR, output_filename)
                canvas.save(output_path, format="JPEG", quality=95)
            elif output_format == 'png':
                output_filename = f"{original_name}_{uuid.uuid4().hex}.png"
                output_path = os.path.join(TMP_DIR, output_filename)
                canvas.save(output_path, format="PNG")
            elif output_format == 'webp':
                output_filename = f"{original_name}_{uuid.uuid4().hex}.webp"
                output_path = os.path.join(TMP_DIR, output_filename)
                canvas.save(output_path, format="WEBP", quality=95, method=6)
            else:
                output_filename = f"{original_name}_{uuid.uuid4().hex}.{output_format}"
                output_path = os.path.join(TMP_DIR, output_filename)
                canvas.save(output_path)

            # クライアントに返す情報
            results.append({
                "url": f"/static/tmp/{output_filename}",
                "filename": output_filename
            })

        session.modified = True
        cleanup_tmp_dir()
        return jsonify(results)
    except Exception as e:
        logging.error("Exception occurred during upload:")
        logging.error(traceback.format_exc())
        return f"エラーが発生しました: {e}", 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    ensure_tmp_files()
    for fname in session.get('tmp_files', []):
        fpath = os.path.join(TMP_DIR, fname)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass
    session['tmp_files'] = []
    session.modified = True
    return '', 204

@app.route('/upload_tempfile', methods=['POST'])
def upload_tempfile():
    file = request.files['image']
    if not file:
        return "No file uploaded", 400

    image = Image.open(file.stream)
    logging.debug(f"Original image mode: {image.mode}, size: {image.size}")

    # 画像処理
    canvas = image.filter(ImageFilter.GaussianBlur(10))
    logging.debug(f"Canvas mode after filter: {canvas.mode}, size: {canvas.size}")

    # PNG保存時はRGBまたはRGBAが安全
    if canvas.mode not in ("RGB", "RGBA"):
        canvas = canvas.convert("RGBA")
        logging.debug(f"Canvas converted mode: {canvas.mode}")

    img_io = BytesIO()
    try:
        canvas.save(img_io, format='PNG')
        img_io.seek(0)
        img_size = len(img_io.getvalue())
        logging.debug(f"BytesIO image size: {img_size} bytes")
    except Exception as e:
        logging.error(f"Failed to save image to BytesIO: {e}")
        return "Image processing error", 500

    response = send_file(
        img_io,
        mimetype='image/png',
        as_attachment=False,
        download_name='processed.png'
    )
    @response.call_on_close
    def cleanup():
        pass
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    host = "0.0.0.0"
    # ルート一覧をログ出力
    with app.app_context():
        logging.info("📌 Available routes:")
        for rule in app.url_map.iter_rules():
            logging.info(f"  {rule}")
    app.run(host=host, port=port)