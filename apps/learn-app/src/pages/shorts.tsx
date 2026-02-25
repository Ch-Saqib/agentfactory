/**
 * Shorts Feed Page - TikTok-style short video feed
 *
 * Route: /shorts
 *
 * Features:
 * - Vertical scroll-snap video feed
 * - Auto-play on scroll to viewport
 * - Engagement (like, comment, share)
 * - Search and filters
 * - Keyboard navigation (arrows, space)
 */

import { useState } from "react";
import { ShortsFeed, ShortsFilters, ShortsSearch, RecommendedShorts } from "../components/shorts";
import type { ShortsFilters as ShortsFiltersType } from "../components/shorts/types";
import { useShortsFeed } from "../components/shorts/hooks/useShortsFeed";

export default function ShortsPage() {
  const [filters, setFilters] = useState<ShortsFiltersType>({});
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    setFilters({ ...filters, search: query || undefined });
  };

  const handleFiltersChange = (newFilters: ShortsFiltersType) => {
    setFilters(newFilters);
  };

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header with Search and Filters */}
      <div className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/95 backdrop-blur">
        <div className="flex items-center gap-4 p-4">
          <div className="flex-1">
            <ShortsSearch
              searchQuery={searchQuery}
              onSearchChange={handleSearchChange}
              placeholder="Search shorts..."
            />
          </div>
        </div>
        <ShortsFilters filters={filters} onFiltersChange={handleFiltersChange} />
      </div>

      {/* Recommended Section (when no search/filter active) */}
      {!searchQuery && !filters.part && !filters.chapter && (
        <div className="border-b border-gray-800 bg-gray-900/50 p-4">
          <RecommendedShorts
            onVideoClick={(videoId) => {
              // Scroll to video in feed
              const element = document.querySelector(`[data-video-id="${videoId}"]`);
              element?.scrollIntoView({ behavior: "smooth" });
            }}
          />
        </div>
      )}

      {/* Main Feed */}
      <ShortsFeed
        part={filters.part}
        chapter={filters.chapter}
        search={filters.search}
        sort={filters.sort}
      />

      {/* Loading indicator when fetching more */}
      <div className="py-8 text-center text-gray-500">
        <p>Scroll or use arrow keys for more shorts</p>
      </div>
    </div>
  );
}
