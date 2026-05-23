/**
 * Background Service Worker
 * ---------------------------
 * The "brain" of the Chrome extension that runs in the background.
 * It acts as a message relay between:
 *   - The side panel (React UI)  →  sends requests for page content
 *   - The content script (page)  →  extracts text and handles highlighting
 *
 * Main responsibilities:
 *   1. Opens the side panel when the extension icon is clicked
 *   2. Relays GET_PAGE_CONTENT requests from the panel to the content script
 *   3. Relays HIGHLIGHT_SOURCE requests from the panel to the content script
 */

import { API_BASE_URL } from "../sidepanel/lib/constants";

// ── Side Panel Setup ───────────────────────────────────────────────

// Open the side panel when the user clicks the extension icon in the toolbar
chrome.action.onClicked.addListener(async (tab) => {
  if (tab.id) {
    await chrome.sidePanel.open({ tabId: tab.id });
  }
});

// Configure Chrome to automatically open the side panel on icon click
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});


// ── Message Relay System ───────────────────────────────────────────
// The side panel can't talk directly to the content script, so the
// service worker acts as a middleman, forwarding messages between them.

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  // ── Request: Get page content ──────────────────────────────────
  // The side panel asks for the current page's text content.
  // We forward this to the content script on the active tab.
  if (message.type === "GET_PAGE_CONTENT") {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (!tab?.id) {
        sendResponse({ error: "No active tab found" });
        return;
      }

      try {
        const response = await chrome.tabs.sendMessage(tab.id, {
          type: "EXTRACT_CONTENT",
        });
        sendResponse(response);
      } catch {
        sendResponse({
          error:
            "Could not read this page. Refresh the tab, then click Refresh in the extension.",
        });
      }
    });

    // Return true to keep the message channel open for the async response
    return true;
  }

  // ── Request: Highlight source text on page ─────────────────────
  // When the user clicks a source excerpt in the chat, we forward
  // the highlight request to the content script to mark it on the page.
  if (message.type === "HIGHLIGHT_SOURCE") {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (tab?.id) {
        chrome.tabs.sendMessage(tab.id, {
          type: "HIGHLIGHT_TEXT",
          payload: message.payload,
        }).catch(() => {});
      }
    });
    return false;
  }

  // ── Request: Floating menu action (explain / simplify / etc.) ───
  if (message.type === "HIGHLIGHT_ACTION") {
    const { selectedText, action, pageContext } = message.payload ?? {};

    (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/highlight-action`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            selected_text: selectedText,
            action,
            page_context: pageContext ?? "",
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          sendResponse({
            error: typeof err.detail === "string" ? err.detail : "Highlight action failed",
          });
          return;
        }
        const data = await res.json();
        sendResponse({ result: data.result });
      } catch {
        sendResponse({ error: "Backend unavailable. Start uvicorn on port 8000." });
      }
    })();

    return true;
  }

  return false;
});
