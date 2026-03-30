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

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import Link from "@docusaurus/Link";
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

const THUMBNAIL_FALLBACK =
  "https://via.placeholder.com/1080x1920/1a1a2e/ffffff?text=No+Thumbnail";
const VIEWED_VIDEOS_STORAGE_KEY = "shorts_viewed_video_ids";
const LIKED_VIDEOS_STORAGE_KEY = "shorts_liked_video_ids";
const WATCHED_VIDEOS_STORAGE_KEY = "shorts_watched_video_ids";

interface VideoComment {
  id: string;
  userId: string;
  videoId: string;
  text: string;
  parentId?: string;
  createdAt: string;
}

export default function ShortsPage() {
  const [shorts, setShorts] = useState<ShortVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeVideo, setActiveVideo] = useState<string | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [muted, setMuted] = useState(true);
  const [currentProgress, setCurrentProgress] = useState<Record<string, number>>({});
  const [likedIds, setLikedIds] = useState<Set<string>>(new Set());
  const [viewCounts, setViewCounts] = useState<Record<string, number>>({});
  const [likeCounts, setLikeCounts] = useState<Record<string, number>>({});
  const [commentCounts, setCommentCounts] = useState<Record<string, number>>({});
  const [filters, setFilters] = useState<ShortsFiltersType>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"story" | "grid">("story");
  const [watchedVideoIds, setWatchedVideoIds] = useState<Set<string>>(new Set());
  const [recordedViewIds, setRecordedViewIds] = useState<Set<string>>(new Set());
  const [commentsByVideo, setCommentsByVideo] = useState<Record<string, VideoComment[]>>({});
  const [openCommentsByVideo, setOpenCommentsByVideo] = useState<Record<string, boolean>>({});
  const [commentDraftByVideo, setCommentDraftByVideo] = useState<Record<string, string>>({});
  const [loadingCommentsByVideo, setLoadingCommentsByVideo] = useState<Record<string, boolean>>({});
  const [commentErrorByVideo, setCommentErrorByVideo] = useState<Record<string, string | null>>({});
  const [submittingCommentByVideo, setSubmittingCommentByVideo] = useState<Record<string, boolean>>({});
  const [pendingLikeIds, setPendingLikeIds] = useState<Set<string>>(new Set());
  const videoRefs = useRef<Record<string, HTMLVideoElement>>({});
  const apiClient = getShortsApiClient();

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(VIEWED_VIDEOS_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        setRecordedViewIds(new Set(parsed.filter((v) => typeof v === "string")));
      }
    } catch {
      // ignore invalid localStorage data
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(LIKED_VIDEOS_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        setLikedIds(new Set(parsed.filter((v) => typeof v === "string")));
      }
    } catch {
      // ignore invalid localStorage data
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const raw = window.localStorage.getItem(WATCHED_VIDEOS_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        setWatchedVideoIds(new Set(parsed.filter((v) => typeof v === "string")));
      }
    } catch {
      // ignore invalid localStorage data
    }
  }, []);

  useEffect(() => {
    if (!activeVideo || typeof document === "undefined") return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [activeVideo]);

  const persistRecordedViews = useCallback((ids: Set<string>) => {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(VIEWED_VIDEOS_STORAGE_KEY, JSON.stringify(Array.from(ids)));
    } catch {
      // ignore storage write errors
    }
  }, []);

  const persistLikedIds = useCallback((ids: Set<string>) => {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(LIKED_VIDEOS_STORAGE_KEY, JSON.stringify(Array.from(ids)));
    } catch {
      // ignore storage write errors
    }
  }, []);

  const persistWatchedIds = useCallback((ids: Set<string>) => {
    if (typeof window === "undefined") return;
    try {
      window.localStorage.setItem(WATCHED_VIDEOS_STORAGE_KEY, JSON.stringify(Array.from(ids)));
    } catch {
      // ignore storage write errors
    }
  }, []);

  const fetchShorts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getVideos({
        ...filters,
        search: searchQuery || undefined,
        limit: 20,
      });
      setShorts(response.shorts);
      setViewCounts(
        response.shorts.reduce<Record<string, number>>((acc, short) => {
          acc[short.id] = short.viewCount || 0;
          return acc;
        }, {})
      );
      setLikeCounts(
        response.shorts.reduce<Record<string, number>>((acc, short) => {
          acc[short.id] = short.likeCount || 0;
          return acc;
        }, {})
      );
      setCommentCounts(
        response.shorts.reduce<Record<string, number>>((acc, short) => {
          acc[short.id] = short.commentCount || 0;
          return acc;
        }, {})
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load shorts");
    } finally {
      setLoading(false);
    }
  }, [apiClient, filters, searchQuery]);

  useEffect(() => {
    fetchShorts();
  }, [fetchShorts]);

  const handlePlay = useCallback((videoId: string) => {
    Object.entries(videoRefs.current).forEach(([id, video]) => {
      if (id !== videoId && video && !video.paused) {
        video.pause();
      }
    });
    setPlayingId(videoId);
  }, []);

  const recordView = useCallback(
    async (videoId: string) => {
      if (recordedViewIds.has(videoId)) return;

      const video = videoRefs.current[videoId];
      if (!video || !Number.isFinite(video.currentTime)) return;

      const duration = Number.isFinite(video.duration) ? video.duration : 0;
      const watchDuration = Math.max(0, Math.floor(video.currentTime));
      const completed = duration > 0 && (video.currentTime / duration) >= 0.9;

      try {
        const result = await apiClient.recordView({
          videoId,
          watchDurationSeconds: watchDuration,
          completed,
        });
        setRecordedViewIds((prev) => {
          const next = new Set(prev).add(videoId);
          persistRecordedViews(next);
          return next;
        });
        setWatchedVideoIds((prev) => {
          if (prev.has(videoId)) return prev;
          const next = new Set(prev).add(videoId);
          persistWatchedIds(next);
          return next;
        });
        if (result.uniqueViewApplied) {
          setViewCounts((prev) => ({
            ...prev,
            [videoId]: result.views ?? ((prev[videoId] || 0) + 1),
          }));
        }
      } catch (err) {
        console.warn("Failed to record view:", err);
      }
    },
    [apiClient, persistRecordedViews, persistWatchedIds, recordedViewIds]
  );

  const handlePause = useCallback(
    (videoId: string) => {
      void recordView(videoId);
      if (playingId === videoId) {
        setPlayingId(null);
      }
    },
    [playingId, recordView]
  );

  const handleTimeUpdate = useCallback(
    (videoId: string, currentTime: number, duration: number) => {
      const progress = duration > 0 ? (currentTime / duration) * 100 : 0;
      setCurrentProgress((prev) => ({ ...prev, [videoId]: progress }));

      if (progress >= 50) {
        setWatchedVideoIds((prev) => {
          if (prev.has(videoId)) return prev;
          const next = new Set(prev);
          next.add(videoId);
          persistWatchedIds(next);
          return next;
        });
      }
    },
    [persistWatchedIds]
  );

  const loadComments = useCallback(
    async (videoId: string) => {
      setLoadingCommentsByVideo((prev) => ({ ...prev, [videoId]: true }));
      setCommentErrorByVideo((prev) => ({ ...prev, [videoId]: null }));
      try {
        const result = await apiClient.getComments(videoId);
        setCommentsByVideo((prev) => ({ ...prev, [videoId]: result.comments }));
        setCommentCounts((prev) => ({ ...prev, [videoId]: result.totalCount }));
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to load comments";
        setCommentErrorByVideo((prev) => ({ ...prev, [videoId]: message }));
      } finally {
        setLoadingCommentsByVideo((prev) => ({ ...prev, [videoId]: false }));
      }
    },
    [apiClient]
  );

  const handleLike = useCallback(
    async (videoId: string) => {
      if (pendingLikeIds.has(videoId)) return;
      if (likedIds.has(videoId)) return;

      setPendingLikeIds((prev) => new Set(prev).add(videoId));

      try {
        const result = await apiClient.likeVideo(videoId);
        setLikedIds((prev) => {
          const next = new Set(prev);
          next.add(videoId);
          persistLikedIds(next);
          return next;
        });
        if (typeof result.likes === "number") {
          setLikeCounts((prev) => ({
            ...prev,
            [videoId]: result.likes,
          }));
        } else if (result.likeApplied) {
          setLikeCounts((prev) => ({
            ...prev,
            [videoId]: (prev[videoId] || 0) + 1,
          }));
        }
      } catch (err) {
        console.error("Failed to update like:", err);
      } finally {
        setPendingLikeIds((prev) => {
          const next = new Set(prev);
          next.delete(videoId);
          return next;
        });
      }
    },
    [apiClient, likedIds, pendingLikeIds, persistLikedIds]
  );

  const handleToggleComments = useCallback(
    (videoId: string) => {
      setOpenCommentsByVideo((prev) => ({ ...prev, [videoId]: true }));
      if (!commentsByVideo[videoId]) {
        void loadComments(videoId);
      }
      if (typeof window !== "undefined") {
        window.requestAnimationFrame(() => {
          const el = document.getElementById(`comments-${videoId}`);
          if (el) {
            el.scrollIntoView({ behavior: "smooth", block: "start" });
          }
        });
      }
    },
    [commentsByVideo, loadComments]
  );

  useEffect(() => {
    if (!activeVideo) return;
    setOpenCommentsByVideo((prev) => ({ ...prev, [activeVideo]: true }));
    if (!commentsByVideo[activeVideo]) {
      void loadComments(activeVideo);
    }
  }, [activeVideo, commentsByVideo, loadComments]);

  const handleSubmitComment = useCallback(
    async (videoId: string) => {
      const text = (commentDraftByVideo[videoId] || "").trim();
      if (!text) return;

      setSubmittingCommentByVideo((prev) => ({ ...prev, [videoId]: true }));
      try {
        const result = await apiClient.commentOnVideo({ videoId, text });
        setCommentsByVideo((prev) => ({
          ...prev,
          [videoId]: [
            {
              id: result.commentId,
              userId: "you",
              videoId,
              text: result.text,
              createdAt: result.createdAt,
            },
            ...(prev[videoId] || []),
          ],
        }));
        setCommentCounts((prev) => ({ ...prev, [videoId]: (prev[videoId] || 0) + 1 }));
        setCommentDraftByVideo((prev) => ({ ...prev, [videoId]: "" }));
        setCommentErrorByVideo((prev) => ({ ...prev, [videoId]: null }));
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to submit comment";
        setCommentErrorByVideo((prev) => ({ ...prev, [videoId]: message }));
      } finally {
        setSubmittingCommentByVideo((prev) => ({ ...prev, [videoId]: false }));
      }
    },
    [apiClient, commentDraftByVideo]
  );

  const handleShare = useCallback(async (short: ShortVideo) => {
    const shareUrl = typeof window !== "undefined" ? window.location.href : "";

    if (navigator.share) {
      await navigator.share({
        title: short.title,
        text: `Check out this short from ${short.lessonPath}`,
        url: shareUrl,
      });
      return;
    }

    if (navigator.clipboard && shareUrl) {
      await navigator.clipboard.writeText(shareUrl);
    }
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === " " || e.key === "k") {
        e.preventDefault();
        if (activeVideo) {
          const video = videoRefs.current[activeVideo];
          if (video) {
            if (video.paused) {
              void video.play();
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
        if (activeVideo) {
          void recordView(activeVideo);
        }
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
  }, [activeVideo, recordView, shorts]);

  const groupedShorts = useMemo(
    () =>
      shorts.reduce((acc, short) => {
        const key = short.lessonPath.split("/").slice(0, 2).join("/");
        if (!acc[key]) {
          acc[key] = [];
        }
        acc[key].push(short);
        return acc;
      }, {} as Record<string, ShortVideo[]>),
    [shorts]
  );

  const parseLessonPath = (path: string) => {
    const parts = path.split("/");
    return {
      part: parts[0]?.replace(/-/g, " ") || "",
      chapter: parts[1]?.replace(/-/g, " ") || "",
      lesson: parts[2]?.replace(/-/g, " ").replace(".md", "") || "",
    };
  };

  const cleanLabel = (text: string | undefined): string => {
    if (!text) return "";
    return text.replace(/^(title|note|lesson):\s*/i, "").trim();
  };

  const activeShort = shorts.find((s) => s.id === activeVideo) ?? null;
  const activeIndex = activeVideo ? shorts.findIndex((s) => s.id === activeVideo) : -1;
  const totalViews = Object.values(viewCounts).reduce((sum, count) => sum + count, 0);
  const totalLikes = Object.values(likeCounts).reduce((sum, count) => sum + count, 0);
  const completedCount = watchedVideoIds.size;

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,rgba(59,130,246,0.18),transparent_32%),linear-gradient(180deg,hsl(var(--background))_0%,hsl(var(--background))_58%,hsl(var(--muted)/0.45)_100%)] pb-24 md:pb-8">
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/95 backdrop-blur-xl supports-[backdrop-filter]:bg-background/80">
        <div className="mx-auto max-w-7xl px-4 py-4 md:px-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
              <div className="min-w-0">
                <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
                  <Link to="/" className="hover:text-primary transition-colors text-inherit no-underline">
                    Learning Shorts
                  </Link>
                </h1>
                <p className="mt-1 max-w-2xl text-sm text-muted-foreground sm:text-[15px]">
                  Short video lessons for quick browsing and review.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={() => setViewMode("story")}
                  className={`inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-sm font-medium transition-colors ${
                    viewMode === "story"
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background hover:bg-muted"
                  }`}
                  title="Story View"
                >
                  <BookOpen className="h-4 w-4" />
                  Story
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`inline-flex items-center gap-2 rounded-lg border px-3.5 py-2 text-sm font-medium transition-colors ${
                    viewMode === "grid"
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background hover:bg-muted"
                  }`}
                  title="Grid View"
                >
                  <Star className="h-4 w-4" />
                  Grid
                </button>
                <button
                  onClick={() => {
                    setFilters({});
                    setSearchQuery("");
                  }}
                  className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-3.5 py-2 text-sm font-medium transition-colors hover:bg-muted"
                >
                  <RotateCcw className="h-4 w-4" />
                  Reset
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div className="w-full max-w-2xl">
                <ShortsSearch
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  placeholder="Search shorts by topic, chapter, or lesson..."
                />
              </div>

              <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                <span>{completedCount} watched</span>
                <span>{shorts.length} available</span>
                <span>{totalViews} views</span>
                <span>{totalLikes} likes</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {loading && (
        <div className="flex min-h-[420px] items-center justify-center px-4">
          <div className="rounded-3xl border border-border/60 bg-card/70 px-8 py-10 text-center shadow-xl backdrop-blur-sm">
            <div className="mb-4 inline-block h-9 w-9 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="text-muted-foreground">Loading learning shorts...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex min-h-[420px] items-center justify-center px-4">
          <div className="max-w-md rounded-3xl border border-red-500/30 bg-red-500/10 px-6 py-8 text-center shadow-lg">
            <p className="mb-4 text-red-500">{error}</p>
            <button
              onClick={fetchShorts}
              className="rounded-full bg-primary px-5 py-2.5 text-primary-foreground transition-opacity hover:opacity-90"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {!loading && !error && shorts.length === 0 && (
        <div className="mx-auto flex min-h-[420px] max-w-2xl items-center justify-center px-4 py-10">
          <div className="rounded-[2rem] border border-border/60 bg-card/75 px-8 py-10 text-center shadow-xl backdrop-blur-sm">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <Sparkles className="h-6 w-6" />
            </div>
            <h2 className="text-xl font-semibold">No shorts match the current view</h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Reset the search or try again later when new clips are published.
            </p>
          </div>
        </div>
      )}

      {!loading && !error && viewMode === "story" && shorts.length > 0 && (
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-8">
          {Object.entries(groupedShorts).map(([groupKey, groupShorts]) => {
            const { part, chapter } = parseLessonPath(groupShorts[0].lessonPath);
            return (
              <section key={groupKey} className="mb-10 last:mb-0">
                <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="h-px flex-1 bg-border/70 sm:max-w-14" />
                    <div className="min-w-0 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
                      <span className="truncate">{part} / {chapter}</span>
                    </div>
                  </div>
                  <div className="self-start rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">
                    {groupShorts.length} clip{groupShorts.length === 1 ? "" : "s"}
                  </div>
                </div>

                <div className="-mx-4 overflow-x-auto px-4 pb-2 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                  <div className="flex snap-x snap-mandatory gap-4 pb-4 sm:gap-5">
                    {groupShorts.map((short) => {
                      const progress = currentProgress[short.id] || 0;
                      const isActive = activeVideo === short.id;
                      const isPlaying = playingId === short.id;

                      return (
                        <button
                          key={short.id}
                          type="button"
                          className={`group relative w-[78vw] min-w-[78vw] max-w-[340px] snap-start overflow-hidden rounded-[1.75rem] border text-left transition-all duration-300 sm:w-[320px] sm:min-w-[320px] ${
                            isActive
                              ? "scale-[1.01] border-primary shadow-2xl shadow-primary/20"
                              : "border-border/70 bg-card hover:-translate-y-1 hover:border-primary/40 hover:shadow-xl"
                          }`}
                          onClick={() => setActiveVideo(short.id)}
                        >
                          <div className="relative aspect-[9/16] bg-muted">
                            <img
                              src={short.thumbnailUrl}
                              alt={cleanLabel(short.title)}
                              className="h-full w-full object-contain bg-black"
                              onError={(e) => {
                                const img = e.currentTarget;
                                if (img.src !== THUMBNAIL_FALLBACK) {
                                  img.src = THUMBNAIL_FALLBACK;
                                }
                              }}
                            />

                            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/15 to-transparent" />
                            <div className="absolute left-3 top-3 rounded-full bg-black/55 px-2.5 py-1 text-[11px] font-medium text-white backdrop-blur-sm">
                              {parseLessonPath(short.lessonPath).lesson}
                            </div>

                            <div className="absolute inset-0 flex items-center justify-center">
                              {isActive ? (
                                <div className="flex h-16 w-16 items-center justify-center rounded-full border border-white/20 bg-white/15 text-white backdrop-blur-sm">
                                  {isPlaying ? (
                                    <Pause className="h-8 w-8" />
                                  ) : (
                                    <Play className="ml-1 h-8 w-8" />
                                  )}
                                </div>
                              ) : (
                                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/90 text-white opacity-90 shadow-lg transition-all duration-300 group-hover:scale-105 group-hover:opacity-100">
                                  <Play className="ml-1 h-7 w-7" />
                                </div>
                              )}
                            </div>

                            <div className="absolute bottom-3 right-3 flex items-center gap-1 rounded-full bg-black/60 px-2.5 py-1 text-xs font-medium text-white backdrop-blur-sm">
                              <Clock className="h-3 w-3" />
                              <span>{short.durationSeconds}s</span>
                            </div>

                            {progress > 0 && (
                              <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
                                <div
                                  className="h-full bg-primary transition-all"
                                  style={{ width: `${progress}%` }}
                                />
                              </div>
                            )}
                          </div>

                          <div className="space-y-3 bg-card p-4">
                            <div>
                              <h3 className="line-clamp-2 text-base font-semibold leading-6">
                                {cleanLabel(short.title)}
                              </h3>
                              <p className="mt-1 text-xs text-muted-foreground">{short.lessonPath}</p>
                            </div>

                            <div className="flex items-center justify-between gap-3 text-xs text-muted-foreground">
                              <div className="flex flex-wrap items-center gap-3">
                                <span className="flex items-center gap-1">
                                  <Eye className="h-3 w-3" />
                                  {viewCounts[short.id] ?? short.viewCount ?? 0}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Heart className="h-3 w-3" />
                                  {likeCounts[short.id] ?? short.likeCount ?? 0}
                                </span>
                                <span className="flex items-center gap-1">
                                  <MessageCircle className="h-3 w-3" />
                                  {commentCounts[short.id] ?? short.commentCount ?? 0}
                                </span>
                              </div>
                              {progress >= 100 && (
                                <span className="flex items-center gap-1 font-medium text-emerald-500">
                                  <Sparkles className="h-3 w-3" />
                                  Watched
                                </span>
                              )}
                            </div>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </section>
            );
          })}
        </div>
      )}

      {!loading && !error && viewMode === "grid" && shorts.length > 0 && (
        <div className="mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-8">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {shorts.map((short) => {
              const progress = currentProgress[short.id] || 0;

              return (
                <button
                  key={short.id}
                  type="button"
                  className="group overflow-hidden rounded-[1.75rem] border border-border/70 bg-card text-left shadow-sm transition-all hover:-translate-y-1 hover:border-primary/40 hover:shadow-xl"
                  onClick={() => setActiveVideo(short.id)}
                >
                  <div className="relative aspect-[9/16] bg-muted">
                    <img
                      src={short.thumbnailUrl}
                      alt={cleanLabel(short.title)}
                      className="h-full w-full object-contain bg-black"
                      onError={(e) => {
                        const img = e.currentTarget;
                        if (img.src !== THUMBNAIL_FALLBACK) {
                          img.src = THUMBNAIL_FALLBACK;
                        }
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/15 to-transparent" />
                    <div className="absolute left-3 top-3 rounded-full bg-black/55 px-2.5 py-1 text-[11px] font-medium text-white backdrop-blur-sm">
                      {short.durationSeconds}s
                    </div>
                    <div className="absolute inset-x-0 bottom-0 p-4 text-white">
                      <h3 className="line-clamp-2 text-sm font-semibold leading-5">{cleanLabel(short.title)}</h3>
                      <p className="mt-1 line-clamp-1 text-xs text-white/70">{parseLessonPath(short.lessonPath).lesson}</p>
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-white/15 text-white backdrop-blur-sm">
                        <Play className="ml-1 h-7 w-7" />
                      </div>
                    </div>
                    {progress > 0 && (
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/30">
                        <div className="h-full bg-primary transition-all" style={{ width: `${progress}%` }} />
                      </div>
                    )}
                  </div>

                  <div className="space-y-3 p-4">
                    <p className="line-clamp-2 text-sm text-muted-foreground">{short.lessonPath}</p>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        {viewCounts[short.id] ?? short.viewCount ?? 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <Heart className="h-3 w-3" />
                        {likeCounts[short.id] ?? short.likeCount ?? 0}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="h-3 w-3" />
                        {commentCounts[short.id] ?? short.commentCount ?? 0}
                      </span>
                      {progress >= 100 && (
                        <span className="flex items-center gap-1 font-medium text-emerald-500">
                          <Sparkles className="h-3 w-3" />
                          Complete
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {activeShort && (
        <div
          className="fixed inset-0 z-50 bg-black/88 p-3 backdrop-blur-md sm:p-4"
          onClick={() => {
            void recordView(activeShort.id);
            setActiveVideo(null);
          }}
        >
          <div
            className="relative mx-auto flex h-full w-full max-w-6xl flex-col overflow-hidden rounded-[2rem] border border-white/10 bg-card shadow-2xl lg:h-[min(92vh,960px)] lg:flex-row"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => {
                void recordView(activeShort.id);
                setActiveVideo(null);
              }}
              className="absolute right-3 top-3 z-20 rounded-full bg-black/50 p-2.5 text-white transition-colors hover:bg-black/70"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="relative shrink-0 border-b border-border/50 bg-black lg:flex lg:w-[46%] lg:min-w-[360px] lg:items-center lg:justify-center lg:border-b-0 lg:border-r">
              <div className="relative mx-auto aspect-[9/16] w-full max-w-[420px] bg-black lg:max-h-full">
                <video
                  ref={(el) => {
                    if (el) videoRefs.current[activeShort.id] = el;
                  }}
                  src={activeShort.videoUrl}
                  className="h-full w-full bg-black object-contain"
                  controls
                  autoPlay
                  muted={muted}
                  playsInline
                  onPlay={() => handlePlay(activeShort.id)}
                  onPause={() => handlePause(activeShort.id)}
                  onTimeUpdate={(e) =>
                    handleTimeUpdate(
                      activeShort.id,
                      e.currentTarget.currentTime,
                      e.currentTarget.duration
                    )
                  }
                />

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setMuted(!muted);
                  }}
                  className="absolute bottom-4 right-4 rounded-full bg-black/55 p-3 text-white transition-colors hover:bg-black/75"
                >
                  {muted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                </button>
              </div>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto">
              <div className="flex min-h-full flex-col p-4 sm:p-6 lg:p-8">
                <div className="pr-12">
                  <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span className="rounded-full bg-primary/10 px-3 py-1 font-medium text-primary">
                      {parseLessonPath(activeShort.lessonPath).part}
                    </span>
                    <span className="rounded-full bg-muted px-3 py-1">
                      {parseLessonPath(activeShort.lessonPath).chapter}
                    </span>
                    <span className="rounded-full bg-muted px-3 py-1">
                      {activeShort.durationSeconds}s
                    </span>
                  </div>

                  <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">
                    {cleanLabel(activeShort.title)}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-muted-foreground">{activeShort.lessonPath}</p>
                </div>

                <div className="mt-5 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1.5 rounded-full bg-muted px-3 py-1.5">
                    <Eye className="h-4 w-4" />
                    {viewCounts[activeShort.id] ?? activeShort.viewCount ?? 0} views
                  </span>
                  <span className="flex items-center gap-1.5 rounded-full bg-muted px-3 py-1.5">
                    <Heart className="h-4 w-4" />
                    {likeCounts[activeShort.id] ?? activeShort.likeCount ?? 0} likes
                  </span>
                  <span className="flex items-center gap-1.5 rounded-full bg-muted px-3 py-1.5">
                    <MessageCircle className="h-4 w-4" />
                    {commentCounts[activeShort.id] ?? activeShort.commentCount ?? 0} comments
                  </span>
                </div>

                <div className="sticky top-0 z-10 mt-6 flex flex-wrap items-center gap-3 border-y border-border/60 bg-card/95 py-4 backdrop-blur supports-[backdrop-filter]:bg-card/75">
                  <button
                    onClick={() => void handleLike(activeShort.id)}
                    disabled={pendingLikeIds.has(activeShort.id)}
                    className={`inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-sm font-medium transition-all ${
                      likedIds.has(activeShort.id)
                        ? "bg-red-500 text-white"
                        : "bg-muted hover:bg-red-500 hover:text-white"
                    } ${pendingLikeIds.has(activeShort.id) ? "cursor-not-allowed opacity-60" : ""}`}
                  >
                    <Heart className={`h-4 w-4 ${likedIds.has(activeShort.id) ? "fill-current" : ""}`} />
                    <span>{likeCounts[activeShort.id] ?? activeShort.likeCount ?? 0}</span>
                  </button>
                  <button
                    onClick={() => handleToggleComments(activeShort.id)}
                    className="inline-flex items-center gap-2 rounded-full bg-muted px-4 py-2.5 text-sm font-medium transition-all hover:bg-primary hover:text-primary-foreground"
                  >
                    <MessageCircle className="h-4 w-4" />
                    Comment ({commentCounts[activeShort.id] ?? activeShort.commentCount ?? 0})
                  </button>
                  <button
                    onClick={() => void handleShare(activeShort)}
                    className="inline-flex items-center gap-2 rounded-full bg-muted px-4 py-2.5 text-sm font-medium transition-all hover:bg-primary hover:text-primary-foreground"
                  >
                    <Share2 className="h-4 w-4" />
                    Share
                  </button>
                  <a
                    href={`/docs/${activeShort.lessonPath.replace(".md", "")}`}
                    className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
                  >
                    <BookOpen className="h-4 w-4" />
                    Read full lesson
                  </a>
                </div>

                <section id={`comments-${activeShort.id}`} className="mt-6 rounded-[1.5rem] border border-border/60 bg-muted/20 p-4 sm:p-5">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <h3 className="text-lg font-semibold">Comments</h3>
                    {openCommentsByVideo[activeShort.id] && (
                      <span className="text-xs text-muted-foreground">Latest discussion first</span>
                    )}
                  </div>

                  <div className="flex flex-col gap-3 sm:flex-row">
                    <input
                      type="text"
                      placeholder="Add a comment..."
                      value={commentDraftByVideo[activeShort.id] || ""}
                      className="min-w-0 flex-1 rounded-full border bg-background px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      onChange={(e) =>
                        setCommentDraftByVideo((prev) => ({
                          ...prev,
                          [activeShort.id]: e.target.value,
                        }))
                      }
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          void handleSubmitComment(activeShort.id);
                        }
                      }}
                    />
                    <button
                      onClick={() => void handleSubmitComment(activeShort.id)}
                      disabled={submittingCommentByVideo[activeShort.id]}
                      className="rounded-full bg-primary px-5 py-3 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Post
                    </button>
                  </div>

                  {loadingCommentsByVideo[activeShort.id] && (
                    <p className="py-6 text-center text-sm text-muted-foreground">Loading comments...</p>
                  )}

                  {!!commentErrorByVideo[activeShort.id] && (
                    <div className="mt-4 rounded-2xl border border-red-300/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                      {commentErrorByVideo[activeShort.id]}
                    </div>
                  )}

                  {!loadingCommentsByVideo[activeShort.id] &&
                    (commentsByVideo[activeShort.id] || []).length === 0 && (
                      <p className="py-6 text-center text-sm text-muted-foreground">
                        No comments yet. Be the first to comment.
                      </p>
                    )}

                  <div className="mt-4 space-y-3">
                    {(commentsByVideo[activeShort.id] || []).map((comment) => (
                      <div key={comment.id} className="rounded-2xl border border-border/60 bg-background/80 p-4 shadow-sm">
                        <div className="mb-2 flex items-center justify-between gap-3">
                          <p className="text-sm font-medium">{comment.userId}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(comment.createdAt).toLocaleString()}
                          </p>
                        </div>
                        <p className="text-sm leading-6 text-muted-foreground">{comment.text}</p>
                      </div>
                    ))}
                  </div>
                </section>

                {currentProgress[activeShort.id] > 0 && (
                  <div className="mt-6">
                    <div className="h-2 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{ width: `${currentProgress[activeShort.id]}%` }}
                      />
                    </div>
                    <p className="mt-2 text-xs text-muted-foreground">
                      {Math.round(currentProgress[activeShort.id])}% complete
                    </p>
                  </div>
                )}
              </div>
            </div>

            <div className="pointer-events-none absolute inset-x-0 bottom-4 flex justify-center px-4 lg:pointer-events-auto lg:inset-x-auto lg:bottom-auto lg:left-4 lg:top-1/2 lg:-translate-y-1/2 lg:px-0">
              <div className="flex items-center gap-2 rounded-full bg-black/45 p-1.5 backdrop-blur-sm lg:block lg:rounded-2xl lg:bg-transparent lg:p-0">
                <button
                  onClick={() => {
                    if (activeIndex > 0) setActiveVideo(shorts[activeIndex - 1].id);
                  }}
                  className="pointer-events-auto rounded-full bg-black/55 p-3 text-white transition-colors hover:bg-black/75 disabled:cursor-not-allowed disabled:opacity-30"
                  disabled={activeIndex <= 0}
                >
                  <ChevronRight className="h-5 w-5 rotate-180" />
                </button>
                <button
                  onClick={() => {
                    if (activeIndex < shorts.length - 1) setActiveVideo(shorts[activeIndex + 1].id);
                  }}
                  className="pointer-events-auto rounded-full bg-black/55 p-3 text-white transition-colors hover:bg-black/75 disabled:cursor-not-allowed disabled:opacity-30 lg:mt-3"
                  disabled={activeIndex === -1 || activeIndex >= shorts.length - 1}
                >
                  <ChevronRight className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {shorts.length > 0 && !activeVideo && (
        <div className="fixed bottom-4 left-1/2 z-20 hidden -translate-x-1/2 lg:block">
          <div className="flex items-center gap-3 rounded-full border border-border/70 bg-background/92 px-4 py-2 text-xs text-muted-foreground shadow-md backdrop-blur-sm">
            <span><kbd className="rounded bg-muted px-1.5 py-0.5">Click</kbd> watch</span>
            <span><kbd className="rounded bg-muted px-1.5 py-0.5">Space</kbd> play</span>
            <span><kbd className="rounded bg-muted px-1.5 py-0.5">M</kbd> mute</span>
            <span><kbd className="rounded bg-muted px-1.5 py-0.5">Esc</kbd> close</span>
          </div>
        </div>
      )}

      {!activeVideo && (
        <div className="fixed bottom-0 left-0 right-0 z-30 border-t border-border/60 bg-card/92 p-3 backdrop-blur-md md:hidden">
          <div className="mx-auto flex max-w-md items-center justify-around text-xs">
            <div className="flex flex-col items-center">
              <Flame className="h-4 w-4 text-orange-500" />
              <span className="font-semibold">{completedCount}</span>
              <span className="text-muted-foreground">Watched</span>
            </div>
            <div className="flex flex-col items-center">
              <TrendingUp className="h-4 w-4 text-primary" />
              <span className="font-semibold">{shorts.length}</span>
              <span className="text-muted-foreground">Available</span>
            </div>
            <div className="flex flex-col items-center">
              <Heart className="h-4 w-4 text-pink-500" />
              <span className="font-semibold">{totalLikes}</span>
              <span className="text-muted-foreground">Likes</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
