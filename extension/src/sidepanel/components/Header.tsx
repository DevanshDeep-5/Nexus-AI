import React from "react";
import { Sun, Moon } from "lucide-react";

interface HeaderProps {
  isDark: boolean;
  onToggleTheme: () => void;
  onRefresh: () => void;
  pageTitle: string;
}

export function Header({ isDark, onToggleTheme }: HeaderProps) {
  return (
    <header className="nexus-header">
      <div className="nexus-header-title">
        <span className="nexus-logo-text">Nexus AI</span>
      </div>
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
