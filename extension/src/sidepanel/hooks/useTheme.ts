import { useState, useEffect, useCallback } from "react";

export function useTheme() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    chrome.storage?.local?.get(["theme"]).then((result) => {
      const saved = result.theme ?? "dark";
      setIsDark(saved === "dark");
      document.documentElement.classList.toggle("dark", saved === "dark");
    }).catch(() => {
      setIsDark(true);
      document.documentElement.classList.add("dark");
    });
  }, []);

  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle("dark", next);
      chrome.storage?.local?.set({ theme: next ? "dark" : "light" }).catch(() => {});
      return next;
    });
  }, []);

  return { isDark, toggleTheme };
}
