# 🎓 YouTube Sentiment Analyzer — Chrome Extension

A Chrome Extension that analyzes YouTube video comments and provides sentiment analysis (Positive / Negative / Neutral) with key insights.

> **🆓 Completely Free — No API Key Required!**
> Uses `youtube-comment-downloader` to fetch comments directly from YouTube — no Google Cloud setup, no quotas, no billing.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **Sentiment Breakdown** | % and count of Positive, Negative, Neutral comments |
| 🔑 **Key Insights** | Top keywords extracted from all comments |
| 💬 **Top Comments** | Best positive and negative comments displayed |
| 🎨 **Premium Dark UI** | Glassmorphism-styled popup with smooth animations |
| ⚡ **Fast** | Analyzes up to 500 comments in seconds |
| 🆓 **No API Key** | Works out of the box — zero configuration |

---

## 🏗️ Project Structure

```
Youtube-sentiment-analysis/
├── backend/
│   ├── app.py            ← Flask REST API
│   ├── analyzer.py       ← VADER sentiment engine + keyword extraction
│   └── config.py         ← Server & comment settings (no API key needed)
├── extension/
│   ├── manifest.json
│   ├── popup.html/css/js
│   ├── content.js
│   ├── background.js
│   └── icons/
├── requirements.txt
├── generate_icons.py
└── README.md
```

---

## 🚀 Setup Guide

### Step 1 — Install Python Dependencies

```powershell
cd d:\Youtube-sentiment-analysis
pip install -r requirements.txt
```

This installs:
- `flask` & `flask-cors` — Backend server
- `vaderSentiment` — Sentiment analysis model
- `youtube-comment-downloader` — Fetches comments directly (no API key!)
- `nltk` — Keyword extraction

### Step 2 — Start the Backend Server

```powershell
cd d:\Youtube-sentiment-analysis\backend
python app.py
```

You should see:
```
🚀 YouTube Sentiment Analyzer — http://localhost:5000
✅ No API key required — using youtube-comment-downloader
```

Leave this terminal window open while using the extension.

### Step 3 — Load the Extension in Chrome

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer Mode** (top-right toggle)
3. Click **Load unpacked**
4. Select the folder: `d:\Youtube-sentiment-analysis\extension\`
5. The extension icon appears in your Chrome toolbar ✅

### Step 4 — Use It!

1. Go to any YouTube video
2. Click the **YouTube Sentiment Analyzer** icon in your toolbar
3. Watch the analysis appear with animated bars and insights 🎉

---

## 🧠 How It Works

```
Chrome Extension
      ↓  (detects video ID from URL)
Flask Backend  →  youtube-comment-downloader  →  Scrapes up to 500 comments
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
| "Could not fetch comments" | Video may be private, age-restricted, or comments disabled |
| Extension not showing | Reload it at `chrome://extensions` |
| Slow first run | NLTK downloads required data on first launch |

---

## 📦 Dependencies

**Backend:** `flask`, `flask-cors`, `vaderSentiment`, `youtube-comment-downloader`, `nltk`

**Extension:** Pure JavaScript (no `node_modules` needed)

> **Note:** No `google-api-python-client` needed — this project uses `youtube-comment-downloader` which scrapes comments directly from YouTube without any API key.

---

## 📄 License

MIT — Free for educational use.
