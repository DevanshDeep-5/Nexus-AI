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
  const controllers = useRef<Partial<Record<RequestKey, AbortController>>>({});

  const cancel = useCallback((key?: RequestKey) => {
    if (key) {
      controllers.current[key]?.abort();
      delete controllers.current[key];
    } else {
      Object.values(controllers.current).forEach((c) => c?.abort());
      controllers.current = {};
    }
    setLoading(false);
  }, []);

  const execute = useCallback(
    async <T>(key: RequestKey, fn: (signal: AbortSignal) => Promise<T>): Promise<T | null> => {
      controllers.current[key]?.abort();

      const controller = new AbortController();
      controllers.current[key] = controller;

      setLoading(true);
      setError(null);

      try {
        return await fn(controller.signal);
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "AbortError") return null;
        const msg = err instanceof Error ? err.message : "Something went wrong";
        setError(msg);
        return null;
      } finally {
        setLoading(false);
        if (controllers.current[key] === controller) {
          delete controllers.current[key];
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
