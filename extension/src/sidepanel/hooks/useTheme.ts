/**
 * useTheme Hook
 * ---------------
 * Manages dark/light theme state with persistence via chrome.storage.
 *
 * Features:
 *   - Loads the saved theme preference on mount (defaults to dark)
 *   - Toggles the "dark" CSS class on <html> to switch themes
 *   - Persists the user's preference so it survives panel reopens
 *
 * Usage:
 *   const { isDark, toggleTheme } = useTheme();
 */

import { useState, useEffect, useCallback } from "react";

export function useTheme() {
  const [isDark, setIsDark] = useState(true);

  // Load the saved theme preference when the hook first mounts
  useEffect(() => {
    chrome.storage?.local?.get(["theme"]).then((result) => {
      const saved = result.theme ?? "dark"; // Default to dark if no saved preference
      setIsDark(saved === "dark");
      document.documentElement.classList.toggle("dark", saved === "dark");
    }).catch(() => {
      // chrome.storage might not be available in dev/test environments
      setIsDark(true);
      document.documentElement.classList.add("dark");
    });
  }, []);

  /** Toggle between dark and light mode, and persist the choice */
  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      const next = !prev;

      // Toggle the CSS class that controls all theme-aware styles
      document.documentElement.classList.toggle("dark", next);

      // Persist to chrome.storage so the preference survives panel reopens
      chrome.storage?.local?.set({ theme: next ? "dark" : "light" }).catch(() => {});

      return next;
    });
  }, []);

  return { isDark, toggleTheme };
}
