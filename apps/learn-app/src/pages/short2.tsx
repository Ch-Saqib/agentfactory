/**
 * Temporary Shorts 2 Page - For testing new Shorts Generator API
 *
 * This page connects to the new shorts-generator backend at /api/v1/shorts
 * Once verified working, this will replace the existing shorts.tsx page.
 */

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Head from "@docusaurus/Head";
import Layout from "@theme/Layout";
import {
  Pause,
  Play,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Sparkles,
  Flame,
  Eye,
  Heart,
  MessageSquare,
  Grid3x3,
  Film,
  TrendingUp,
  CheckCircle,
  XCircle,
  Loader2,
} from "lucide-react";

// Types matching the new Shorts API response
interface ShortVideoAPI {
  id: number;
  chapter_id: string;
  chapter_title: string;
  video_url: string;
  thumbnail_url: string;
  duration_seconds: number;
  created_at: string;
  file_size_mb?: number;
  views?: number;
  likes?: number;
  comments?: number;
}

// Transform API response to match existing ShortVideo interface
function transformShortVideoAPI(video: ShortVideoAPI) {
  return {
    id: video.id.toString(),
    lessonPath: video.chapter_id,
    title: video.chapter_title,
    videoUrl: video.video_url,
    thumbnailUrl: video.thumbnail_url,
    durationSeconds: video.duration_seconds,
    viewCount: video.views || 0,
    likeCount: video.likes || 0,
    commentCount: video.comments || 0,
  };
}

interface ShortVideo {
  id: string;
  lessonPath: string;
  title: string;
  videoUrl: string;
  thumbnailUrl: string;
  durationSeconds: number;
  viewCount: number;
  likeCount: number;
  commentCount: number;
}

interface VideoModal {
  isOpen: boolean;
  video: ShortVideo | null;
}

type ViewMode = "story" | "grid";

interface StoriesResponse {
  videos: ShortVideoAPI[];
  total_count: number;
}

// API Configuration (using port 8001 since 8000 is taken)
const SHORTS_API_URL = "http://localhost:8001/api/v1/shorts";

// Format duration (seconds to MM:SS)
function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

// Format view count (e.g., 1.2K, 1M)
function formatViewCount(count: number): string {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
}

