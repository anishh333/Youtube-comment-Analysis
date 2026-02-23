"""
analyzer.py — Sentiment Analysis + Key Insights Engine
Uses VADER for sentiment scoring and NLTK for keyword extraction.
"""

import re
from collections import Counter

import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Download stopwords once — safe to call even if already downloaded
nltk.download("stopwords", quiet=True)

from nltk.corpus import stopwords

# Initialize VADER
_analyzer = SentimentIntensityAnalyzer()
_stop_words = set(stopwords.words("english"))

# Extra noise words to filter from key insights
_EXTRA_STOP = {
    "video", "videos", "watch", "watched", "like", "liked", "comment",
    "comments", "please", "thank", "thanks", "subscribe", "subscribed",
    "channel", "youtube", "really", "great", "good", "amazing", "best",
    "love", "need", "time", "make", "just", "one", "also", "get", "see",
    "well", "know", "people", "much", "many", "even", "still", "going",
    "think", "would", "could", "should", "want", "very", "so", "this",
    "that", "these", "those", "it", "is", "are", "was", "been",
}


def _classify(compound: float) -> str:
    """Classify a VADER compound score into positive/negative/neutral."""
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def _clean_text(text: str) -> str:
    """Remove URLs, mentions, emojis (basic), and extra whitespace."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # Remove non-ASCII (emojis etc.)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_keywords(comments: list[str], top_n: int = 10) -> list[str]:
    """Extract top keywords from all comments using word frequency."""
    all_words = []
    for comment in comments:
        cleaned = _clean_text(comment).lower()
        # Simple regex tokenizer — no NLTK punkt data needed
        tokens = re.findall(r"\b[a-z]+\b", cleaned)
        filtered = [
            w for w in tokens
            if len(w) > 3
            and w not in _stop_words
            and w not in _EXTRA_STOP
        ]
        all_words.extend(filtered)

    freq = Counter(all_words)
    return [word for word, _ in freq.most_common(top_n)]


def _get_top_comments(
    scored_comments: list[dict], n: int = 3
) -> dict:
    """Return top N most positive and most negative comments."""
    positives = sorted(
        [c for c in scored_comments if c["sentiment"] == "positive"],
        key=lambda x: x["compound"],
        reverse=True,
    )
    negatives = sorted(
        [c for c in scored_comments if c["sentiment"] == "negative"],
        key=lambda x: x["compound"],
    )
    return {
        "top_positive": [c["text"] for c in positives[:n]],
        "top_negative": [c["text"] for c in negatives[:n]],
    }


def analyze_comments(comments: list[str]) -> dict:
    """
    Analyze a list of comment strings and return sentiment stats + insights.

    Returns:
        {
            total: int,
            positive: int, negative: int, neutral: int,
            positive_pct: float, negative_pct: float, neutral_pct: float,
            average_compound: float,     # Overall sentiment score -1 to 1
            sentiment_label: str,        # "Mostly Positive" etc.
            key_insights: list[str],     # Top keywords
            top_comments: {
                top_positive: list[str],
                top_negative: list[str]
            }
        }
    """
    if not comments:
        return {
            "total": 0,
            "positive": 0, "negative": 0, "neutral": 0,
            "positive_pct": 0.0, "negative_pct": 0.0, "neutral_pct": 0.0,
            "average_compound": 0.0,
            "sentiment_label": "No Comments Found",
            "key_insights": [],
            "top_comments": {"top_positive": [], "top_negative": []},
        }

    scored = []
    compound_sum = 0.0

    for text in comments:
        cleaned = _clean_text(text)
        scores = _analyzer.polarity_scores(cleaned)
        compound = scores["compound"]
        compound_sum += compound
        scored.append({
            "text": text[:280],  # Truncate for display
            "compound": compound,
            "sentiment": _classify(compound),
        })

    total = len(scored)
    pos = sum(1 for c in scored if c["sentiment"] == "positive")
    neg = sum(1 for c in scored if c["sentiment"] == "negative")
    neu = total - pos - neg
    avg_compound = round(compound_sum / total, 4)

    # Overall sentiment label
    pos_pct = round((pos / total) * 100, 1)
    neg_pct = round((neg / total) * 100, 1)

    if pos_pct >= 60:
        label = "Highly Positive"
    elif pos_pct >= 40:
        label = "Mostly Positive"
    elif neg_pct >= 60:
        label = "Highly Negative"
    elif neg_pct >= 40:
        label = "Mostly Negative"
    else:
        label = "Mixed / Neutral"

    key_insights = _extract_keywords(comments, top_n=10)
    top_comments = _get_top_comments(scored)

    # Worth watching verdict
    if pos_pct >= 50 and avg_compound >= 0:
        worth = "yes"
        worth_reason = "Most viewers found this video helpful and valuable."
    elif pos_pct >= 35 and neg_pct < 40:
        worth = "maybe"
        worth_reason = "Viewers have mixed feelings — it may be useful depending on your level."
    else:
        worth = "no"
        worth_reason = "Many viewers found this video unhelpful or confusing."

    return {
        "total": total,
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "positive_pct": pos_pct,
        "negative_pct": neg_pct,
        "neutral_pct": round(100 - pos_pct - neg_pct, 1),
        "average_compound": avg_compound,
        "sentiment_label": label,
        "worth_watching": worth,
        "worth_reason": worth_reason,
        "key_insights": key_insights,
        "top_comments": top_comments,
    }
