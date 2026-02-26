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
import { Eye, Heart, MessageCircle, TrendingUp, DollarSign, BarChart3, Video, Loader2, Lightbulb } from "lucide-react";

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
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      {/* Aggregate Statistics */}
      {aggregate && (
        <div>
          <div className="mb-4 flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <BarChart3 className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold text-foreground">
              Aggregate Statistics
            </h2>
          </div>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Total Generated */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="mb-2 flex items-center gap-2 text-muted-foreground">
                <Video className="h-4 w-4" />
                <span className="text-sm">Total Generated</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                {aggregate.total_generated}
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                Shorts created
              </div>
            </div>

            {/* Total Cost */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="mb-2 flex items-center gap-2 text-muted-foreground">
                <DollarSign className="h-4 w-4" />
                <span className="text-sm">Total Cost</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                ${aggregate.total_cost_usd.toFixed(2)}
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                ${aggregate.avg_cost_per_video_usd.toFixed(4)}/video avg
              </div>
            </div>

            {/* Total Engagement */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="mb-2 flex items-center gap-2 text-muted-foreground">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm">Total Engagement</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                {aggregate.total_engagement.toLocaleString()}
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                {aggregate.total_views} views +{" "}
                {aggregate.total_likes} likes +{" "}
                {aggregate.total_comments} comments
              </div>
            </div>

            {/* Engagement per Dollar */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="mb-2 flex items-center gap-2 text-muted-foreground">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm">Engagement per Dollar</span>
              </div>
              <div className="text-3xl font-bold text-success">
                {aggregate.total_cost_usd > 0
                  ? (
                      aggregate.total_engagement / aggregate.total_cost_usd
                    ).toFixed(0)
                  : "0"}
              </div>
              <div className="mt-2 text-xs text-muted-foreground">
                ROI metric
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Performing Videos */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground">
            Top Performing Videos
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => setSortBy("engagement")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                sortBy === "engagement"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              Engagement
            </button>
            <button
              onClick={() => setSortBy("views")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                sortBy === "views"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              Views
            </button>
            <button
              onClick={() => setSortBy("likes")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                sortBy === "likes"
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
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
              className={`rounded-lg border bg-card p-4 text-left transition-all hover:border-primary ${
                selectedVideoId === video.video_id
                  ? "border-primary ring-2 ring-primary/20"
                  : "border-border"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                      #{index + 1}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {video.lesson_path.split("/").slice(-2).join("/")}
                    </span>
                  </div>
                  <h3 className="mb-2 text-sm font-medium text-foreground">
                    {video.title}
                  </h3>
                  <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Eye className="h-3 w-3" />
                      {video.view_count} views
                    </span>
                    <span className="flex items-center gap-1">
                      <Heart className="h-3 w-3" />
                      {video.like_count} likes
                    </span>
                    <span className="flex items-center gap-1">
                      <MessageCircle className="h-3 w-3" />
                      {video.comment_count} comments
                    </span>
                  </div>
                </div>
                <div className="text-2xl font-bold text-primary">
                  {video.metric_count.toLocaleString()}
                </div>
              </div>
            </button>
          ))}
        </div>

        {topVideos.length === 0 && !loading && (
          <div className="rounded-lg border border-border bg-card p-12 text-center text-muted-foreground">
            No analytics data available yet
          </div>
        )}
      </div>

      {/* Video Details Panel */}
      {selectedVideoAnalytics && (
        <div className="rounded-lg border border-border bg-card p-6">
          <h2 className="mb-6 text-xl font-semibold text-foreground">
            Video Details: {selectedVideoAnalytics.title}
          </h2>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {/* Views */}
            <div>
              <div className="text-sm text-muted-foreground">Views</div>
              <div className="text-2xl font-bold text-foreground">
                {selectedVideoAnalytics.view_count.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
                {selectedVideoAnalytics.unique_viewers} unique
              </div>
            </div>

            {/* Likes */}
            <div>
              <div className="text-sm text-muted-foreground">Likes</div>
              <div className="text-2xl font-bold text-success">
                {selectedVideoAnalytics.like_count.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
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
              <div className="text-sm text-muted-foreground">Comments</div>
              <div className="text-2xl font-bold text-primary">
                {selectedVideoAnalytics.comment_count.toLocaleString()}
              </div>
              <div className="text-xs text-muted-foreground">
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
              <div className="text-sm text-muted-foreground">Engagement Score</div>
              <div
                className={`text-2xl font-bold ${
                  selectedVideoAnalytics.engagement_score >= 20
                    ? "text-success"
                    : selectedVideoAnalytics.engagement_score >= 10
                    ? "text-warning"
                    : "text-destructive"
                }`}
              >
                {selectedVideoAnalytics.engagement_score.toFixed(1)}
              </div>
              <div className="text-xs text-muted-foreground">
                (likes + comments) / views × 100
              </div>
            </div>

            {/* Duration */}
            <div>
              <div className="text-sm text-muted-foreground">Duration</div>
              <div className="text-2xl font-bold text-foreground">
                {formatDuration(selectedVideoAnalytics.duration_seconds)}
              </div>
            </div>

            {/* Avg Watch Duration */}
            <div>
              <div className="text-sm text-muted-foreground">
                Avg Watch Duration
              </div>
              <div className="text-2xl font-bold text-foreground">
                {formatDuration(
                  Math.round(selectedVideoAnalytics.avg_watch_duration_seconds)
                )}
              </div>
            </div>

            {/* Completion Rate */}
            <div>
              <div className="text-sm text-muted-foreground">Completion Rate</div>
              <div
                className={`text-2xl font-bold ${
                  selectedVideoAnalytics.completion_rate >= 70
                    ? "text-success"
                    : selectedVideoAnalytics.completion_rate >= 40
                    ? "text-warning"
                    : "text-destructive"
                }`}
              >
                {selectedVideoAnalytics.completion_rate.toFixed(1)}%
              </div>
            </div>

            {/* Generation Cost */}
            <div>
              <div className="text-sm text-muted-foreground">Generation Cost</div>
              <div className="text-2xl font-bold text-foreground">
                ${selectedVideoAnalytics.generation_cost_usd.toFixed(4)}
              </div>
              <div className="text-xs text-muted-foreground">
                ROI: {calculateROI(selectedVideoAnalytics).toFixed(0)}
              </div>
            </div>
          </div>

          {/* Lesson Path */}
          <div className="mt-6 rounded-lg bg-muted p-3">
            <div className="text-xs text-muted-foreground">Source Lesson</div>
            <div className="text-sm text-foreground">
              {selectedVideoAnalytics.lesson_path}
            </div>
          </div>
        </div>
      )}

      {/* CTR Tracking Note */}
      <div className="rounded-lg border border-warning/50 bg-warning/10 p-6">
        <div className="flex items-start gap-3">
          <Lightbulb className="h-5 w-5 text-warning mt-0.5" />
          <div className="flex-1">
            <h3 className="mb-2 text-lg font-semibold text-warning">
              Click-Through Rate (CTR) Tracking
            </h3>
            <p className="text-sm text-muted-foreground">
              CTR tracking from shorts to full lessons requires integration with
              the lesson page. Track clicks on the "View Lesson" button and
              correlate with video views to measure conversion rates.
            </p>
            <div className="mt-4 text-xs text-muted-foreground">
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
    return <div className="text-sm text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-4">
      <div>
        <div className="text-xs text-muted-foreground">Total Views</div>
        <div className="text-lg font-semibold text-foreground">
          {aggregate.total_views.toLocaleString()}
        </div>
      </div>
      <div className="h-8 w-px bg-border" />
      <div>
        <div className="text-xs text-muted-foreground">Avg Engagement</div>
        <div className="text-lg font-semibold text-foreground">
          {aggregate.total_generated > 0
            ? (
                aggregate.total_engagement / aggregate.total_generated
              ).toFixed(0)
            : "0"}
        </div>
      </div>
      <div className="h-8 w-px bg-border" />
      <div>
        <div className="text-xs text-muted-foreground">Total Cost</div>
        <div className="text-lg font-semibold text-foreground">
          ${aggregate.total_cost_usd.toFixed(2)}
        </div>
      </div>
    </div>
  );
}
