import React from "react";
import { MessageSquare, AlignLeft, FileText } from "lucide-react";
import type { TabId } from "../lib/constants";
import { TABS } from "../lib/constants";

const iconMap: Record<string, React.FC<{ className?: string }>> = {
  MessageSquare,
  Zap: AlignLeft,
  FileText,
};

interface TabBarProps {
  activeTab: TabId;
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
