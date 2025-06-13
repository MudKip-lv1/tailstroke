# Tails

**Tails** is a web-based image processing tool that allows users to blur images beautifully and intuitively.  
No coding skills required — it features a minimal, user-friendly interface. Future updates will include a wider range of image editing functions.

---

## Features

- Upload up to 10 images at once  
- Customize output image size freely  
- Supports downloading in JPG and PNG formats  
- Temporary storage (cleared on browser reload)  
- Minimal, modern UI inspired by Apple design  

---

## Run Locally

### 1. Clone and Setup

```bash
git clone https://github.com/your-username/tailstroke.git
cd tailstroke
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python app.py
```

Open the browser and go to:

```
http://127.0.0.1:5000
```

---

## Deploy to Render

1. Go to [https://dashboard.render.com/](https://dashboard.render.com/)
2. Click **New > Web Service**
3. Connect your GitHub repository
4. Set the following parameters:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Runtime**: Python 3.x
   - **Instance Type**: Free or Starter (depending on usage)
5. In the **Advanced Settings**, add this environment variable:
   - `PORT=10000` (or as needed)

Once deployed, you'll get a public URL like `https://your-app-name.onrender.com`.

---

## Project Structure

```
tailstroke/
├── app.py                # Main Flask app
├── templates/
│   └── index.html        # Frontend (Jinja2 template)
├── static/
│   ├── style.css         # CSS styling
│   ├── sample/           # Before/After sample images
│   └── tmp/              # Temporary upload folder
├── .gitignore
├── requirements.txt
└── README.md
```

---

## License

MIT License