// API Client Functions
async function fetchShortsVideos(
  limit: number = 20,
  offset: number = 0
): Promise<{ videos: ShortVideo[]; totalCount: number }> {
  try {
    const response = await fetch(
      `${SHORTS_API_URL}/videos/for-page?limit=${limit}&offset=${offset}`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    // API returns a plain array, not an object with videos property
    const data: ShortVideoAPI[] = await response.json();
    const videos = data.map(transformShortVideoAPI);

    return { videos, totalCount: videos.length };
  } catch (error) {
    console.error("Failed to fetch shorts:", error);
    throw error;
  }
}

async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${SHORTS_API_URL}/health`);
    const data = await response.json();
    return data.status === "healthy" || data.status === "degraded";
  } catch {
    return false;
  }
}

// Horizontal Story Card Component
function StoryCard({
  video,
  index,
  onClick,
}: {
  video: ShortVideo;
  index: number;
  onClick: () => void;
}) {
  const [imageError, setImageError] = useState(false);

  return (
    <div
      className="flex-shrink-0 w-44 cursor-pointer group"
      onClick={onClick}
    >
      {/* Thumbnail with gradient border */}
      <div className="relative aspect-[9/16] rounded-2xl overflow-hidden mb-2 ring-2 ring-gradient-to-r from-blue-500 via-purple-500 to-pink-500 ring-offset-2 ring-offset-gray-900">
        {!imageError ? (
          <img
            src={video.thumbnailUrl}
            alt={video.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
            <Film className="w-16 h-16 text-white/50" />
          </div>
        )}

        {/* Play button overlay */}
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-14 h-14 rounded-full bg-white/90 flex items-center justify-center">
            <Play className="w-6 h-6 text-gray-900 ml-1" fill="currentColor" />
          </div>
        </div>

        {/* Duration badge */}
        <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded-md">
          <span className="text-xs font-medium text-white">
            {formatDuration(video.durationSeconds)}
          </span>
        </div>

        {/* Index badge */}
        <div className="absolute top-2 left-2 bg-gradient-to-r from-blue-500 to-purple-600 px-2 py-1 rounded-full">
          <span className="text-xs font-bold text-white">#{index + 1}</span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-sm font-medium text-gray-200 line-clamp-2 group-hover:text-white transition-colors">
        {video.title}
      </h3>

      {/* Engagement stats */}
      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <Eye className="w-3 h-3" />
          <span>{formatViewCount(video.viewCount)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Heart className="w-3 h-3" />
          <span>{formatViewCount(video.likeCount)}</span>
        </div>
      </div>
    </div>
  );
}

// Grid Video Card Component
function GridCard({
  video,
  index,
  onClick,
}: {
  video: ShortVideo;
  index: number;
  onClick: () => void;
}) {
  const [imageError, setImageError] = useState(false);

  return (
    <div
      className="cursor-pointer group"
      onClick={onClick}
    >
      <div className="relative aspect-[9/16] rounded-xl overflow-hidden ring-1 ring-white/10 group-hover:ring-purple-500/50 transition-all">
        {!imageError ? (
          <img
            src={video.thumbnailUrl}
            alt={video.title}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-blue-600 to-purple-700 flex items-center justify-center">
            <Film className="w-12 h-12 text-white/50" />
          </div>
        )}

        {/* Play overlay */}
        <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-12 h-12 rounded-full bg-white/90 flex items-center justify-center">
            <Play className="w-5 h-5 text-gray-900 ml-0.5" fill="currentColor" />
          </div>
        </div>

        {/* Duration badge */}
        <div className="absolute bottom-2 right-2 bg-black/70 px-2 py-1 rounded-md">
          <span className="text-xs font-medium text-white">
            {formatDuration(video.durationSeconds)}
          </span>
        </div>
      </div>

      {/* Title */}
      <h3 className="text-sm font-medium text-gray-200 line-clamp-2 mt-2 group-hover:text-white transition-colors">
        {video.title}
      </h3>

      {/* Stats */}
      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <Eye className="w-3 h-3" />
          <span>{formatViewCount(video.viewCount)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Heart className="w-3 h-3" />
          <span>{formatViewCount(video.likeCount)}</span>
        </div>
        <div className="flex items-center gap-1">
          <MessageSquare className="w-3 h-3" />
          <span>{video.commentCount}</span>
        </div>
      </div>
    </div>
  );
}

// Video Modal Component
function VideoModal({
  isOpen,
  video,
  onClose,
}: {
  isOpen: boolean;
  video: ShortVideo | null;
  onClose: () => void;
}) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  if (!isOpen || !video) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-md h-[80vh] max-h-[800px] bg-gray-900 rounded-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-colors"
        >
          <XCircle className="w-6 h-6" />
        </button>

        {/* Video player */}
        <div className="w-full h-full flex items-center justify-center">
          <video
            src={video.videoUrl}
            controls
            autoPlay
            className="w-full h-full object-contain bg-black"
          />
        </div>

        {/* Video info overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 pt-12">
          <h2 className="text-lg font-semibold text-white mb-2">
            {video.title}
          </h2>
          <div className="flex items-center gap-4 text-sm text-gray-300">
            <div className="flex items-center gap-1">
              <Eye className="w-4 h-4" />
              <span>{formatViewCount(video.viewCount)} views</span>
            </div>
            <div className="flex items-center gap-1">
              <Heart className="w-4 h-4" />
              <span>{formatViewCount(video.likeCount)}</span>
            </div>
            <div className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4" />
              <span>{video.commentCount}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// API Health Indicator
function ApiHealthIndicator({ isHealthy, isLoading }: { isHealthy: boolean | null; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Checking API...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      {isHealthy ? (
        <>
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="text-green-500">API Connected</span>
        </>
      ) : (
        <>
          <XCircle className="w-4 h-4 text-red-500" />
          <span className="text-red-500">API Offline</span>
        </>
      )}
    </div>
  );
}

// Main Short2 Page Component
export default function Short2Page(): JSX.Element {
  const [videos, setVideos] = useState<ShortVideo[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("story");
  const [modal, setModal] = useState<VideoModal>({ isOpen: false, video: null });
  const [scrollIndex, setScrollIndex] = useState(0);
  const [isApiHealthy, setIsApiHealthy] = useState<boolean | null>(null);
  const [isCheckingHealth, setIsCheckingHealth] = useState(true);

  // Load videos function
  const loadVideos = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await fetchShortsVideos(50);
      setVideos(result.videos);
      setTotalCount(result.totalCount);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load videos. Make sure the shorts-generator server is running on localhost:8000"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      setIsCheckingHealth(true);
      const healthy = await checkApiHealth();
      setIsApiHealthy(healthy);
      setIsCheckingHealth(false);
    };
    checkHealth();
  }, []);

  // Load videos on mount
  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  // Scroll controls for story view
  const scrollContainer = useCallback((element: HTMLElement | null, direction: "left" | "right") => {
    if (!element) return;
    const scrollAmount = 400;
    element.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }, []);

  const storiesContainerId = useMemo(() => "stories-container", []);

  const openVideo = useCallback((video: ShortVideo) => {
    setModal({ isOpen: true, video });
  }, []);

  const closeVideo = useCallback(() => {
    setModal({ isOpen: false, video: null });
  }, []);

  return (
    <Layout title="Shorts 2 - Testing" description="Test page for new Shorts Generator API">
      <Head>
        <meta name="robots" content="noindex, nofollow" />
      </Head>

      <main className="min-h-screen bg-gradient-to-br from-gray-950 via-blue-950/20 to-purple-950/20">
        {/* Header */}
        <div className="sticky top-0 z-40 bg-gray-950/80 backdrop-blur-xl border-b border-white/5">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              {/* Logo/Title */}
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Shorts 2
                  </h1>
                  <p className="text-xs text-gray-500">Testing New API</p>
                </div>
              </div>

              {/* Right side */}
              <div className="flex items-center gap-4">
                {/* API Health */}
                <ApiHealthIndicator isHealthy={isApiHealthy} isLoading={isCheckingHealth} />

                {/* View mode toggle */}
                <div className="flex items-center bg-gray-900 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode("story")}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      viewMode === "story"
                        ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                        : "text-gray-400 hover:text-white"
                    }`}
                  >
                    Story View
                  </button>
                  <button
                    onClick={() => setViewMode("grid")}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      viewMode === "grid"
                        ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                        : "text-gray-400 hover:text-white"
                    }`}
                  >
                    <Grid3x3 className="w-4 h-4" />
                  </button>
                </div>

                {/* Refresh button */}
                <button
                  onClick={loadVideos}
                  disabled={isLoading}
                  className="p-2 rounded-lg hover:bg-gray-900 transition-colors disabled:opacity-50"
                  title="Refresh videos"
                >
                  <RefreshCw className={`w-5 h-5 text-gray-400 ${isLoading ? "animate-spin" : ""}`} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Stats bar */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Flame className="w-5 h-5 text-orange-500" />
                <span className="text-2xl font-bold text-white">{totalCount}</span>
                <span className="text-gray-400">Videos Generated</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">New Shorts Generator Backend</span>
              </div>
            </div>
          </div>

          {/* Error state */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-red-400 font-medium mb-1">Failed to load videos</h3>
                  <p className="text-sm text-gray-400">{error}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Make sure the shorts-generator server is running: <code>cd apps/shorts-generator && uv run uvicorn shorts_generator.main:app --port 8001 --reload</code>
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Loading state */}
          {isLoading && !error && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <Loader2 className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Loading shorts...</p>
              </div>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && !error && videos.length === 0 && (
            <div className="text-center py-20">
              <div className="w-20 h-20 rounded-full bg-gray-900 flex items-center justify-center mx-auto mb-4">
                <Film className="w-10 h-10 text-gray-600" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">No videos yet</h3>
              <p className="text-gray-400">
                Videos will appear here after generation. Use the API to generate videos from markdown content.
              </p>
            </div>
          )}

          {/* Story View */}
          {!isLoading && !error && videos.length > 0 && viewMode === "story" && (
            <div className="relative">
              {/* Left scroll button */}
              <button
                onClick={() => scrollContainer(document.getElementById(storiesContainerId), "left")}
                className="absolute left-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-gray-900/90 flex items-center justify-center text-white shadow-lg hover:bg-gray-800 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              {/* Stories container */}
              <div
                id={storiesContainerId}
                className="flex gap-4 overflow-x-auto pb-4 px-1 scrollbar-hide"
                style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
              >
                {videos.map((video, index) => (
                  <StoryCard
                    key={video.id}
                    video={video}
                    index={index}
                    onClick={() => openVideo(video)}
                  />
                ))}
              </div>

              {/* Right scroll button */}
              <button
                onClick={() => scrollContainer(document.getElementById(storiesContainerId), "right")}
                className="absolute right-0 top-1/2 -translate-y-1/2 z-10 w-10 h-10 rounded-full bg-gray-900/90 flex items-center justify-center text-white shadow-lg hover:bg-gray-800 transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* Grid View */}
          {!isLoading && !error && videos.length > 0 && viewMode === "grid" && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {videos.map((video, index) => (
                <GridCard
                  key={video.id}
                  video={video}
                  index={index}
                  onClick={() => openVideo(video)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Video Modal */}
        <VideoModal isOpen={modal.isOpen} video={modal.video} onClose={closeVideo} />
      </main>
    </Layout>
  );
}
