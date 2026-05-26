function extractPageContent(): {
  content: string;
  title: string;
  url: string;
  isYouTube: boolean;
  videoId?: string;
} {
  const url = window.location.href;
  const title = document.title;

  const ytMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  const isYouTube = !!ytMatch;
  const videoId = ytMatch?.[1];

  const excludeSelectors = [
    "script", "style", "noscript", "iframe", "nav", "footer", "header",
    ".nav", ".footer", ".header", ".sidebar", ".advertisement", ".ad", ".ads",
    ".cookie", ".modal", ".popup", "[role='navigation']", "[role='banner']",
    "[role='contentinfo']", "[aria-hidden='true']",
  ];

  const clone = document.body.cloneNode(true) as HTMLElement;
  excludeSelectors.forEach((sel) => clone.querySelectorAll(sel).forEach((el) => el.remove()));

  const mainContent =
    clone.querySelector("main") ||
    clone.querySelector("article") ||
    clone.querySelector('[role="main"]') ||
    clone.querySelector(".post-content") ||
    clone.querySelector(".article-content") ||
    clone.querySelector(".entry-content");

  let content = (mainContent?.textContent || clone.textContent || "").trim();
  content = content.replace(/\s+/g, " ").replace(/\n{3,}/g, "\n\n").trim();

  if (content.length > 100000) {
    content = content.substring(0, 100000) + "\n\n[Content truncated]";
  }

  return { content, title, url, isYouTube, videoId };
}

let floatingMenu: HTMLElement | null = null;

function createFloatingMenu() {
  if (floatingMenu) return;

  const host = document.createElement("div");
  host.id = "ask-page-ai-float-host";
  const shadow = host.attachShadow({ mode: "open" });

  const style = document.createElement("style");
  style.textContent = `
    .atp-float-menu {
      display: none;
      position: fixed;
      z-index: 2147483647;
      background: linear-gradient(135deg, #1a1d2b 0%, #282d3e 100%);
      border: 1px solid rgba(124, 92, 252, 0.3);
      border-radius: 12px;
      padding: 4px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 30px rgba(124,92,252,0.15);
      backdrop-filter: blur(20px);
      font-family: 'Inter', system-ui, sans-serif;
      animation: atp-pop-in 0.2s ease-out;
    }
    .atp-float-menu.visible { display: flex; gap: 2px; }
    @keyframes atp-pop-in {
      from { transform: scale(0.9) translateY(5px); opacity: 0; }
      to { transform: scale(1) translateY(0); opacity: 1; }
    }
    .atp-action-btn {
      display: flex;
      align-items: center;
      gap: 5px;
      padding: 8px 12px;
      border: none;
      background: transparent;
      color: #e5e8f0;
      font-size: 12px;
      font-weight: 500;
      font-family: inherit;
      border-radius: 8px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .atp-action-btn:hover {
      background: rgba(124, 92, 252, 0.2);
      color: #c7c4ff;
    }
  `;

  const menu = document.createElement("div");
  menu.className = "atp-float-menu";

  const actions = [
    { icon: "💡", label: "Explain", action: "explain" },
    { icon: "✨", label: "Simplify", action: "simplify" },
    { icon: "📝", label: "Summarize", action: "summarize" },
    { icon: "📋", label: "Examples", action: "examples" },
  ];

  actions.forEach(({ icon, label, action }) => {
    const btn = document.createElement("button");
    btn.className = "atp-action-btn";
    btn.innerHTML = `<span class="atp-icon">${icon}</span>${label}`;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const selectedText = window.getSelection()?.toString().trim();

      if (selectedText) {
        chrome.runtime.sendMessage(
          {
            type: "HIGHLIGHT_ACTION",
            payload: {
              selectedText,
              action,
              pageContext: extractPageContent().content.substring(0, 3000),
            },
          },
          (response) => {
            if (chrome.runtime.lastError) {
              showToast("Extension error. Try refreshing the page.", true);
              return;
            }
            if (response?.error) {
              showToast(response.error, true);
              return;
            }
            if (response?.result) {
              showToast(response.result.slice(0, 500));
            }
          }
        );
      }

      hideFloatingMenu();
    });

    menu.appendChild(btn);
  });

  shadow.appendChild(style);
  shadow.appendChild(menu);
  document.body.appendChild(host);
  floatingMenu = menu;
}

