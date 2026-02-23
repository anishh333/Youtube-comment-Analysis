/**
 * background.js — Service Worker (Manifest V3)
 * Handles extension lifecycle events.
 */

chrome.runtime.onInstalled.addListener(() => {
    console.log("[YouTube Sentiment Analyzer] Extension installed.");
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    // Forward messages between content script and popup if needed
    if (message.type === "PING") {
        sendResponse({ type: "PONG" });
    }
    return true;
});
