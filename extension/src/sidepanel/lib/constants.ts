/**
 * Application Constants
 * ----------------------
 * Centralized configuration values used across the frontend.
 * Changing these values affects the entire app in one place.
 */

/** Base URL for all backend API calls */
export const API_BASE_URL = "http://localhost:8000";

/**
 * Tab definitions for the bottom navigation bar.
 * Each tab has:
 *   - id:    unique identifier used for routing/state
 *   - label: display text shown in the tab button
 *   - icon:  name of the Lucide React icon component to render
 */
export const TABS = [
  { id: "chat", label: "Chat", icon: "MessageSquare" },
  { id: "summarize", label: "Summarize", icon: "Zap" },
  { id: "notes", label: "Notes", icon: "FileText" },
] as const;

/** TypeScript union type derived from the TABS array — ensures type safety */
export type TabId = (typeof TABS)[number]["id"];

/** Maximum characters allowed in the chat input field */
export const MAX_INPUT_LENGTH = 1000;
