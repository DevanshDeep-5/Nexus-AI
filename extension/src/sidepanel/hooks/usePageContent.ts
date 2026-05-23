/**
 * usePageContent Hook
 * --------------------
 * Extracts the current tab's webpage content via Chrome's messaging API.
 *
 * Flow:
 *   1. Sends a "GET_PAGE_CONTENT" message to the background service worker
 *   2. The service worker forwards it to the content script on the active tab
 *   3. The content script extracts the page's text, title, URL, and YouTube info
 *   4. The response is stored in state and made available to components
 *
 * Also provides a `refresh` function to re-extract content (useful when
 * the user navigates to a new page while the side panel is still open).
 */

import { useState, useEffect, useCallback } from "react";

/** Shape of the extracted page data */
interface PageData {
  /** The full text content extracted from the page's DOM */
  content: string;
  /** The page's URL */
  url: string;
  /** The page's <title> tag */
  title: string;
  /** Whether this is a YouTube watch page */
  isYouTube: boolean;
  /** The YouTube video ID (only present if isYouTube is true) */
  videoId?: string;
}

export function usePageContent() {
  // Initialize with empty values — will be populated after extraction
  const [pageData, setPageData] = useState<PageData>({
    content: "",
    url: "",
    title: "",
    isYouTube: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Extract content from the active tab by messaging the background
   * service worker, which relays the request to the content script.
   */
  const extractContent = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Send message to the background service worker
      const response = await chrome.runtime.sendMessage({ type: "GET_PAGE_CONTENT" });

      if (response?.error) {
        // Content script reported an error (e.g., restricted page)
        setError(response.error);
      } else if (response) {
        // Successfully extracted — update state with the page data
        setPageData({
          content: response.content || "",
          url: response.url || "",
          title: response.title || "",
          isYouTube: response.isYouTube || false,
          videoId: response.videoId,
        });
      }
    } catch (err) {
      // This usually means the content script isn't injected (e.g., chrome:// pages)
      setError("Could not extract page content. Make sure you're on a webpage.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Extract content automatically when the hook first mounts
  useEffect(() => {
    extractContent();
  }, [extractContent]);

  return { pageData, loading, error, refresh: extractContent };
}
