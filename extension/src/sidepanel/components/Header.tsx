/**
 * Header Component
 * ------------------
 * The top bar of the side panel showing the "Nexus AI" brand logo
 * and a theme toggle button (sun/moon icon).
 */

import React from "react";
import { Sun, Moon } from "lucide-react";

interface HeaderProps {
  /** Whether dark mode is currently active */
  isDark: boolean;
  /** Callback to toggle between dark and light mode */
  onToggleTheme: () => void;
  /** Callback to refresh page content (unused in header, kept for API consistency) */
  onRefresh: () => void;
  /** The current page's title (unused in header, kept for API consistency) */
  pageTitle: string;
}

export function Header({ isDark, onToggleTheme }: HeaderProps) {
  return (
    <header className="nexus-header">
      {/* Brand logo */}
      <div className="nexus-header-title">
        <span className="nexus-logo-text">Nexus AI</span>
      </div>

      {/* Theme toggle — shows Sun icon in dark mode, Moon icon in light mode */}
      <button
        onClick={onToggleTheme}
        className="nexus-icon-btn"
        title={isDark ? "Switch to light mode" : "Switch to dark mode"}
      >
        {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>
    </header>
  );
}
