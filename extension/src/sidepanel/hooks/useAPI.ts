/**
 * useAPI Hook
 * ------------
 * Wraps backend API calls with per-request loading/error state and
 * cancellation support.
 *
 * Each view (SummarizeView, NotesView, ChatView) creates its own useAPI()
 * instance, so they never share loading/error state or abort controllers.
 * This ensures that one view completing never interferes with another.
 */

import { useState, useCallback, useRef } from "react";
import { api } from "../lib/api";
import type {
  AskResponse,
  SummarizeResponse,
  ELI5Response,
  DebateResponse,
  NotesResponse,
} from "../lib/api";

type RequestKey = "ask" | "summarize" | "eli5" | "debate" | "notes";

export function useAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRefs = useRef<Partial<Record<RequestKey, AbortController>>>({});

  const cancel = useCallback((key?: RequestKey) => {
    if (key) {
      abortRefs.current[key]?.abort();
      delete abortRefs.current[key];
    } else {
      Object.values(abortRefs.current).forEach((controller) => controller?.abort());
      abortRefs.current = {};
    }
    setLoading(false);
  }, []);

  const execute = useCallback(
    async <T>(key: RequestKey, fn: (signal: AbortSignal) => Promise<T>): Promise<T | null> => {
      // Cancel any existing request for this key
      abortRefs.current[key]?.abort();

      const controller = new AbortController();
      abortRefs.current[key] = controller;

      setLoading(true);
      setError(null);

      try {
        const result = await fn(controller.signal);
        return result;
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") {
          // Request was intentionally cancelled — don't show error
          return null;
        }
        const message = err instanceof Error ? err.message : "Something went wrong";
        setError(message);
        return null;
      } finally {
        setLoading(false);
        if (abortRefs.current[key] === controller) {
          delete abortRefs.current[key];
        }
      }
    },
    []
  );

  const ask = useCallback(
    (question: string, content: string, url: string) =>
      execute<AskResponse>("ask", (signal) => api.ask(question, content, url, { signal })),
    [execute]
  );

  const summarize = useCallback(
    (content: string, url: string) =>
      execute<SummarizeResponse>("summarize", (signal) => api.summarize(content, url, { signal })),
    [execute]
  );

  const eli5 = useCallback(
    (content: string, url: string) =>
      execute<ELI5Response>("eli5", (signal) => api.eli5(content, url, { signal })),
    [execute]
  );

  const debate = useCallback(
    (content: string, url: string) =>
      execute<DebateResponse>("debate", (signal) => api.debate(content, url, { signal })),
    [execute]
  );

  const notes = useCallback(
    (content: string, url: string) =>
      execute<NotesResponse>("notes", (signal) => api.notes(content, url, { signal })),
    [execute]
  );

  return { loading, error, cancel, ask, summarize, eli5, debate, notes };
}
