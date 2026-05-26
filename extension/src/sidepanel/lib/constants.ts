// The base URL for all API calls - change this if your backend runs on a different port
export const API_BASE_URL = "http://localhost:8000";

export const TABS = [
  { id: "chat", label: "Chat", icon: "MessageSquare" },
  { id: "summarize", label: "Summarize", icon: "Zap" },
  { id: "notes", label: "Notes", icon: "FileText" },
] as const;

export type TabId = (typeof TABS)[number]["id"];

export const MAX_INPUT_LENGTH = 1000;
