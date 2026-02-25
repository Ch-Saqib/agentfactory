/**
 * ShortsSearch - Search bar for finding shorts by keyword
 *
 * Features:
 * - Real-time search with debouncing
 * - Clear search button
 * - Search suggestions (optional)
 * - Keyboard shortcut support (Ctrl+K / Cmd+K)
 */

import React, { useState, useCallback, useRef, useEffect } from "react";

interface ShortsSearchProps {
  /** Current search query */
  searchQuery: string;
  /** Callback when search changes */
  onSearchChange: (query: string) => void;
  /** Placeholder text */
  placeholder?: string;
}

export function ShortsSearch({
  searchQuery,
  onSearchChange,
  placeholder = "Search shorts...",
}: ShortsSearchProps) {
  const [inputValue, setInputValue] = useState(searchQuery);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  const debouncedSearch = useCallback(
    (() => {
      let timeout: NodeJS.Timeout;
      return (query: string) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          onSearchChange(query);
        }, 300);
      };
    })(),
    [onSearchChange]
  );

  // Handle input change
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setInputValue(value);
      debouncedSearch(value);
    },
    [debouncedSearch]
  );

  // Handle clear search
  const handleClear = useCallback(() => {
    setInputValue("");
    onSearchChange("");
    inputRef.current?.focus();
  }, [onSearchChange]);

  // Handle keyboard shortcut (Ctrl+K / Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const hasValue = inputValue.trim().length > 0;

  return (
    <div
      className={`relative flex items-center rounded-full border transition-all ${
        isFocused
          ? "border-blue-500 bg-gray-800"
          : "border-gray-700 bg-gray-900"
      }`}
    >
      {/* Search Icon */}
      <span className="pl-4 text-gray-400">🔍</span>

    {/* Input Field */}
    <input
      ref={inputRef}
      type="text"
      value={inputValue}
      onChange={handleChange}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      placeholder={placeholder}
      className="flex-1 bg-transparent py-2 pr-10 text-sm text-white placeholder-gray-500 focus:outline-none"
    />

    {/* Clear Button */}
    {hasValue && (
      <button
        onClick={handleClear}
        className="mr-3 rounded-full p-1 text-gray-400 hover:text-white transition-colors"
      >
        ✕
      </button>
    )}

    {/* Keyboard Shortcut Hint */}
    {!hasValue && !isFocused && (
      <span className="absolute right-3 hidden text-xs text-gray-500 sm:block">
        Ctrl+K
      </span>
    )}
  </div>
  );
}


/**
 * RecommendedShorts - Personalized recommendations section
 *
 * Features:
 * - "For You" section based on viewing history
 * - "Continue Learning" section based on progress
 * - "Trending" section - most viewed in 7 days
 */

import { useShortsFeed } from "./hooks/useShortsFeed";

interface RecommendedShortsProps {
  /** User's current lesson progress (for recommendations) */
  currentLessonPath?: string;
  /** Recently viewed lessons */
  recentlyViewed?: string[];
  /** Callback when video is clicked */
  onVideoClick?: (videoId: string) => void;
}

interface RecommendationSectionProps {
  title: string;
  videoIds: string[];
  onVideoClick: (videoId: string) => void;
}

function RecommendationSection({
  title,
  videoIds,
  onVideoClick,
}: RecommendationSectionProps) {
  const { shorts, loading } = useShortsFeed({
    // TODO: Implement recommendation API endpoint
    sort: "relevant",
  });

  // Filter to only show recommended videos
  const recommendedShorts = shorts.filter((s) =>
    videoIds.includes(s.id)
  );

  if (recommendedShorts.length === 0 && !loading) {
    return null;
  }

  return (
    <section className="mb-6">
      <h3 className="mb-3 text-lg font-semibold text-white">{title}</h3>

      {loading ? (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-32 w-24 shrink-0 animate-pulse rounded-lg bg-gray-800"
            />
          ))}
        </div>
      ) : (
        <div className="flex gap-3 overflow-x-auto pb-2">
          {recommendedShorts.map((short) => (
            <button
              key={short.id}
              onClick={() => onVideoClick(short.id)}
              className="group relative h-32 w-24 shrink-0 overflow-hidden rounded-lg transition-transform active:scale-105"
            >
              {/* Thumbnail */}
              <img
                src={short.thumbnailUrl}
                alt={short.title}
                className="h-full w-full object-cover"
              />

              {/* Overlay on hover */}
              <div className="absolute inset-0 bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
                <div className="flex h-full items-center justify-center">
                  <span className="text-xs text-white">▶️</span>
                </div>
              </div>

              {/* Title Tooltip */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <p className="truncate text-xs text-white">{short.title}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

export function RecommendedShorts({
  currentLessonPath,
  recentlyViewed = [],
  onVideoClick,
}: RecommendedShortsProps) {
  // Mock recommendation logic (would use API in production)
  const forYouVideoIds = recentlyViewed.slice(0, 5); // Based on history

  // Continue learning - suggest next lessons in current part
  // TODO: Implement logic to get next lessons based on currentLessonPath
  const continueLearningVideoIds: string[] = [];

  // Trending - most viewed in 7 days
  // TODO: Implement API call to get trending videos
  const trendingVideoIds: string[] = [];

  return (
    <div className="space-y-4">
      {/* "For You" Section */}
      {forYouVideoIds.length > 0 && (
        <RecommendationSection
          title="For You"
          videoIds={forYouVideoIds}
          onVideoClick={onVideoClick || (() => {})}
        />
      )}

      {/* "Continue Learning" Section */}
      {continueLearningVideoIds.length > 0 && (
        <RecommendationSection
          title="Continue Learning"
          videoIds={continueLearningVideoIds}
          onVideoClick={onVideoClick || (() => {})}
        />
      )}

      {/* "Trending" Section */}
      {trendingVideoIds.length > 0 && (
        <RecommendationSection
          title="Trending This Week"
          videoIds={trendingVideoIds}
          onVideoClick={onVideoClick || (() => {})}
        />
      )}
    </div>
  );
}
