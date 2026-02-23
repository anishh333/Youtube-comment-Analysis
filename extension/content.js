/**
 * content.js — Runs on YouTube pages
 * Extracts the current video ID and listens for messages from the popup.
 */

function getVideoId() {
  try {
    const url = new URL(window.location.href);
    if (url.hostname.includes("youtube.com")) {
      // Standard watch page: youtube.com/watch?v=VIDEO_ID
      const v = url.searchParams.get("v");
      if (v) return v;

      // Shorts: youtube.com/shorts/VIDEO_ID
      const shortsMatch = url.pathname.match(/\/shorts\/([a-zA-Z0-9_-]{11})/);
      if (shortsMatch) return shortsMatch[1];
    }
  } catch (e) {
    // Ignore URL parsing errors
  }
  return null;
}

// Listen for popup requesting the video ID
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "GET_VIDEO_ID") {
    const videoId = getVideoId();
    sendResponse({ videoId });
  }
  return true; // Keep channel open for async
});
