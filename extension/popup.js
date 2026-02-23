/**
 * popup.js — YouTube Sentiment Analyzer Extension
 * Handles: video detection, API calls, UI rendering
 */

const BACKEND_URL = "http://localhost:5000";

// ── DOM refs ───────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const statusDot = $("status-dot");
const videoInfo = $("video-info");
const videoThumb = $("video-thumb");
const videoTitle = $("video-title");
const commentCount = $("comment-count");

const stateNotYT = $("state-not-youtube");
const stateLoading = $("state-loading");
const loadingMsg = $("loading-msg");
const stateError = $("state-error");
const errorMsg = $("error-msg");
const btnRetry = $("btn-retry");
const stateResults = $("state-results");

const overallLabel = $("overall-label");
const avgScore = $("avg-score");

const verdictCard = $("verdict-card");
const verdictBadge = $("verdict-badge");
const verdictReason = $("verdict-reason");
const barPositive = $("bar-positive");
const barNeutral = $("bar-neutral");
const barNegative = $("bar-negative");
const pctPositive = $("pct-positive");
const pctNeutral = $("pct-neutral");
const pctNegative = $("pct-negative");
const cntPositive = $("cnt-positive");
const cntNeutral = $("cnt-neutral");
const cntNegative = $("cnt-negative");

const insightsContainer = $("insights-container");
const listPositive = $("list-positive");
const listNegative = $("list-negative");
const btnReanalyze = $("btn-reanalyze");

// Tab buttons
const tabPositive = $("tab-positive");
const tabNegative = $("tab-negative");
const commentsPositive = $("comments-positive");
const commentsNegative = $("comments-negative");

// ── State ──────────────────────────────────────────────────────────────────
let currentVideoId = null;

// ── Show/hide helpers ──────────────────────────────────────────────────────
function showOnly(...panels) {
    [stateNotYT, stateLoading, stateError, stateResults].forEach((p) => {
        p.classList.toggle("hidden", !panels.includes(p));
    });
}

function setVideoInfoVisible(show) {
    videoInfo.classList.toggle("hidden", !show);
}

// ── Backend health check ───────────────────────────────────────────────────
async function checkBackend() {
    statusDot.className = "status-dot checking";
    try {
        const res = await fetch(`${BACKEND_URL}/health`, { method: "GET" });
        if (res.ok) {
            statusDot.className = "status-dot online";
            statusDot.title = "Backend online ✓";
            return true;
        }
    } catch (_) { /* ignore */ }
    statusDot.className = "status-dot offline";
    statusDot.title = "Backend offline — run python app.py";
    return false;
}

// ── Get current video ID from content script ───────────────────────────────
async function getCurrentVideoId() {
    return new Promise((resolve) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (!tabs[0]) return resolve(null);
            const tab = tabs[0];
            // Quick URL check
            if (!tab.url || !tab.url.includes("youtube.com/watch") && !tab.url.includes("youtube.com/shorts")) {
                return resolve(null);
            }
            chrome.tabs.sendMessage(tab.id, { type: "GET_VIDEO_ID" }, (resp) => {
                if (chrome.runtime.lastError || !resp) return resolve(null);
                resolve(resp.videoId || null);
            });
        });
    });
}

// ── Render helpers ─────────────────────────────────────────────────────────
function animateBar(el, pct) {
    // Tiny delay so CSS transition fires
    setTimeout(() => { el.style.width = pct + "%"; }, 50);
}

