/**
 * AnalyticsDashboard - Analytics dashboard for shorts performance
 *
 * Features:
 * - Per-short analytics (views, likes, shares, completion rate)
 * - Aggregate analytics (total generated, total cost, top performing)
 * - CTR to full lesson tracking
 * - Engagement score calculation
 */

import React, { useState, useCallback, useEffect } from "react";
import { getShortsApiClient } from "../../../lib/shorts-api";

/**
 * Video analytics data
 */
interface VideoAnalytics {
  video_id: string;
  lesson_path: string;
  title: string;
  duration_seconds: number;
  view_count: number;
  unique_viewers: number;
  like_count: number;
  comment_count: number;
  avg_watch_duration_seconds: number;
  completion_rate: number;
  engagement_score: number;
  generation_cost_usd: number;
}

/**
 * Aggregate analytics data
 */
interface AggregateAnalytics {
  total_generated: number;
  total_cost_usd: number;
  avg_cost_per_video_usd: number;
  total_likes: number;
  total_comments: number;
  total_views: number;
  total_engagement: number;
}

/**
 * Top performing video data
 */
interface TopPerformingVideo {
  video_id: string;
  title: string;
  lesson_path: string;
  metric_count: number;
  like_count: number;
  comment_count: number;
  view_count: number;
}

/**
 * Props for AnalyticsDashboard
 */
interface AnalyticsDashboardProps {
  /** Auto-refresh interval in milliseconds */
  refreshInterval?: number;
}

/**
 * Main analytics dashboard component
 */
