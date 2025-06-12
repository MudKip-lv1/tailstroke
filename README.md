# 🖌️ Tailstroke

**Tailstroke** は、画像を美しくぼかして仕上げるWebベースの画像加工ツールです。  
ノーコードで直感的に使えるインターフェースを備え、今後は多彩な画像編集機能の拡張も予定しています。

---

## 🚀 Features

- 🖼️ 最大10枚の画像を同時アップロード可能  
- 🔧 出力サイズを自由に指定  
- 💾 JPG / PNG形式でダウンロード対応  
- ⚡ 一時保存（ブラウザリロードで削除）  
- 🌐 Apple風のモダンでミニマルなUI  

---

## 🧪 ローカル環境での実行方法

### 1. 環境構築

```bash
git clone https://github.com/your-username/tailstroke.git
cd tailstroke
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. サーバー起動

```bash
python app.py
```

ブラウザで以下にアクセス：  
`http://127.0.0.1:5000`

---

## 🗂️ プロジェクト構成

```
tailstroke/
├── app.py                # Flaskアプリ本体
├── templates/
│   └── index.html        # フロントエンドUI
├── static/
│   ├── style.css         # スタイリング
│   └── tmp/              # 一時画像ファイル格納用
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📄 ライセンス

MIT License
