/**
 * ShortsFeed - TikTok-style vertical video feed
 *
 * Features:
 * - Vertical scroll-snap (9:16 aspect ratio cards)
 * - Auto-play on scroll to viewport
 * - Pause on scroll away
 * - Muted by default, tap to unmute
 * - Double-tap to like
 * - Swipe up/down navigation
 */

import React, { useRef, useCallback, useEffect, useState } from "react";
import { useShortsFeed } from "./hooks/useShortsFeed";
import { ShortVideoPlayer } from "./ShortVideoPlayer";
import { ShortsControls } from "./ShortsControls";
import type { ShortVideo } from "./types";

interface ShortsFeedProps {
  /** Part filter (01-09) */
  part?: string;
  /** Chapter filter within part */
  chapter?: string;
  /** Search keyword */
  search?: string;
  /** Sort order: recent, popular, relevant */
  sort?: "recent" | "popular" | "relevant";
}

export function ShortsFeed({
  part,
  chapter,
  search,
  sort = "recent",
}: ShortsFeedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [visibleIndex, setVisibleIndex] = useState(0);

  // Fetch shorts feed data
  const { shorts, loading, error, hasMore, loadMore, refresh } = useShortsFeed({
    part,
    chapter,
    search,
    sort,
  });

  // Handle scroll events to detect visible video
  const handleScroll = useCallback(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const scrollTop = container.scrollTop;
    const cardHeight = container.offsetHeight; // 100vh height
    const newIndex = Math.round(scrollTop / cardHeight);

    setVisibleIndex(newIndex);
  }, []);

  // Scroll to specific index
  const scrollToIndex = useCallback(
    (index: number) => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const cardHeight = container.offsetHeight;
      container.scrollTo({
        top: index * cardHeight,
        behavior: "smooth",
      });
      setCurrentIndex(index);
    },
    []
  );

  // Handle swipe/drag gestures
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    // Store initial touch position for swipe detection
    const startY = e.touches[0].clientY;
    (e.target as HTMLElement).dataset.touchStartY = startY.toString();
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    // Optional: Add visual feedback during swipe
  }, []);

  const handleTouchEnd = useCallback(
    (e: React.TouchEvent) => {
      const endY = e.changedTouches[0].clientY;
      const startY = parseFloat((e.target as HTMLElement).dataset.touchStartY || "0");
      const diff = startY - endY;

      // Swipe threshold (must swipe at least 50px)
      if (Math.abs(diff) > 50) {
        const newIndex = diff > 0 ? currentIndex + 1 : currentIndex - 1;
        const clampedIndex = Math.max(0, Math.min(newIndex, shorts.length - 1));
        scrollToIndex(clampedIndex);
      }
    },
    [currentIndex, shorts.length, scrollToIndex]
  );

  // Keyboard navigation (arrow keys)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowUp" && currentIndex > 0) {
        scrollToIndex(currentIndex - 1);
      } else if (e.key === "ArrowDown" && currentIndex < shorts.length - 1) {
        scrollToIndex(currentIndex + 1);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex, shorts.length, scrollToIndex]);

  // Auto-load more when near end
  useEffect(() => {
    if (currentIndex >= shorts.length - 3 && hasMore && !loading) {
      loadMore();
    }
  }, [currentIndex, shorts.length, hasMore, loading, loadMore]);

  // Track scroll position
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, [handleScroll]);

  // Handle video actions
  const handleLike = useCallback((videoId: string) => {
    // TODO: Implement like action
    console.log("Liked:", videoId);
  }, []);

  const handleComment = useCallback((videoId: string) => {
    // TODO: Open comment panel
    console.log("Comment:", videoId);
  }, []);

  const handleShare = useCallback((videoId: string) => {
    // TODO: Implement share action
    if (navigator.share) {
      navigator.share({
        title: "Check out this short!",
        url: window.location.href,
      });
    }
  }, []);

  const handleVideoClick = useCallback(() => {
    // Navigate to full lesson
    // TODO: Implement navigation to lesson
    console.log("Navigate to lesson");
  }, []);

  // Loading state
  if (loading && shorts.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-white border-t-transparent" />
          <p className="text-white">Loading shorts...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && shorts.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <p className="text-xl font-semibold">Failed to load shorts</p>
          <button
            onClick={refresh}
            className="mt-4 rounded bg-blue-500 px-4 py-2 hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (shorts.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-900">
        <div className="text-center text-white">
          <p className="text-xl font-semibold">No shorts available</p>
          <p className="mt-2 text-gray-400">Check back later for new content!</p>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="h-screen w-full overflow-y-auto overflow-x-hidden snap-y snap-mandatory bg-black"
      style={{
        scrollSnapType: "y mandatory",
        scrollbarWidth: "none", // Firefox
      }}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Hide scrollbar for Chrome/Safari */}
      <style>{`
        div::-webkit-scrollbar {
          display: none;
        }
      `}</style>

      {shorts.map((short, index) => (
        <div
          key={short.id}
          className="relative h-screen w-full snap-start snap-always"
          style={{ scrollSnapAlign: "start" }}
        >
          {/* Video Player */}
          <ShortVideoPlayer
            short={short}
            isActive={index === visibleIndex}
            onVideoClick={handleVideoClick}
          />

          {/* Video Controls */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            {/* Video Info */}
            <div className="mb-4 text-white">
              <h3 className="text-lg font-semibold">{short.title}</h3>
              <p className="text-sm text-gray-300">{short.lessonPath}</p>
              <p className="mt-1 text-xs text-gray-400">
                {short.durationSeconds}s · {short.viewCount || 0} views
              </p>
            </div>

            {/* Action Buttons */}
            <ShortsControls
              short={short}
              onLike={() => handleLike(short.id)}
              onComment={() => handleComment(short.id)}
              onShare={() => handleShare(short.id)}
            />
          </div>

          {/* Progress Indicator */}
          <div className="absolute right-2 top-1/2 flex -translate-y-1/2 flex-col gap-2">
            {shorts.slice(
              Math.max(0, index - 1),
              Math.min(shorts.length, index + 2)
            ).map((_, i) => {
              const actualIndex = Math.max(0, index - 1) + i;
              return (
                <div
                  key={actualIndex}
                  className={`h-2 w-2 rounded-full transition-all ${
                    actualIndex === visibleIndex
                      ? "bg-white scale-125"
                      : "bg-white/30"
                  }`}
                />
              );
            })}
          </div>
        </div>
      ))}

      {/* Loading More Indicator */}
      {hasMore && (
        <div className="flex h-screen items-center justify-center bg-gray-900">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-white border-t-transparent" />
        </div>
      )}
    </div>
  );
}
