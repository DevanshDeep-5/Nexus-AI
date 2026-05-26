import { useState, useEffect, useCallback } from "react";

interface PageData {
  content: string;
  url: string;
  title: string;
  isYouTube: boolean;
  videoId?: string;
}

const defaultPageData: PageData = {
  content: "",
  url: "",
  title: "",
  isYouTube: false,
};

export function usePageContent() {
  const [pageData, setPageData] = useState<PageData>(defaultPageData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const extractContent = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await chrome.runtime.sendMessage({ type: "GET_PAGE_CONTENT" });

      if (response?.error) {
        setError(response.error);
      } else if (response) {
        setPageData({
          content: response.content || "",
          url: response.url || "",
          title: response.title || "",
          isYouTube: response.isYouTube || false,
          videoId: response.videoId,
        });
      }
    } catch {
      setError("Could not extract page content. Make sure you're on a webpage.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    extractContent();
  }, [extractContent]);

  return { pageData, loading, error, refresh: extractContent };
}
