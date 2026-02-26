/**
 * Learning Shorts - "Story Stream" Design
 *
 * A unique horizontal card-based learning experience.
 * Unlike TikTok (vertical full-screen) or YouTube (grid list),
 * this design emphasizes the learning journey with:
 * - Horizontal story cards with progress tracking
 * - Hover-to-preview interaction
 * - Learning path visualization
 * - XP rewards and streaks
 * - Part/Chapter context integration
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { getShortsApiClient } from "../lib/shorts-api";
import type { ShortVideo, ShortsFilters as ShortsFiltersType } from "../components/shorts/types";
import { ShortsSearch } from "../components/shorts";
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Heart,
  MessageCircle,
  Share2,
  Clock,
  Eye,
  TrendingUp,
  BookOpen,
  ChevronRight,
  Sparkles,
  Flame,
  Star,
  X,
  RotateCcw,
} from "lucide-react";

export default function ShortsPage() {
  const [shorts, setShorts] = useState<ShortVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeVideo, setActiveVideo] = useState<string | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [muted, setMuted] = useState(true);
  const [currentProgress, setCurrentProgress] = useState<Record<string, number>>({});
  const [likedIds, setLikedIds] = useState<Set<string>>(new Set());
  const [filters, setFilters] = useState<ShortsFiltersType>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"story" | "grid">("story");
  const [watchedCount, setWatchedCount] = useState(0);
  const videoRefs = useRef<Record<string, HTMLVideoElement>>({});

  // Fetch shorts
  const fetchShorts = useCallback(async () => {
    try {
      setLoading(true);
      const client = getShortsApiClient();
      const response = await client.getVideos({
        ...filters,
        search: searchQuery || undefined,
        limit: 20,
      });
      setShorts(response.shorts);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load shorts");
    } finally {
      setLoading(false);
    }
  }, [filters, searchQuery]);

  useEffect(() => {
    fetchShorts();
  }, [fetchShorts]);

  // Video playback handlers
  const handlePlay = useCallback((videoId: string) => {
    // Pause all other videos
    Object.entries(videoRefs.current).forEach(([id, video]) => {
      if (id !== videoId && video && !video.paused) {
        video.pause();
      }
    });
    setPlayingId(videoId);
  }, []);

  const handlePause = useCallback((videoId: string) => {
    if (playingId === videoId) {
      setPlayingId(null);
    }
  }, [playingId]);

  const handleTimeUpdate = useCallback((videoId: string, currentTime: number, duration: number) => {
    const progress = (currentTime / duration) * 100;
    setCurrentProgress((prev) => ({ ...prev, [videoId]: progress }));

    // Mark as watched when 50% complete
    if (progress >= 50 && !currentProgress[videoId]) {
      setWatchedCount((prev) => prev + 1);
    }
  }, [currentProgress]);

  const handleLike = useCallback((videoId: string) => {
    setLikedIds((prev) => {
      const newLiked = new Set(prev);
      if (newLiked.has(videoId)) {
        newLiked.delete(videoId);
      } else {
        newLiked.add(videoId);
        // Visual feedback animation could go here
      }
      return newLiked;
    });
  }, []);

  const handleShare = useCallback(async (short: ShortVideo) => {
    if (navigator.share) {
      await navigator.share({
        title: short.title,
        text: `Check out this short from ${short.lessonPath}`,
        url: window.location.href,
      });
    }
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === " " || e.key === "k") {
        e.preventDefault();
        if (activeVideo) {
          const video = videoRefs.current[activeVideo];
          if (video) {
            if (video.paused) {
              video.play();
            } else {
              video.pause();
            }
          }
        }
      }
      if (e.key === "m") {
        setMuted((prev) => !prev);
      }
      if (e.key === "Escape") {
        setActiveVideo(null);
      }
      if (e.key === "ArrowLeft") {
        const currentIndex = shorts.findIndex((s) => s.id === activeVideo);
        if (currentIndex > 0) {
          setActiveVideo(shorts[currentIndex - 1].id);
        }
      }
      if (e.key === "ArrowRight") {
        const currentIndex = shorts.findIndex((s) => s.id === activeVideo);
        if (currentIndex < shorts.length - 1) {
          setActiveVideo(shorts[currentIndex + 1].id);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeVideo, shorts]);

  // Group shorts by lesson path
  const groupedShorts = shorts.reduce((acc, short) => {
    const key = short.lessonPath.split("/").slice(0, 2).join("/");
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(short);
    return acc;
  }, {} as Record<string, ShortVideo[]>);

  // Parse lesson path for display
  const parseLessonPath = (path: string) => {
    const parts = path.split("/");
    return {
      part: parts[0]?.replace(/-/g, " ") || "",
      chapter: parts[1]?.replace(/-/g, " ") || "",
      lesson: parts[2]?.replace(/-/g, " ").replace(".md", "") || "",
    };
  };

  // Clean label prefixes from API responses (e.g., "title: " or "note: ")
  const cleanLabel = (text: string | undefined): string => {
    if (!text) return "";
    return text.replace(/^(title|note|lesson):\s*/i, "").trim();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 relative">
          {/* Top Row: Title & Stats */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-xl">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/50 bg-clip-text text-transparent">
                  Learning Shorts
                </h1>
                <p className="text-sm text-muted-foreground">Bite-sized AI agent lessons</p>
              </div>
            </div>

            {/* Stats Bar */}
            <div className="hidden md:flex items-center gap-6">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-accent/10 rounded-lg">
                <Flame className="w-4 h-4 text-orange-500" />
                <span className="font-semibold">{watchedCount}</span>
                <span className="text-xs text-muted-foreground">watched</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-lg">
                <TrendingUp className="w-4 h-4 text-primary" />
                <span className="font-semibold">{shorts.length}</span>
                <span className="text-xs text-muted-foreground">available</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode("story")}
                  className={`p-2 rounded-lg transition-all ${
                    viewMode === "story"
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                  title="Story View"
                >
                  <BookOpen className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-2 rounded-lg transition-all ${
                    viewMode === "grid"
                      ? "bg-primary text-primary-foreground"
                      : "hover:bg-muted"
                  }`}
                  title="Grid View"
                >
                  <Star className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="max-w-md">
            <ShortsSearch
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
              placeholder="Search shorts by topic..."
            />
          </div>
        </div>
      </header>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mb-4" />
            <p className="text-muted-foreground">Loading learning shorts...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <button
              onClick={fetchShorts}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Story View - Horizontal Cards */}
      {!loading && !error && viewMode === "story" && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          {Object.entries(groupedShorts).map(([groupKey, groupShorts]) => {
            const { part, chapter } = parseLessonPath(groupShorts[0].lessonPath);
            return (
              <div key={groupKey} className="mb-12">
                {/* Section Header */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-px bg-border flex-1" />
                  <h2 className="text-lg font-semibold px-4 py-1 bg-primary/10 rounded-full text-primary">
                    {part} / {chapter}
                  </h2>
                  <div className="h-px bg-border flex-1" />
                </div>

                {/* Horizontal Scroll Cards */}
                <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x">
                  {groupShorts.map((short) => {
                    const isLiked = likedIds.has(short.id);
                    const progress = currentProgress[short.id] || 0;
                    const isActive = activeVideo === short.id;
                    const isPlaying = playingId === short.id;

                    return (
                      <div
                        key={short.id}
                        className={`relative flex-shrink-0 w-[320px] rounded-2xl overflow-hidden border-2 transition-all duration-300 cursor-pointer group snap-start ${
                          isActive
                            ? "border-primary shadow-xl shadow-primary/20 scale-105"
                            : "border-border hover:border-primary/50 hover:shadow-lg"
                        }`}
                        onClick={() => setActiveVideo(short.id)}
                      >
                        {/* Video Thumbnail/Preview */}
                        <div className="relative aspect-[9/16] bg-muted">
                          {/* Thumbnail Image */}
                          <img
                            src={short.thumbnailUrl}
                            alt={cleanLabel(short.title)}
                            className="w-full h-full object-cover"
                          />

                          {/* Gradient Overlay */}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                          {/* Play Button Overlay */}
                          <div className="absolute inset-0 flex items-center justify-center">
                            {isActive ? (
                              <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                                {isPlaying ? (
                                  <Pause className="w-8 h-8 text-white" />
                                ) : (
                                  <Play className="w-8 h-8 text-white ml-1" />
                                )}
                              </div>
                            ) : (
                              <div className="w-14 h-14 rounded-full bg-primary/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <Play className="w-7 h-7 text-white ml-1" />
                              </div>
                            )}
                          </div>

                          {/* Duration Badge */}
                          <div className="absolute bottom-3 right-3 px-2 py-1 bg-black/60 backdrop-blur-sm rounded-lg flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            <span className="text-xs font-medium">{short.durationSeconds}s</span>
                          </div>

                          {/* Progress Bar */}
                          {progress > 0 && (
                            <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
                              <div
                                className="h-full bg-primary transition-all"
                                style={{ width: `${progress}%` }}
                              />
                            </div>
                          )}
                        </div>

                        {/* Info Section */}
                        <div className="p-4 bg-card">
                          <h3 className="font-semibold text-base mb-2 line-clamp-2">
                            {cleanLabel(short.title)}
                          </h3>
                          <p className="text-xs text-muted-foreground mb-3">
                            {parseLessonPath(short.lessonPath).lesson}
                          </p>

                          {/* Stats Row */}
                          <div className="flex items-center justify-between text-xs text-muted-foreground">
                            <div className="flex items-center gap-3">
                              <span className="flex items-center gap-1">
                                <Eye className="w-3 h-3" />
                                {short.viewCount || 0}
                              </span>
                              <span className="flex items-center gap-1">
                                <Heart className="w-3 h-3" />
                                {short.likeCount || 0}
                              </span>
                            </div>
                            {progress >= 100 && (
                              <span className="text-green-500 font-medium flex items-center gap-1">
                                <Sparkles className="w-3 h-3" />
                                Watched
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Grid View */}
      {!loading && !error && viewMode === "grid" && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {shorts.map((short) => {
              const isLiked = likedIds.has(short.id);
              const progress = currentProgress[short.id] || 0;

              return (
                <div
                  key={short.id}
                  className="group relative rounded-2xl overflow-hidden border-2 border-border hover:border-primary/50 transition-all cursor-pointer"
                  onClick={() => setActiveVideo(short.id)}
                >
                  <div className="relative aspect-[9/16] bg-muted">
                    <img
                      src={short.thumbnailUrl}
                      alt={cleanLabel(short.title)}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                    <div className="absolute bottom-3 left-3 right-3">
                      <h3 className="font-semibold text-sm line-clamp-2 mb-1">
                        {cleanLabel(short.title)}
                      </h3>
                      <div className="flex items-center justify-between text-xs">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {short.durationSeconds}s
                        </span>
                        {progress >= 100 && (
                          <span className="text-green-400 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            Complete
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Video Modal - Expanded View */}
      {activeVideo && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setActiveVideo(null)}
        >
          <div
            className="relative w-full max-w-4xl bg-card rounded-3xl overflow-hidden shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close Button */}
            <button
              onClick={() => setActiveVideo(null)}
              className="absolute top-4 right-4 z-10 p-2 bg-black/50 hover:bg-black/70 rounded-full transition-colors"
            >
              <X className="w-5 h-5 text-white" />
            </button>

            {/* Video Player */}
            <div className="relative aspect-video bg-black">
              <video
                ref={(el) => {
                  if (el) videoRefs.current[activeVideo] = el;
                }}
                src={(shorts.find((s) => s.id === activeVideo))?.videoUrl}
                className="w-full h-full"
                controls
                autoPlay
                muted={muted}
                onPlay={() => handlePlay(activeVideo)}
                onPause={() => handlePause(activeVideo)}
                onTimeChange={(e) =>
                  handleTimeUpdate(
                    activeVideo,
                    e.currentTarget.currentTime,
                    e.currentTarget.duration
                  )
                }
              />

              {/* Mute Toggle */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setMuted(!muted);
                }}
                className="absolute bottom-16 right-4 p-3 bg-black/50 hover:bg-black/70 rounded-full"
              >
                {muted ? (
                  <VolumeX className="w-5 h-5 text-white" />
                ) : (
                  <Volume2 className="w-5 h-5 text-white" />
                )}
              </button>
            </div>

            {/* Video Info */}
            <div className="p-6">
              {shorts
                .filter((s) => s.id === activeVideo)
                .map((short) => {
                  const isLiked = likedIds.has(short.id);
                  return (
                    <div key={short.id}>
                      <h2 className="text-2xl font-bold mb-2">{cleanLabel(short.title)}</h2>
                      <p className="text-sm text-muted-foreground mb-4">
                        {short.lessonPath}
                      </p>

                      {/* Action Buttons */}
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => handleLike(short.id)}
                          className={`flex items-center gap-2 px-4 py-2.5 rounded-full transition-all ${
                            isLiked
                              ? "bg-red-500 text-white"
                              : "bg-muted hover:bg-red-500 hover:text-white"
                          }`}
                        >
                          <Heart className={`w-5 h-5 ${isLiked ? "fill-current" : ""}`} />
                          <span>{short.likeCount || 0}</span>
                        </button>
                        <button
                          onClick={() => {
                            // Toggle comment section visibility
                            const commentSection = document.getElementById(`comments-${short.id}`);
                            if (commentSection) {
                              commentSection.classList.toggle("hidden");
                              commentSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
                            }
                          }}
                          className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-muted hover:bg-primary hover:text-primary-foreground transition-all"
                        >
                          <MessageCircle className="w-5 h-5" />
                          Comment
                        </button>
                        <button
                          onClick={() => handleShare(short)}
                          className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-muted hover:bg-primary hover:text-primary-foreground transition-all"
                        >
                          <Share2 className="w-5 h-5" />
                        </button>
                        <a
                          href={`/docs/${short.lessonPath.replace(".md", "")}`}
                          className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-primary text-primary-foreground hover:opacity-90 transition-all"
                        >
                          <BookOpen className="w-5 h-5" />
                          Read Full Lesson
                        </a>
                      </div>

                      {/* Comment Section */}
                      <div id={`comments-${short.id}`} className="hidden mt-6 pt-6 border-t">
                        <h3 className="text-lg font-semibold mb-4">Comments</h3>
                        <div className="space-y-4">
                          {/* Add Comment */}
                          <div className="flex gap-3">
                            <input
                              type="text"
                              placeholder="Add a comment..."
                              className="flex-1 px-4 py-2 rounded-full border bg-muted focus:outline-none focus:ring-2 focus:ring-primary"
                              onKeyPress={(e) => {
                                if (e.key === "Enter" && e.currentTarget.value.trim()) {
                                  // TODO: Submit comment to API
                                  e.currentTarget.value = "";
                                }
                              }}
                            />
                            <button className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">
                              Post
                            </button>
                          </div>
                          {/* Placeholder for comments */}
                          <p className="text-sm text-muted-foreground text-center py-4">
                            No comments yet. Be the first to comment!
                          </p>
                        </div>
                      </div>

                      {/* Progress */}
                      {currentProgress[short.id] > 0 && (
                        <div className="mt-4">
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all"
                              style={{ width: `${currentProgress[short.id]}%` }}
                            />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {Math.round(currentProgress[short.id])}% complete
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>

            {/* Navigation */}
            <div className="absolute top-1/2 -translate-y-1/2 left-4">
              <button
                onClick={() => {
                  const currentIndex = shorts.findIndex((s) => s.id === activeVideo);
                  if (currentIndex > 0) setActiveVideo(shorts[currentIndex - 1].id);
                }}
                className="p-3 bg-black/50 hover:bg-black/70 rounded-full disabled:opacity-30 disabled:cursor-not-allowed"
                disabled={shorts.findIndex((s) => s.id === activeVideo) === 0}
              >
                <ChevronRight className="w-6 h-6 text-white rotate-180" />
              </button>
            </div>
            <div className="absolute top-1/2 -translate-y-1/2 right-4">
              <button
                onClick={() => {
                  const currentIndex = shorts.findIndex((s) => s.id === activeVideo);
                  if (currentIndex < shorts.length - 1) setActiveVideo(shorts[currentIndex + 1].id);
                }}
                className="p-3 bg-black/50 hover:bg-black/70 rounded-full disabled:opacity-30 disabled:cursor-not-allowed"
                disabled={shorts.findIndex((s) => s.id === activeVideo) === shorts.length - 1}
              >
                <ChevronRight className="w-6 h-6 text-white" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Hints */}
      {shorts.length > 0 && !activeVideo && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-30">
          <div className="flex items-center gap-4 px-6 py-3 bg-card/80 backdrop-blur-sm rounded-full border shadow-lg text-xs text-muted-foreground">
            <span><kbd className="px-1.5 py-0.5 bg-muted rounded">Click</kbd> to watch</span>
            <span><kbd className="px-1.5 py-0.5 bg-muted rounded">Space</kbd> play/pause</span>
            <span><kbd className="px-1.5 py-0.5 bg-muted rounded">M</kbd> mute</span>
            <span><kbd className="px-1.5 py-0.5 bg-muted rounded">Esc</kbd> close</span>
          </div>
        </div>
      )}

      {/* Mobile Stats Bar */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-card/95 backdrop-blur-sm border-t p-3">
        <div className="flex items-center justify-around text-xs">
          <div className="flex flex-col items-center">
            <Flame className="w-4 h-4 text-orange-500" />
            <span className="font-semibold">{watchedCount}</span>
            <span className="text-muted-foreground">Watched</span>
          </div>
          <div className="flex flex-col items-center">
            <TrendingUp className="w-4 h-4 text-primary" />
            <span className="font-semibold">{shorts.length}</span>
            <span className="text-muted-foreground">Available</span>
          </div>
        </div>
      </div>
    </div>
  );
}
