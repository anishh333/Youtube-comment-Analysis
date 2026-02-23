"""
app.py — Flask REST API for YouTube Comment Sentiment Analysis
Uses youtube-comment-downloader (no API key needed!) + VADER sentiment.
"""

import logging
import itertools
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

from config import MAX_COMMENTS, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from analyzer import analyze_comments

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ── Flask App ──────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)  # Allow all origins for local development

# One shared downloader instance
_downloader = YoutubeCommentDownloader()


# ── YouTube comment fetcher (no API key!) ──────────────────────────────────

def fetch_comments(video_id: str, max_results: int = MAX_COMMENTS) -> tuple[list[str], str]:
    """
    Fetch comments using youtube-comment-downloader (no API key needed).
    Returns (list_of_comment_texts, video_title_placeholder).
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    log.info(f"Fetching comments for: {url}")

    try:
        comments_gen = _downloader.get_comments_from_url(
            url, sort_by=SORT_BY_POPULAR
        )
        # Take up to max_results comments
        comments_data = list(itertools.islice(comments_gen, max_results))
    except Exception as e:
        err = str(e).lower()
        if "sign in" in err or "age" in err:
            raise ValueError(
                "This video requires sign-in or is age-restricted. "
                "Try a different video."
            )
        if "disabled" in err or "not available" in err:
            raise ValueError(
                "Comments are disabled for this video."
            )
        raise ValueError(f"Could not fetch comments: {e}")

    texts = [c.get("text", "").strip() for c in comments_data if c.get("text", "").strip()]
    log.info(f"Fetched {len(texts)} comments for video {video_id}")

    # We don't get the title from this library; we'll return a placeholder.
    # The extension will show the video ID and count instead.
    video_title = f"YouTube Video ({video_id})"
    return texts, video_title


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "YouTube Sentiment Analyzer",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze  body: {videoId: string}"
        },
        "note": "No API key required!"
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "YouTube Sentiment Analyzer is running (no API key required!)"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    POST /analyze
    Body: { "videoId": "dQw4w9WgXcQ" }
    Returns: full sentiment analysis JSON
    """
    data = request.get_json(silent=True)
    if not data or "videoId" not in data:
        return jsonify({"error": "Missing 'videoId' in request body"}), 400

    video_id = data["videoId"].strip()
    if not video_id:
        return jsonify({"error": "videoId cannot be empty"}), 400

    # Accept full YouTube URL or just video ID
    if "youtube.com" in video_id or "youtu.be" in video_id:
        # Extract ID from URL if user sends full URL
        import re
        match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", video_id)
        if match:
            video_id = match.group(1)

    log.info(f"Analyzing video: {video_id}")

    try:
        comments, video_title = fetch_comments(video_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return jsonify({"error": "Failed to fetch comments. Make sure the video is public and has comments enabled."}), 500

    if not comments:
        return jsonify({
            "error": "No comments could be fetched. The video may have comments disabled, "
                     "be private, or require sign-in. Please try a different public video."
        }), 400

    result = analyze_comments(comments)
    result["video_id"]    = video_id
    result["video_title"] = video_title

    return jsonify(result)


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info(f"🚀 YouTube Sentiment Analyzer — http://localhost:{FLASK_PORT}")
    log.info("✅ No API key required — using youtube-comment-downloader")
    log.info("Press Ctrl+C to stop.")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