function showFloatingMenu(x: number, y: number) {
  if (!floatingMenu) createFloatingMenu();
  if (!floatingMenu) return;

  const menuWidth = 380;
  const menuHeight = 44;
  let left = x - menuWidth / 2;
  let top = y - menuHeight - 10;

  left = Math.max(10, Math.min(left, window.innerWidth - menuWidth - 10));
  if (top < 10) top = y + 20;

  floatingMenu.style.left = `${left}px`;
  floatingMenu.style.top = `${top}px`;
  floatingMenu.classList.add("visible");
}

function hideFloatingMenu() {
  floatingMenu?.classList.remove("visible");
}

function highlightTextOnPage(searchText: string) {
  // Clear previous highlights
  document.querySelectorAll(".atp-highlight").forEach((el) => {
    const parent = el.parentNode;
    if (parent) {
      parent.replaceChild(document.createTextNode(el.textContent || ""), el);
      parent.normalize();
    }
  });

  if (!searchText || searchText.length < 10) return;
  const search = searchText.substring(0, 200).trim();

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        const tag = parent.tagName.toLowerCase();
        if (["script", "style", "noscript"].includes(tag)) return NodeFilter.FILTER_REJECT;
        if (parent.closest("#ask-page-ai-float-host")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    }
  );

  const textNodes: Text[] = [];
  let node: Node | null;
  while ((node = walker.nextNode())) {
    textNodes.push(node as Text);
  }

  const normalizedSearch = search.replace(/\s+/g, " ").toLowerCase();

  for (const tn of textNodes) {
    const text = tn.textContent || "";
    const idx = text.toLowerCase().indexOf(normalizedSearch.substring(0, Math.min(40, normalizedSearch.length)));

    if (idx !== -1) {
      try {
        const range = document.createRange();
        range.setStart(tn, idx);
        range.setEnd(tn, Math.min(idx + search.length, text.length));

        const mark = document.createElement("mark");
        mark.className = "atp-highlight";
        range.surroundContents(mark);
        mark.scrollIntoView({ behavior: "smooth", block: "center" });
        break;
      } catch (e) {}
    }
  }
}

document.addEventListener("mouseup", () => {
  setTimeout(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim();

    if (text && text.length > 3) {
      const range = selection!.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      showFloatingMenu(rect.left + rect.width / 2, rect.top);
    } else {
      hideFloatingMenu();
    }
  }, 10);
});

document.addEventListener("mousedown", (e) => {
  const host = document.getElementById("ask-page-ai-float-host");
  if (host && !host.contains(e.target as Node)) {
    hideFloatingMenu();
  }
});

function showToast(text: string, isError = false) {
  const host = document.getElementById("ask-page-ai-float-host");
  const shadow = host?.shadowRoot;
  if (!shadow) return;

  let toast = shadow.getElementById("atp-toast") as HTMLDivElement | null;
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "atp-toast";
    toast.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 2147483647;
      max-width: 360px; padding: 12px 16px; border-radius: 12px;
      font-family: system-ui, sans-serif; font-size: 13px; line-height: 1.4;
      color: #fff; background: linear-gradient(135deg, #1a1d2b, #282d3e);
      border: 1px solid rgba(124, 92, 252, 0.35);
      box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    `;
    shadow.appendChild(toast);
  }

  toast.style.borderColor = isError ? "rgba(244,63,94,0.5)" : "rgba(124, 92, 252, 0.35)";
  toast.textContent = text;
  toast.style.display = "block";
  setTimeout(() => { toast!.style.display = "none"; }, 8000);
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type === "EXTRACT_CONTENT") {
    try {
      sendResponse(extractPageContent());
    } catch {
      sendResponse({ error: "Failed to extract content" });
    }
    return true;
  }
  if (message.type === "HIGHLIGHT_TEXT") {
    highlightTextOnPage(message.payload?.text || "");
    return false;
  }
  return false;
});

createFloatingMenu();
