/**
 * ChatView Component
 * --------------------
 * The main chat interface where users ask questions about the page.
 *
 * Features:
 *   - Message history with user/AI bubbles
 *   - Auto-scroll to latest message
 *   - Auto-resize textarea input
 *   - Suggestion chips from the curiosity API
 *   - Request cancellation support
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import { Send, StopCircle } from "lucide-react";
import { MessageBubble, type Message } from "./MessageBubble";
import { SkeletonBubble } from "./SkeletonLoader";
import { useAPI } from "../hooks/useAPI";
import { api } from "../lib/api";

interface ChatViewProps {
  /** The extracted text content of the current page */
  pageContent: string;
  /** The URL of the current page */
  pageUrl: string;
  /** Callback to highlight a source excerpt on the page */
  onHighlightSource: (text: string) => void;
}

export function ChatView({ pageContent, pageUrl, onHighlightSource }: ChatViewProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { loading, error, ask, cancel } = useAPI();

  // ── Auto-scroll ──────────────────────────────────────────────────
  // Scroll to the bottom whenever a new message appears or loading starts
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Fetch suggestions separately — must not share abort with /ask (was cancelling chat)
  useEffect(() => {
    if (!pageContent) return;

    let cancelled = false;
    api
      .curiosity(pageContent, pageUrl)
      .then((res) => {
        if (!cancelled && res?.questions?.length) {
          setSuggestions(res.questions.slice(0, 4));
        }
      })
      .catch(() => {
        // Suggestions are optional; ignore failures
      });

    return () => {
      cancelled = true;
    };
  }, [pageContent, pageUrl]);

  /**
   * Submit a question — either from the input field or a suggestion chip.
   * Creates a user message bubble, sends it to the /ask endpoint,
   * and appends the AI's response as a new bubble.
   */
  const handleSubmit = useCallback(
    async (question?: string) => {
      const q = question || input.trim();
      if (!q || loading) return;

      // Add the user's message to the chat
      const userMsg: Message = {
        id: `user-${Date.now()}`,
        role: "user",
        content: q,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setSuggestions([]); // Hide suggestions once the user starts chatting

      const result = await ask(q, pageContent, pageUrl);
      if (result?.answer?.trim()) {
        const aiMsg: Message = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: result.answer,
          sources: result.sources ?? [],
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMsg]);
      }
      // Errors are shown via `error` from useAPI; no extra bubble needed
    },
    [input, loading, ask, pageContent, pageUrl]
  );

  /** Submit on Enter key, allow Shift+Enter for new lines */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-center px-6 animate-fade-in">
            <div className="nexus-hero-icon mb-5">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L13.5 8.5L20 10L13.5 11.5L12 18L10.5 11.5L4 10L10.5 8.5L12 2Z" fill="#7c5cfc" fillOpacity="0.9"/>
                <path d="M18 14L18.75 17.25L22 18L18.75 18.75L18 22L17.25 18.75L14 18L17.25 17.25L18 14Z" fill="#a78bfa" fillOpacity="0.7"/>
                <path d="M6 3L6.5 5.5L9 6L6.5 6.5L6 9L5.5 6.5L3 6L5.5 5.5L6 3Z" fill="#a78bfa" fillOpacity="0.7"/>
              </svg>
            </div>

            <h3 className="nexus-hero-title">Ask anything about this page</h3>
            <p className="nexus-hero-subtitle">
              Answers grounded in page content<br />only — no hallucinations.
            </p>

            {suggestions.length > 0 && (
              <div className="w-full mt-6 space-y-2">
                <p className="nexus-suggestions-label">Suggested questions</p>
                <div className="space-y-1.5">
                  {suggestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => handleSubmit(q)}
                      className="nexus-suggestion-chip"
                    >
                      <span className="nexus-suggestion-arrow">→</span>
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onHighlightSource={onHighlightSource}
          />
        ))}

        {loading && <SkeletonBubble />}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="mx-4 mb-2 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 animate-fade-in">
          {error}
        </div>
      )}

      <div className="nexus-input-area">
        <div className="nexus-input-row">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this page..."
            rows={1}
            className="nexus-textarea"
            style={{ height: "36px" }}
            onInput={(e) => {
              const t = e.currentTarget;
              t.style.height = "36px";
              t.style.height = Math.min(t.scrollHeight, 120) + "px";
            }}
          />

          {loading ? (
            <button onClick={() => cancel("ask")} className="nexus-send-btn nexus-stop-btn">
              <StopCircle className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim()}
              className="nexus-send-btn"
            >
              <Send className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
