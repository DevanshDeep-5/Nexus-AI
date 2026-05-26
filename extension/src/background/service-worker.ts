import { API_BASE_URL } from "../sidepanel/lib/constants";

// Open the side panel when the extension icon is clicked
chrome.action.onClicked.addListener(async (tab) => {
  if (tab.id) {
    await chrome.sidePanel.open({ tabId: tab.id });
  }
});

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

  if (message.type === "GET_PAGE_CONTENT") {
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
      const tab = tabs[0];
      if (!tab?.id) {
        sendResponse({ error: "No active tab found" });
        return;
      }

      try {
        const response = await chrome.tabs.sendMessage(tab.id, { type: "EXTRACT_CONTENT" });
        sendResponse(response);
      } catch {
        sendResponse({
          error: "Could not read this page. Refresh the tab, then click Refresh in the extension.",
        });
      }
    });

    return true; // Keep message channel open for async response
  }

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
