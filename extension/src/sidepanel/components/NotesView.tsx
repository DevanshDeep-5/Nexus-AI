/**
 * NotesView Component
 * ---------------------
 * Displays AI-generated structured study notes for the current page.
 *
 * Data flow:
 *   1. On mount, sends the page content to POST /notes
 *   2. Shows skeleton loaders while waiting
 *   3. Renders titled sections with bullet points and key terms
 *
 * The outer container uses h-full + overflow-y-auto so the content
 * scrolls independently when it exceeds the panel height.
 */

import React, { useState, useEffect, useRef } from "react";
import { FileText, BookOpen, Tag } from "lucide-react";
import { SkeletonCard } from "./SkeletonLoader";
import { useAPI } from "../hooks/useAPI";
import type { NotesResponse } from "../lib/api";

interface NotesViewProps {
  /** The extracted text content of the current page */
  pageContent: string;
  /** The URL of the current page */
  pageUrl: string;
}

export function NotesView({ pageContent, pageUrl }: NotesViewProps) {
  const [data, setData] = useState<NotesResponse | null>(null);
  const { loading, error, notes } = useAPI();
  const hasFetched = useRef(false);

  // Fetch notes once when the component mounts (and content is available)
  useEffect(() => {
    if (pageContent && !hasFetched.current) {
      hasFetched.current = true;
      notes(pageContent, pageUrl).then((res) => {
        if (res) setData(res);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageContent]);

  // ── Loading State ──────────────────────────────────────────────
  if (loading) {
    return (
      <div className="p-4 space-y-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  // ── Error State ────────────────────────────────────────────────
  if (error) {
    return (
      <div className="p-4">
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800 text-sm text-rose-600 dark:text-rose-400">
          {error}
        </div>
      </div>
    );
  }

  if (!data) return null;

  // ── Rendered Notes ────────────────────────────────────────────
  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4 space-y-4 animate-fade-in">

        {/* Notes header — title with section count */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-surface-800 dark:text-surface-100">{data.title}</h2>
            <p className="text-[10px] text-surface-400">{data.sections.length} sections</p>
          </div>
        </div>

        {/* Section cards — each has a heading, bullet list, and key terms */}
        {data.sections.map((section, i) => (
          <div key={i} className="glass-card p-4 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
            {/* Section heading */}
            <div className="flex items-center gap-2 mb-3">
              <FileText className="w-4 h-4 text-primary-500" />
              <h3 className="text-sm font-semibold text-surface-800 dark:text-surface-100">
                {section.heading}
              </h3>
            </div>

            {/* Bullet points */}
            <ul className="space-y-1.5 mb-3">
              {section.bullets.map((bullet, j) => (
                <li key={j} className="flex gap-2 text-xs text-surface-600 dark:text-surface-300">
                  <span className="text-primary-400 mt-0.5 flex-shrink-0">•</span>
                  <span>{bullet}</span>
                </li>
              ))}
            </ul>

            {/* Key terms — shown as badge pills below the bullets */}
            {section.key_terms.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-2 border-t border-surface-200/50 dark:border-surface-700/30">
                <Tag className="w-3 h-3 text-surface-400 mt-0.5" />
                {section.key_terms.map((term, j) => (
                  <span key={j} className="badge-primary text-[10px]">
                    {term}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

      </div>
    </div>
  );
}