export function AnalyticsDashboard({
  refreshInterval = 30000, // 30 seconds
}: AnalyticsDashboardProps) {
  const [aggregate, setAggregate] = useState<AggregateAnalytics | null>(null);
  const [topVideos, setTopVideos] = useState<TopPerformingVideo[]>([]);
  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null);
  const [selectedVideoAnalytics, setSelectedVideoAnalytics] =
    useState<VideoAnalytics | null>(null);
  const [sortBy, setSortBy] = useState<"views" | "likes" | "engagement">(
    "engagement"
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const apiClient = getShortsApiClient();

  // Load aggregate analytics
  const loadAggregate = useCallback(async () => {
    try {
      const data = await apiClient.getAggregateAnalytics();
      setAggregate(data);
    } catch (err: any) {
      setError(err.message || "Failed to load aggregate analytics");
    }
  }, [apiClient]);

  // Load top performing videos
  const loadTopVideos = useCallback(async () => {
    try {
      const data = await apiClient.getTopPerforming({
        limit: 10,
        sortBy,
      });
      setTopVideos(data.videos);
    } catch (err: any) {
      setError(err.message || "Failed to load top videos");
    }
  }, [apiClient, sortBy]);

  // Load video analytics
  const loadVideoAnalytics = useCallback(
    async (videoId: string) => {
      try {
        const data = await apiClient.getVideoAnalytics(videoId);
        setSelectedVideoAnalytics(data);
      } catch (err: any) {
        setError(err.message || "Failed to load video analytics");
      }
    },
    [apiClient]
  );

  // Initial load
  useEffect(() => {
    setLoading(true);
    Promise.all([loadAggregate(), loadTopVideos()]).finally(() => {
      setLoading(false);
    });
  }, [loadAggregate, loadTopVideos]);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      loadAggregate();
      loadTopVideos();
      if (selectedVideoId) {
        loadVideoAnalytics(selectedVideoId);
      }
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [
    loadAggregate,
    loadTopVideos,
    loadVideoAnalytics,
    selectedVideoId,
    refreshInterval,
  ]);

  // Handle video selection
  const handleVideoClick = (videoId: string) => {
    setSelectedVideoId(videoId);
    loadVideoAnalytics(videoId);
  };

  // Format duration
  function formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }

  // Calculate ROI (engagement per dollar)
  function calculateROI(analytics: VideoAnalytics): number {
    if (analytics.generation_cost_usd <= 0) return 0;
    return (
      (analytics.view_count + analytics.like_count * 10) /
      analytics.generation_cost_usd
    );
  }

  if (loading && !aggregate) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-700 border-t-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-white">
            Shorts Analytics Dashboard
          </h1>
          <p className="text-gray-400">
            Track performance and engagement metrics for lesson shorts
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-500 bg-red-500/10 p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Aggregate Statistics */}
        {aggregate && (
          <div className="mb-8">
            <h2 className="mb-4 text-xl font-semibold text-white">
              Aggregate Statistics
            </h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {/* Total Generated */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
                <div className="mb-2 text-sm text-gray-400">Total Generated</div>
                <div className="text-3xl font-bold text-white">
                  {aggregate.total_generated}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Shorts created
                </div>
              </div>

              {/* Total Cost */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
                <div className="mb-2 text-sm text-gray-400">Total Cost</div>
                <div className="text-3xl font-bold text-white">
                  ${aggregate.total_cost_usd.toFixed(2)}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  ${aggregate.avg_cost_per_video_usd.toFixed(4)}/video avg
                </div>
              </div>

              {/* Total Engagement */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
                <div className="mb-2 text-sm text-gray-400">
                  Total Engagement
                </div>
                <div className="text-3xl font-bold text-white">
                  {aggregate.total_engagement.toLocaleString()}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  {aggregate.total_views} views +{" "}
                  {aggregate.total_likes} likes +{" "}
                  {aggregate.total_comments} comments
                </div>
              </div>

              {/* Engagement per Dollar */}
              <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
                <div className="mb-2 text-sm text-gray-400">
                  Engagement per Dollar
                </div>
                <div className="text-3xl font-bold text-green-400">
                  {aggregate.total_cost_usd > 0
                    ? (
                        aggregate.total_engagement / aggregate.total_cost_usd
                      ).toFixed(0)
                    : "0"}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  ROI metric
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Top Performing Videos */}
        <div className="mb-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Top Performing Videos
            </h2>
            <div className="flex gap-2">
              <button
                onClick={() => setSortBy("engagement")}
                className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                  sortBy === "engagement"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                Engagement
              </button>
              <button
                onClick={() => setSortBy("views")}
                className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                  sortBy === "views"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                Views
              </button>
              <button
                onClick={() => setSortBy("likes")}
                className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                  sortBy === "likes"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-800 text-gray-300 hover:bg-gray-700"
                }`}
              >
                Likes
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {topVideos.map((video, index) => (
              <button
                key={video.video_id}
                onClick={() => handleVideoClick(video.video_id)}
                className={`rounded-lg border bg-gray-900 p-4 text-left transition-all hover:border-blue-500 ${
                  selectedVideoId === video.video_id
                    ? "border-blue-500 ring-2 ring-blue-500/20"
                    : "border-gray-800"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <span className="rounded-full bg-blue-500/20 px-2 py-0.5 text-xs font-medium text-blue-400">
                        #{index + 1}
                      </span>
                      <span className="text-xs text-gray-500">
                        {video.lesson_path.split("/").slice(-2).join("/")}
                      </span>
                    </div>
                    <h3 className="mb-2 text-sm font-medium text-white">
                      {video.title}
                    </h3>
                    <div className="flex flex-wrap gap-4 text-xs text-gray-400">
                      <span>👁️ {video.view_count} views</span>
                      <span>👍 {video.like_count} likes</span>
                      <span>💬 {video.comment_count} comments</span>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-blue-400">
                    {video.metric_count.toLocaleString()}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {topVideos.length === 0 && !loading && (
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-12 text-center text-gray-500">
              No analytics data available yet
            </div>
          )}
        </div>

        {/* Video Details Panel */}
        {selectedVideoAnalytics && (
          <div className="mb-8 rounded-lg border border-gray-800 bg-gray-900 p-6">
            <h2 className="mb-6 text-xl font-semibold text-white">
              Video Details: {selectedVideoAnalytics.title}
            </h2>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {/* Views */}
              <div>
                <div className="text-sm text-gray-400">Views</div>
                <div className="text-2xl font-bold text-white">
                  {selectedVideoAnalytics.view_count.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">
                  {selectedVideoAnalytics.unique_viewers} unique
                </div>
              </div>

              {/* Likes */}
              <div>
                <div className="text-sm text-gray-400">Likes</div>
                <div className="text-2xl font-bold text-green-400">
                  {selectedVideoAnalytics.like_count.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">
                  {selectedVideoAnalytics.view_count > 0
                    ? (
                        (selectedVideoAnalytics.like_count /
                          selectedVideoAnalytics.view_count) *
                        100
                      ).toFixed(1)
                    : 0}
                  % like rate
                </div>
              </div>

              {/* Comments */}
              <div>
                <div className="text-sm text-gray-400">Comments</div>
                <div className="text-2xl font-bold text-blue-400">
                  {selectedVideoAnalytics.comment_count.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500">
                  {selectedVideoAnalytics.view_count > 0
                    ? (
                        (selectedVideoAnalytics.comment_count /
                          selectedVideoAnalytics.view_count) *
                        100
                      ).toFixed(1)
                    : 0}
                  % comment rate
                </div>
              </div>

              {/* Engagement Score */}
              <div>
                <div className="text-sm text-gray-400">Engagement Score</div>
                <div
                  className={`text-2xl font-bold ${
                    selectedVideoAnalytics.engagement_score >= 20
                      ? "text-green-400"
                      : selectedVideoAnalytics.engagement_score >= 10
                      ? "text-yellow-400"
                      : "text-red-400"
                  }`}
                >
                  {selectedVideoAnalytics.engagement_score.toFixed(1)}
                </div>
                <div className="text-xs text-gray-500">
                  (likes + comments) / views × 100
                </div>
              </div>

              {/* Duration */}
              <div>
                <div className="text-sm text-gray-400">Duration</div>
                <div className="text-2xl font-bold text-white">
                  {formatDuration(selectedVideoAnalytics.duration_seconds)}
                </div>
              </div>

              {/* Avg Watch Duration */}
              <div>
                <div className="text-sm text-gray-400">
                  Avg Watch Duration
                </div>
                <div className="text-2xl font-bold text-white">
                  {formatDuration(
                    Math.round(selectedVideoAnalytics.avg_watch_duration_seconds)
                  )}
                </div>
              </div>

              {/* Completion Rate */}
              <div>
                <div className="text-sm text-gray-400">Completion Rate</div>
                <div
                  className={`text-2xl font-bold ${
                    selectedVideoAnalytics.completion_rate >= 70
                      ? "text-green-400"
                      : selectedVideoAnalytics.completion_rate >= 40
                      ? "text-yellow-400"
                      : "text-red-400"
                  }`}
                >
                  {selectedVideoAnalytics.completion_rate.toFixed(1)}%
                </div>
              </div>

              {/* Generation Cost */}
              <div>
                <div className="text-sm text-gray-400">Generation Cost</div>
                <div className="text-2xl font-bold text-white">
                  ${selectedVideoAnalytics.generation_cost_usd.toFixed(4)}
                </div>
                <div className="text-xs text-gray-500">
                  ROI: {calculateROI(selectedVideoAnalytics).toFixed(0)}
                </div>
              </div>
            </div>

            {/* Lesson Path */}
            <div className="mt-6 rounded-lg bg-gray-950 p-3">
              <div className="text-xs text-gray-500">Source Lesson</div>
              <div className="text-sm text-gray-300">
                {selectedVideoAnalytics.lesson_path}
              </div>
            </div>
          </div>
        )}

        {/* CTR Tracking Note */}
        <div className="rounded-lg border border-yellow-500/50 bg-yellow-500/10 p-6">
          <h3 className="mb-2 text-lg font-semibold text-yellow-400">
            Click-Through Rate (CTR) Tracking
          </h3>
          <p className="text-sm text-gray-400">
            CTR tracking from shorts to full lessons requires integration with
            the lesson page. Track clicks on the "View Lesson" button and
            correlate with video views to measure conversion rates.
          </p>
          <div className="mt-4 text-xs text-gray-500">
            <p>Potential implementation:</p>
            <ul className="ml-4 mt-2 list-disc space-y-1">
              <li>Add tracking pixel/event on "View Lesson" button click</li>
              <li>Store click events in ShortAnalytics table</li>
              <li>Calculate CTR = (lesson_page_views / short_views) × 100</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Compact version for embedding in other pages
 */
export function AnalyticsDashboardMini() {
  const [aggregate, setAggregate] = useState<AggregateAnalytics | null>(null);
  const apiClient = getShortsApiClient();

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await apiClient.getAggregateAnalytics();
        setAggregate(data);
      } catch (err) {
        console.warn("Failed to load analytics:", err);
      }
    };
    loadStats();
    const interval = setInterval(loadStats, 60000); // 1 minute
    return () => clearInterval(interval);
  }, [apiClient]);

  if (!aggregate) {
    return <div className="text-sm text-gray-500">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4 rounded-lg border border-gray-800 bg-gray-900 p-4">
      <div>
        <div className="text-xs text-gray-400">Total Views</div>
        <div className="text-lg font-semibold text-white">
          {aggregate.total_views.toLocaleString()}
        </div>
      </div>
      <div className="h-8 w-px bg-gray-800" />
      <div>
        <div className="text-xs text-gray-400">Avg Engagement</div>
        <div className="text-lg font-semibold text-white">
          {aggregate.total_generated > 0
            ? (
                aggregate.total_engagement / aggregate.total_generated
              ).toFixed(0)
            : "0"}
        </div>
      </div>
      <div className="h-8 w-px bg-gray-800" />
      <div>
        <div className="text-xs text-gray-400">Total Cost</div>
        <div className="text-lg font-semibold text-white">
          ${aggregate.total_cost_usd.toFixed(2)}
        </div>
      </div>
    </div>
  );
}