function renderResults(data, videoId) {
    // Video meta
    videoTitle.textContent = data.video_title || "Unknown Video";
    commentCount.textContent = `${data.total} comments analyzed`;
    videoThumb.src = `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
    setVideoInfoVisible(true);

    // Overall label
    overallLabel.textContent = data.sentiment_label;
    const score = data.average_compound;
    const sign = score > 0 ? "+" : "";
    avgScore.textContent = `Overall score: ${sign}${score.toFixed(3)}`;

    // Colour the gradient by sentiment
    if (score > 0.05) overallLabel.style.background = "linear-gradient(90deg, #22d3a5, #a855f7)";
    else if (score < -0.05) overallLabel.style.background = "linear-gradient(90deg, #f87171, #a855f7)";
    else overallLabel.style.background = "linear-gradient(90deg, #60a5fa, #a855f7)";
    overallLabel.style.webkitBackgroundClip = "text";
    overallLabel.style.webkitTextFillColor = "transparent";

    // Bars
    animateBar(barPositive, data.positive_pct);
    animateBar(barNeutral, data.neutral_pct);
    animateBar(barNegative, data.negative_pct);

    pctPositive.textContent = data.positive_pct + "%";
    pctNeutral.textContent = data.neutral_pct + "%";
    pctNegative.textContent = data.negative_pct + "%";
    cntPositive.textContent = data.positive;
    cntNeutral.textContent = data.neutral;
    cntNegative.textContent = data.negative;

    // Key Insights chips
    insightsContainer.innerHTML = "";
    if (data.key_insights && data.key_insights.length > 0) {
        data.key_insights.forEach((word, i) => {
            const chip = document.createElement("span");
            chip.className = "insight-chip";
            chip.style.animationDelay = `${i * 40}ms`;
            chip.textContent = word;
            insightsContainer.appendChild(chip);
        });
    } else {
        insightsContainer.innerHTML = '<span style="font-size:11px;color:var(--text-muted)">No keywords extracted.</span>';
    }

    // Worth Watching verdict
    const worth = data.worth_watching || "maybe";
    verdictCard.className = `verdict-card verdict-${worth}`;
    verdictCard.classList.remove("hidden");
    const badgeMap = { yes: "✅ YES", maybe: "🤔 MAYBE", no: "❌ NO" };
    verdictBadge.textContent = badgeMap[worth] || worth.toUpperCase();
    verdictReason.textContent = data.worth_reason || "";

    // Top comments
    renderCommentList(listPositive, data.top_comments.top_positive, "positive");
    renderCommentList(listNegative, data.top_comments.top_negative, "negative");

    showOnly(stateResults);
}

function renderCommentList(container, comments, type) {
    container.innerHTML = "";
    if (!comments || comments.length === 0) {
        container.innerHTML = `<p class="no-comments">No ${type} comments found.</p>`;
        return;
    }
    comments.forEach((text) => {
        const card = document.createElement("div");
        card.className = `comment-card ${type}-card`;
        card.textContent = text.length > 200 ? text.slice(0, 200) + "…" : text;
        container.appendChild(card);
    });
}

// ── Tab switching ──────────────────────────────────────────────────────────
function setupTabs() {
    [tabPositive, tabNegative].forEach((btn) => {
        btn.addEventListener("click", () => {
            const tab = btn.dataset.tab;
            tabPositive.classList.toggle("active", tab === "positive");
            tabNegative.classList.toggle("active", tab === "negative");
            commentsPositive.classList.toggle("active", tab === "positive");
            commentsNegative.classList.toggle("active", tab === "negative");
        });
    });
}

// ── Main analyze flow ──────────────────────────────────────────────────────
async function analyze(videoId) {
    currentVideoId = videoId;
    showOnly(stateLoading);
    setVideoInfoVisible(false);
    loadingMsg.textContent = "Fetching comments from YouTube…";

    // Reset bars instantly (before animation)
    [barPositive, barNeutral, barNegative].forEach(b => b.style.width = "0%");

    // Check backend health first
    const isOnline = await checkBackend();
    if (!isOnline) {
        showOnly(stateError);
        errorMsg.textContent =
            "Cannot reach the backend. Make sure you ran:\n\n  cd backend && python app.py";
        return;
    }

    loadingMsg.textContent = "Analyzing sentiment with VADER AI…";

    try {
        const res = await fetch(`${BACKEND_URL}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ videoId }),
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.error || `Server error ${res.status}`);
        }

        renderResults(data, videoId);
    } catch (err) {
        showOnly(stateError);
        errorMsg.textContent = err.message || "An unexpected error occurred.";
    }
}

// ── Init ───────────────────────────────────────────────────────────────────
async function init() {
    setupTabs();

    // Check backend status (non-blocking)
    checkBackend();

    // Retry button
    btnRetry.addEventListener("click", () => {
        if (currentVideoId) analyze(currentVideoId);
    });

    // Re-analyze button
    btnReanalyze.addEventListener("click", () => {
        if (currentVideoId) analyze(currentVideoId);
    });

    // Get video ID
    const videoId = await getCurrentVideoId();

    if (!videoId) {
        showOnly(stateNotYT);
        return;
    }

    await analyze(videoId);
}

document.addEventListener("DOMContentLoaded", init);
