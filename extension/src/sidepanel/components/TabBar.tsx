/**
 * TabBar Component
 * ------------------
 * Horizontal navigation bar with equally-spaced tab buttons.
 * Each tab shows an icon and label, and highlights when active.
 *
 * The icon mapping translates icon names from constants.ts to
 * actual Lucide React icon components.
 */

import React from "react";
import { MessageSquare, AlignLeft, FileText } from "lucide-react";
import type { TabId } from "../lib/constants";
import { TABS } from "../lib/constants";

/**
 * Maps icon name strings (from TABS constant) to Lucide React components.
 * This decouples the tab definition from the icon import, so tabs can be
 * configured in constants.ts without importing React components there.
 */
const iconMap: Record<string, React.FC<{ className?: string }>> = {
  MessageSquare,       // Chat tab icon
  Zap: AlignLeft,      // Summarize tab icon (AlignLeft used for the layout metaphor)
  FileText,            // Notes tab icon
};

interface TabBarProps {
  /** The currently active tab ID */
  activeTab: TabId;
  /** Callback fired when the user clicks a tab */
  onTabChange: (tab: TabId) => void;
}

export function TabBar({ activeTab, onTabChange }: TabBarProps) {
  return (
    <nav className="nexus-tabbar-equal">
      {TABS.map((tab) => {
        const Icon = iconMap[tab.icon];
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`nexus-tab-equal ${isActive ? "nexus-tab-active" : "nexus-tab-inactive"}`}
          >
            {Icon && <Icon className="w-3.5 h-3.5" />}
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}
