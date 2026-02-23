# 🎓 YouTube Sentiment Analyzer — Chrome Extension

A Chrome Extension that analyzes YouTube video comments and provides sentiment analysis (Positive / Negative / Neutral) with key insights — focused on **educational content**.

> **No cloud required.** Uses VADER — a lightweight AI model running entirely on your local machine.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Sentiment Breakdown** | % and count of Positive, Negative, Neutral comments |
| 🔑 **Key Insights** | Top keywords extracted from all comments |
| 💬 **Top Comments** | Best positive and negative comments displayed |
| 🎨 **Premium Dark UI** | Glassmorphism-styled popup with smooth animations |
| ⚡ **Fast** | Analyzes up to 500 comments in seconds |

---

## 🏗️ Project Structure

```
Youtube-sentiment-analysis/
├── backend/
│   ├── app.py          ← Flask REST API
│   ├── analyzer.py     ← VADER sentiment engine
│   ├── config.py       ← 👈 Paste your API key here
│   └── requirements.txt
├── extension/
│   ├── manifest.json
│   ├── popup.html/css/js
│   ├── content.js
│   ├── background.js
│   └── icons/
├── generate_icons.py
└── README.md
```

---

## 🚀 Setup Guide

### Step 1 — Get a YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Go to **APIs & Services → Library**
4. Search **"YouTube Data API v3"** → **Enable**
5. Go to **APIs & Services → Credentials**
6. Click **Create Credentials → API key**
7. Copy the key

### Step 2 — Configure the API Key

Open `backend/config.py` and replace the placeholder:

```python
YOUTUBE_API_KEY = "AIzaSy..."   # ← paste your key here
```

### Step 3 — Start the Backend Server

```powershell
cd d:\Youtube-sentiment-analysis\backend
python app.py
```

You should see:
```
Starting YouTube Sentiment Analyzer on http://localhost:5000
```

Leave this terminal window open while using the extension.

### Step 4 — Load the Extension in Chrome

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer Mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the folder: `d:\Youtube-sentiment-analysis\extension\`
5. The extension icon appears in your Chrome toolbar ✅

### Step 5 — Use It!

1. Go to any YouTube video (e.g. a Khan Academy, Veritasium, or 3Blue1Brown video)
2. Click the **YouTube Sentiment Analyzer** icon in your toolbar
3. Watch the analysis appear with animated bars and insights 🎉

---

## 🧠 How It Works

```
Chrome Extension
      ↓  (detects video ID from URL)
Flask Backend  →  YouTube Data API v3  →  Fetch up to 500 comments
      ↓
VADER Sentiment Model  →  Score each comment (-1.0 to +1.0)
      ↓
NLTK Keyword Extraction  →  Key topics from all comments
      ↓
JSON Response  →  Extension renders results
```

### Sentiment Classification

| Label | VADER Compound Score |
|---|---|
| ✅ Positive | ≥ +0.05 |
| ⚪ Neutral | -0.05 to +0.05 |
| ❌ Negative | ≤ -0.05 |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| Red dot (backend offline) | Run `python app.py` in `backend/` folder |
| "API key not configured" | Add your key to `backend/config.py` |
| "Comments disabled" | Video has comments turned off |
| Extension not showing | Reload it at `chrome://extensions` |

---

## 📦 Dependencies

**Backend:** `flask`, `flask-cors`, `vaderSentiment`, `google-api-python-client`, `nltk`

**Extension:** Pure JavaScript (no `node_modules` needed)

---

## 📄 License

MIT — Free for educational use.
