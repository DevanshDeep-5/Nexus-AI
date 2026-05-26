import React from "react";
import { Sparkles, User } from "lucide-react";
import ReactMarkdown from "react-markdown";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: { text: string; relevance: number }[];
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
  onHighlightSource?: (text: string) => void;
}

export function MessageBubble({ message, onHighlightSource }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-2.5 animate-slide-up ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${isUser ? "bg-surface-700" : ""}`}
        style={!isUser ? { background: "linear-gradient(135deg, #6d4ef0, #7c5cfc)", boxShadow: "0 2px 10px rgba(124,92,252,0.3)" } : {}}
      >
        {isUser ? (
          <User className="w-3 h-3 text-surface-300" />
        ) : (
          <Sparkles className="w-3 h-3 text-white" />
        )}
      </div>

      <div className={isUser ? "nexus-bubble-user" : "nexus-bubble-ai"}>
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none prose-invert prose-p:my-1 prose-ul:my-1 prose-li:my-0.5 prose-headings:my-2 prose-code:text-purple-300 prose-code:bg-purple-500/10 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-p:text-[rgba(255,255,255,0.8)]">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-2.5 border-t border-white/10">
            <p className="text-[9px] font-semibold uppercase tracking-widest mb-1.5" style={{ color: "rgba(255,255,255,0.25)" }}>
              Sources from page
            </p>
            <div className="space-y-1">
              {message.sources.map((source, i) => (
                <button
                  key={i}
                  onClick={() => onHighlightSource?.(source.text)}
                  className="block w-full text-left text-[11px] rounded-lg px-2.5 py-1.5 transition-all duration-200 cursor-pointer line-clamp-2"
                  style={{
                    background: "rgba(124,92,252,0.08)",
                    border: "1px solid rgba(124,92,252,0.15)",
                    color: "#a78bfa",
                  }}
                  title="Click to highlight on page"
                >
                  "{source.text.substring(0, 120)}{source.text.length > 120 ? "…" : ""}"
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
