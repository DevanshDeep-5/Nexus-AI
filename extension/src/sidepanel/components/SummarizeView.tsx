/**
 * SummarizeView Component
 * -------------------------
 * Displays a structured TL;DR summary of the current page.
 *
 * Data flow:
 *   1. On mount, sends the page content to POST /summarize
 *   2. Shows skeleton loaders while waiting for the response
 *   3. Renders the result as three cards: Key Points, Insights, Takeaway
 *
 * The outer container uses h-full + overflow-y-auto so the content
 * scrolls independently when it exceeds the panel height.
 */

import React, { useState, useEffect, useRef } from "react";
import { Zap, CheckCircle2, Lightbulb, Target } from "lucide-react";
import { SkeletonCard } from "./SkeletonLoader";
import { useAPI } from "../hooks/useAPI";
import type { SummarizeResponse } from "../lib/api";

interface SummarizeViewProps {
  /** The extracted text content of the current page */
  pageContent: string;
  /** The URL of the current page */
  pageUrl: string;
}

export function SummarizeView({ pageContent, pageUrl }: SummarizeViewProps) {
  const [data, setData] = useState<SummarizeResponse | null>(null);
  const { loading, error, summarize } = useAPI();
  const hasFetched = useRef(false);

  // Fetch summary once when the component mounts (and content is available)
  useEffect(() => {
    if (pageContent && !hasFetched.current) {
      hasFetched.current = true;
      summarize(pageContent, pageUrl).then((res) => {
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

  // ── Rendered Summary ──────────────────────────────────────────
  return (
    <div className="h-full overflow-y-auto">
      <div className="p-4 space-y-4 animate-fade-in">

        {/* Key Points Card */}
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-7 h-7 rounded-lg bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center">
              <Zap className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-sm font-semibold text-surface-800 dark:text-surface-100">Key Points</h3>
            <span className="badge-primary">{data.key_points.length}</span>
          </div>
          <ul className="space-y-2">
            {data.key_points.map((point, i) => (
              <li key={i} className="flex gap-2.5 text-xs text-surface-700 dark:text-surface-300 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Insights Card — only shown if there are insights */}
        {data.insights.length > 0 && (
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-900/40 flex items-center justify-center">
                <Lightbulb className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              </div>
              <h3 className="text-sm font-semibold text-surface-800 dark:text-surface-100">Insights</h3>
            </div>
            <ul className="space-y-2">
              {data.insights.map((insight, i) => (
                <li key={i} className="flex gap-2.5 text-xs text-surface-700 dark:text-surface-300 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                  <span className="text-amber-500 flex-shrink-0">💡</span>
                  <span>{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Takeaway Card — highlighted with a left border accent */}
        {data.takeaway && (
          <div className="glass-card p-4 border-l-4 border-l-primary-500">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-primary-500" />
              <h3 className="text-sm font-semibold text-surface-800 dark:text-surface-100">Final Takeaway</h3>
            </div>
            <p className="text-xs text-surface-700 dark:text-surface-300 leading-relaxed">{data.takeaway}</p>
          </div>
        )}

      </div>
    </div>
  );
}
