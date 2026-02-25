/**
 * ShortsFilters - Filter bar for shorts feed
 *
 * Features:
 * - Filter by Part (01-09)
 * - Filter by Chapter within Part
 * - Sort options (Recent, Popular, Relevant)
 * - Active filter indicators
 * - Clear all filters
 */

import React, { useState, useCallback } from "react";
import type { ShortsFilters } from "../types";

interface ShortsFiltersProps {
  /** Current filters */
  filters: ShortsFilters;
  /** Callback when filters change */
  onFiltersChange: (filters: ShortsFilters) => void;
  /** Available parts (derived from book structure) */
  availableParts?: string[];
  /** Available chapters (if part is selected) */
  availableChapters?: Record<string, string[]>;
}

const PART_NAMES: Record<string, string> = {
  "01": "Foundations",
  "02": "Applied Workflows",
  "03": "SDD-RI Fundamentals",
  "04": "Coding for Problem Solving",
  "05": "Data Engineering",
  "06": "Production ML",
  "07": "Agent Development",
  "08": "Testing & QA",
  "09": "Operations & Deployment",
};

const SORT_OPTIONS = [
  { value: "recent", label: "Recent" },
  { value: "popular", label: "Popular" },
  { value: "relevant", label: "Relevant" },
];

export function ShortsFilters({
  filters,
  onFiltersChange,
  availableParts = Object.keys(PART_NAMES),
  availableChapters = {},
}: ShortsFiltersProps) {
  const [showFilters, setShowFilters] = useState(false);

  // Count active filters
  const activeFilterCount = [
    filters.part,
    filters.chapter,
    filters.search,
  ].filter(Boolean).length;

  // Clear all filters
  const handleClearFilters = useCallback(() => {
    onFiltersChange({});
  }, [onFiltersChange]);

  // Update part filter
  const handlePartChange = useCallback(
    (part: string) => {
      onFiltersChange({
        ...filters,
        part: part || undefined,
        chapter: undefined, // Reset chapter when part changes
      });
    },
    [filters, onFiltersChange]
  );

  // Update chapter filter
  const handleChapterChange = useCallback(
    (chapter: string) => {
      onFiltersChange({
        ...filters,
        chapter: chapter || undefined,
      });
    },
    [filters, onFiltersChange]
  );

  // Update sort
  const handleSortChange = useCallback(
    (sort: "recent" | "popular" | "relevant") => {
      onFiltersChange({
        ...filters,
        sort,
      });
    },
    [filters, onFiltersChange]
  );

  // Get available chapters for selected part
  const chaptersForPart = filters.part
    ? availableChapters[filters.part] || []
    : [];

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-gray-800 bg-gray-900/50 p-2">
      {/* Filter Toggle Button */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
          showFilters
            ? "bg-blue-500 text-white"
            : "bg-gray-800 text-gray-300 hover:bg-gray-700"
        }`}
      >
        <span>{showFilters ? "Hide" : "Filters"}</span>
        {activeFilterCount > 0 && (
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-xs text-white">
            {activeFilterCount}
          </span>
        )}
      </button>

      {/* Expanded Filters Panel */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-3">
          {/* Part Filter */}
          <div className="relative">
            <select
              value={filters.part || ""}
              onChange={(e) => handlePartChange(e.target.value || undefined)}
              className="appearance-none rounded-full border border-gray-700 bg-gray-800 px-4 py-2 pr-8 text-sm text-white hover:border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Parts</option>
              {availableParts.map((part) => (
                <option key={part} value={part}>
                  {PART_NAMES[part] || part} ({part})
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400">
              ▼
            </div>
          </div>

          {/* Chapter Filter (shown only when part is selected) */}
          {filters.part && chaptersForPart.length > 0 && (
            <div className="relative">
              <select
                value={filters.chapter || ""}
                onChange={(e) =>
                  handleChapterChange(e.target.value || undefined)
                }
                className="appearance-none rounded-full border border-gray-700 bg-gray-800 px-4 py-2 pr-8 text-sm text-white hover:border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">All Chapters</option>
                {chaptersForPart.map((chapter) => (
                  <option key={chapter} value={chapter}>
                    {chapter}
                  </option>
                ))}
              </select>
              <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400">
                ▼
              </div>
            </div>
          )}

          {/* Sort Options */}
          <div className="relative">
            <select
              value={filters.sort || "recent"}
              onChange={(e) =>
                handleSortChange(
                  e.target.value as "recent" | "popular" | "relevant"
                )
              }
              className="appearance-none rounded-full border border-gray-700 bg-gray-800 px-4 py-2 pr-8 text-sm text-white hover:border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400">
              ▼
            </div>
          </div>

          {/* Clear Filters Button */}
          {activeFilterCount > 0 && (
            <button
              onClick={handleClearFilters}
              className="rounded-full border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 hover:bg-gray-700"
            >
              Clear
            </button>
          )}
        </div>
      )}
    </div>
  );
}
