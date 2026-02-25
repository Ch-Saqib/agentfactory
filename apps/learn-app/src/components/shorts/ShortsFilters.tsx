/**
 * Shorts Filters - Minimal, themed filter chips
 */

import React, { useState, useCallback } from "react";
import { X, Filter } from "lucide-react";
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

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Filter Toggle */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className={`flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-all ${
          showFilters || activeFilterCount > 0
            ? "bg-primary text-primary-foreground"
            : "bg-muted hover:bg-primary/20"
        }`}
      >
        <Filter className="w-4 h-4" />
        <span>Filters</span>
        {activeFilterCount > 0 && (
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-background text-xs">
            {activeFilterCount}
          </span>
        )}
      </button>

      {/* Expanded Filters */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-2">
          {/* Part Chips */}
          {availableParts.map((part) => (
            <button
              key={part}
              onClick={() => handlePartChange(filters.part === part ? "" : part)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                filters.part === part
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-primary/20"
              }`}
            >
              {PART_NAMES[part] || part}
            </button>
          ))}

          {/* Sort */}
          <div className="relative">
            <select
              value={filters.sort || "recent"}
              onChange={(e) =>
                handleSortChange(
                  e.target.value as "recent" | "popular" | "relevant"
                )
              }
              className="appearance-none rounded-full border bg-muted px-3 py-1.5 pr-6 text-xs hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-primary"
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Clear */}
          {activeFilterCount > 0 && (
            <button
              onClick={handleClearFilters}
              className="p-1.5 rounded-full hover:bg-muted text-muted-foreground transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
