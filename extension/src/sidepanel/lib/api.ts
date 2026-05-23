import { API_BASE_URL } from "./constants";

interface ApiOptions {
  signal?: AbortSignal;
}

function formatApiError(detail: unknown, fallback: string): string {
  if (typeof detail === "string" && detail.trim()) return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (typeof item === "object" && item && "msg" in item ? String((item as { msg: string }).msg) : String(item)))
      .filter(Boolean);
    if (messages.length) return messages.join("; ");
  }
  return fallback || "API request failed";
}

async function post<T>(endpoint: string, body: Record<string, unknown>, opts?: ApiOptions): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: opts?.signal,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Network error";
    if (message.includes("Failed to fetch") || message.includes("NetworkError")) {
      throw new Error(
        `Cannot reach the backend at ${API_BASE_URL}. Is uvicorn running on port 8000?`
      );
    }
    throw err instanceof Error ? err : new Error(message);
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(formatApiError(err.detail, res.statusText));
  }

  return res.json();
}

export interface SourceExcerpt {
  text: string;
  relevance: number;
}

export interface AskResponse {
  answer: string;
  sources: SourceExcerpt[];
}

export interface SummarizeResponse {
  key_points: string[];
  insights: string[];
  takeaway: string;
}

export interface ELI5Response {
  explanation: string;
}

export interface DebateResponse {
  arguments_for: string[];
  arguments_against: string[];
  verdict: string;
}

export interface NotesSection {
  heading: string;
  bullets: string[];
  key_terms: string[];
}

export interface NotesResponse {
  title: string;
  sections: NotesSection[];
}

export interface CuriosityResponse {
  questions: string[];
}

export interface YouTubeTranscriptResponse {
  transcript: string;
  video_id: string;
}

export interface HighlightActionResponse {
  result: string;
}

export const api = {
  ask(question: string, pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<AskResponse>("/ask", {
      question,
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  summarize(pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<SummarizeResponse>("/summarize", {
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  eli5(pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<ELI5Response>("/eli5", {
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  debate(pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<DebateResponse>("/debate", {
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  notes(pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<NotesResponse>("/notes", {
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  curiosity(pageContent: string, pageUrl: string, opts?: ApiOptions) {
    return post<CuriosityResponse>("/curiosity", {
      page_content: pageContent,
      page_url: pageUrl,
    }, opts);
  },

  youtubeTranscript(videoId: string, opts?: ApiOptions) {
    return post<YouTubeTranscriptResponse>("/youtube/transcript", {
      video_id: videoId,
    }, opts);
  },

  highlightAction(selectedText: string, action: string, pageContext: string, opts?: ApiOptions) {
    return post<HighlightActionResponse>("/highlight-action", {
      selected_text: selectedText,
      action,
      page_context: pageContext,
    }, opts);
  },
};
