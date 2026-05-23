/**
 * Skeleton Loader Components
 * ----------------------------
 * Animated placeholder components shown while data is loading.
 * These provide visual feedback so the UI doesn't feel "frozen"
 * during API calls.
 *
 * Three variants:
 *   - SkeletonLoader: Generic lines (for general content)
 *   - SkeletonCard:   Card with title + body lines (for Summary/Notes/etc.)
 *   - SkeletonBubble: Chat bubble shape (for the Chat tab's AI response)
 */

import React from "react";

/**
 * Generic skeleton with animated shimmer lines.
 * Lines get progressively shorter to mimic a paragraph shape.
 *
 * @param lines - Number of skeleton lines to render (default: 4)
 */
export function SkeletonLoader({ lines = 4 }: { lines?: number }) {
  return (
    <div className="space-y-3 animate-fade-in p-4">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div
            className="skeleton h-4"
            style={{ width: `${85 - i * 10}%`, animationDelay: `${i * 0.15}s` }}
          />
        </div>
      ))}
      <div className="skeleton h-4 w-3/5" style={{ animationDelay: `${lines * 0.15}s` }} />
    </div>
  );
}

/** Card-shaped skeleton — mimics a glass-card with a title and body lines */
export function SkeletonCard() {
  return (
    <div className="glass-card p-4 space-y-3 animate-fade-in">
      <div className="skeleton h-5 w-2/5" />
      <div className="skeleton h-3 w-full" />
      <div className="skeleton h-3 w-4/5" />
      <div className="skeleton h-3 w-3/5" />
    </div>
  );
}

/** Chat bubble skeleton — mimics an AI response with avatar and text lines */
export function SkeletonBubble() {
  return (
    <div className="flex gap-2 animate-fade-in">
      {/* Avatar placeholder */}
      <div className="skeleton w-7 h-7 rounded-full flex-shrink-0" />
      {/* Text lines placeholder */}
      <div className="space-y-2 flex-1 max-w-[80%]">
        <div className="skeleton h-4 w-full" />
        <div className="skeleton h-4 w-4/5" />
        <div className="skeleton h-4 w-3/5" />
      </div>
    </div>
  );
}
