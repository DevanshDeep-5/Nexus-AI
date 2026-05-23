/**
 * SidePanel — Main Layout Component
 * ------------------------------------
 * The root component for the Chrome extension's side panel.
 * Manages the overall layout: header, page info bar, tab navigation,
 * and the active tab's content view.
 *
 * State management:
 *   - activeTab: which tab (Chat/Summarize/Notes) is currently shown
 *   - isDark:    dark/light theme (managed by the useTheme hook)
 *   - pageData:  the extracted content from the current webpage
 */

import React, { useState, useCallback } from "react";
import { Header } from "./components/Header";
import { TabBar } from "./components/TabBar";
import { ChatView } from "./components/ChatView";
import { SummarizeView } from "./components/SummarizeView";
import { NotesView } from "./components/NotesView";
import { usePageContent } from "./hooks/usePageContent";
import { useTheme } from "./hooks/useTheme";
import type { TabId } from "./lib/constants";
import { RefreshCw, Globe, AlertTriangle } from "lucide-react";

export function SidePanel() {
  const [activeTab, setActiveTab] = useState<TabId>("chat");
  const { isDark, toggleTheme } = useTheme();
  const { pageData, loading: pageLoading, error: pageError, refresh } = usePageContent();

  /** Send a message to the content script to highlight source text on the page */
  const handleHighlightSource = useCallback((text: string) => {
    chrome.runtime?.sendMessage({
      type: "HIGHLIGHT_SOURCE",
      payload: { text },
    }).catch(() => { });
  }, []);

  // ── Loading State ──────────────────────────────────────────────────
  // Shown while the content script is extracting text from the page

  if (pageLoading) {
    return (
      <div className="nexus-root">
        <Header isDark={isDark} onToggleTheme={toggleTheme} onRefresh={refresh} pageTitle="" />
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <RefreshCw className="w-5 h-5 text-primary-500 animate-spin" />
            <p className="text-xs text-surface-400">Loading page content…</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Error / Empty State ────────────────────────────────────────────
  // Shown when content extraction fails or returns empty content

  if (pageError || !pageData.content) {
    return (
      <div className="nexus-root">
        <Header isDark={isDark} onToggleTheme={toggleTheme} onRefresh={refresh} pageTitle="" />
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center animate-fade-in">
            {pageError ? (
              <>
                <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-amber-500/10 flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-amber-500" />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">Could not extract page</h3>
                <p className="text-xs text-surface-500 mb-4 max-w-[200px]">{pageError}</p>
              </>
            ) : (
              <>
                <div className="w-12 h-12 mx-auto mb-4 rounded-2xl bg-surface-800 flex items-center justify-center">
                  <Globe className="w-6 h-6 text-surface-500" />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">Navigate to a webpage</h3>
                <p className="text-xs text-surface-500 max-w-[200px]">
                  Open a webpage and click refresh to start asking questions about it.
                </p>
              </>
            )}
            <button onClick={refresh} className="nexus-refresh-btn mt-4">
              Refresh
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ── Main Content ──────────────────────────────────────────────────

  return (
    <div className="nexus-root">
      <Header
        isDark={isDark}
        onToggleTheme={toggleTheme}
        onRefresh={refresh}
        pageTitle={pageData.title}
      />

      <div className="nexus-page-bar">
        <div className="nexus-page-bar-inner">
          <span className="nexus-page-label">CURRENT PAGE</span>
          <button onClick={refresh} className="nexus-icon-btn" title="Refresh">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
        <p className="nexus-page-title" title={pageData.title}>{pageData.title}</p>
      </div>

      <TabBar activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 overflow-hidden">
        {activeTab === "chat" && (
          <ChatView
            pageContent={pageData.content}
            pageUrl={pageData.url}
            onHighlightSource={handleHighlightSource}
          />
        )}
        {activeTab === "summarize" && (
          <SummarizeView pageContent={pageData.content} pageUrl={pageData.url} />
        )}
        {activeTab === "notes" && (
          <NotesView pageContent={pageData.content} pageUrl={pageData.url} />
        )}
      </div>

      {pageData.isYouTube && (
        <div className="px-4 py-2 bg-rose-500/10 border-t border-rose-500/20">
          <p className="text-[10px] text-rose-400 font-medium text-center">
            📺 YouTube video detected — transcript extracted
          </p>
        </div>
      )}
    </div>
  );
}
