/**
 * Shorts API Client
 *
 * TypeScript client for the Lesson Shorts Generator API.
 * Provides methods for:
 * - Fetching shorts feed with filters
 * - Getting single video metadata
 * - Engagement actions (like, comment, share)
 * - Progress tracking
 */

import type { ShortVideo, ShortsFilters } from "../components/shorts/types";

// API base URL (configure based on environment)
// This is a default - the actual URL should be fetched from Docusaurus config
// using getShortsApiBaseUrl() when possible
const getDefaultApiBaseUrl = () => {
  // Check for environment variable (server-side or build-time)
  if (typeof process !== "undefined" && process.env?.SHORTS_API_URL) {
    return process.env.SHORTS_API_URL + "/api/v1";
  }
  // Default fallback (should be overridden by components)
  return "http://localhost:8004/api/v1";
};

const DEFAULT_API_BASE_URL = getDefaultApiBaseUrl();

/**
 * Get the Shorts API base URL from Docusaurus config or environment
 * Call this from React components to get the configured URL
 */
export function getShortsApiBaseUrl(): string {
  // Try to read from injected global (set by client scripts)
  if (typeof window !== "undefined" && (window as any).__SHORTS_API_URL__) {
    return (window as any).__SHORTS_API_URL__ + "/api/v1";
  }
  // Fall back to default
  return DEFAULT_API_BASE_URL;
}

/**
 * API error class
 */
export class ShortsApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = "ShortsApiError";
  }
}

/**
 * Shorts API response wrapper
 */
interface ApiResponse<T> {
  data: T;
  error?: string;
  message?: string;
}

/**
 * Paginated response wrapper
 */
interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/**
 * Video metadata from API
 */
interface VideoMetadataResponse {
  video_id: string;
  lesson_path: string;
  title: string;
  duration_seconds: number;
  video_url: string;
  thumbnail_url: string;
  created_at: string;
  generation_cost: number;
  view_count?: number;
  like_count?: number;
  comment_count?: number;
}

/**
 * Job status from API
 */
interface JobStatusResponse {
  job_id: string;
  lesson_path: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  error_message?: string;
  retry_count: number;
  created_at: string;
  completed_at?: string;
  video_id?: string;
}

/**
 * Engagement request payload
 */
interface EngagementRequest {
  action: "like" | "unlike" | "share";
  video_id: string;
}

/**
 * Comment request payload
 */
interface CommentRequest {
  video_id: string;
  text: string;
  parent_id?: string;
}

/**
 * View tracking request
 */
interface ViewTrackingRequest {
  video_id: string;
  watch_duration_seconds: number;
  completed: boolean;
}

/**
 * Transform API response to ShortVideo
 */
function transformVideoMetadata(data: VideoMetadataResponse): ShortVideo {
  return {
    id: data.video_id,
    lessonPath: data.lesson_path,
    title: data.title,
    durationSeconds: data.duration_seconds,
    videoUrl: data.video_url,
    thumbnailUrl: data.thumbnail_url,
    viewCount: data.view_count,
    likeCount: data.like_count,
    commentCount: data.comment_count,
    generationCost: data.generation_cost,
  };
}

/**
 * Shorts API Client
 */
export class ShortsApiClient {
  private baseUrl: string;
  private apiKey: string | null;

  constructor(baseUrl: string = DEFAULT_API_BASE_URL, apiKey: string | null = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  /**
   * Make API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.apiKey) {
      headers["Authorization"] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: response.statusText };
      }
      throw new ShortsApiError(
        errorData.detail || errorData.message || "API request failed",
        response.status,
        errorData
      );
    }

    return response.json();
  }

  /**
   * Get health check
   */
  async healthCheck(): Promise<{
    status: string;
    service: string;
    version: string;
    dependencies: Record<string, string>;
  }> {
    return this.request("/health");
  }

  /**
   * Get list of shorts videos with optional filters
   */
  async getVideos(filters: ShortsFilters = {}): Promise<{
    shorts: ShortVideo[];
    totalCount: number;
    hasMore: boolean;
  }> {
    const params = new URLSearchParams();

    if (filters.part) {
      params.set("part", filters.part);
    }
    if (filters.chapter) {
      params.set("chapter", filters.chapter);
    }
    if (filters.search) {
      params.set("search", filters.search);
    }

    // Default pagination
    if (!filters.limit) {
      params.set("limit", "50");
    } else {
      params.set("limit", filters.limit.toString());
    }

    if (filters.offset) {
      params.set("offset", filters.offset.toString());
    }

    const query = params.toString();
    const url = `/videos${query ? `?${query}` : ""}`;

    const data: VideoMetadataResponse[] = await this.request(url);

    const shorts = data.map(transformVideoMetadata);

    return {
      shorts,
      totalCount: shorts.length, // API doesn't return total count yet
      hasMore: shorts.length === (filters.limit || 50),
    };
  }

  /**
   * Get single video by ID
   */
  async getVideo(videoId: string): Promise<ShortVideo> {
    const data: VideoMetadataResponse = await this.request(`/videos/${videoId}`);
    return transformVideoMetadata(data);
  }

  /**
   * Get job status by ID
   */
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    return this.request(`/status/${jobId}`);
  }

  /**
   * List all jobs with optional filter
   */
  async listJobs(options: {
    status?: "queued" | "processing" | "completed" | "failed";
    page?: number;
    pageSize?: number;
  } = {}): Promise<{
    jobs: JobStatusResponse[];
    totalCount: number;
    page: number;
    pageSize: number;
  }> {
    const params = new URLSearchParams();

    if (options.status) {
      params.set("status_filter", options.status);
    }

    params.set("page", (options.page || 1).toString());
    params.set("page_size", (options.pageSize || 50).toString());

    const query = params.toString();
    const data = await this.request(`/jobs${query ? `?${query}` : ""}`);

    return data;
  }

  /**
   * Generate a short video
   */
  async generateShort(request: {
    lessonPath: string;
    targetDuration?: number;
    voice?: string;
  }): Promise<{
    jobId: string;
    status: string;
    message: string;
  }> {
    return this.request("/generate", {
      method: "POST",
      body: JSON.stringify({
        lesson_path: request.lessonPath,
        target_duration: request.targetDuration || 60,
        voice: request.voice || "en-US-AriaNeural",
      }),
    });
  }

  /**
   * Batch generate shorts
   */
  async batchGenerate(request: {
    lessonPaths: string[];
    targetDuration?: number;
    voice?: string;
    priority?: "high" | "normal" | "low";
  }): Promise<{
    batchId: string;
    jobCount: number;
    status: string;
    message: string;
  }> {
    return this.request("/batch", {
      method: "POST",
      body: JSON.stringify({
        lesson_paths: request.lessonPaths,
        target_duration: request.targetDuration || 60,
        voice: request.voice || "en-US-AriaNeural",
        priority: request.priority || "normal",
      }),
    });
  }

  /**
   * Like a video
   */
  async likeVideo(videoId: string): Promise<void> {
    await this.request(`/videos/${videoId}/like`, {
      method: "POST",
    });
  }

  /**
   * Unlike a video
   */
  async unlikeVideo(videoId: string): Promise<void> {
    await this.request(`/videos/${videoId}/unlike`, {
      method: "POST",
    });
  }

  /**
   * Comment on a video
   */
  async commentOnVideo(request: {
    videoId: string;
    text: string;
    parentId?: string;
  }): Promise<{
    commentId: string;
    text: string;
    createdAt: string;
  }> {
    return this.request(`/videos/${request.videoId}/comments`, {
      method: "POST",
      body: JSON.stringify({
        text: request.text,
        parent_id: request.parentId,
      }),
    });
  }

  /**
   * Get comments for a video
   */
  async getComments(
    videoId: string,
    options: {
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<{
    comments: Array<{
      id: string;
      userId: string;
      videoId: string;
      text: string;
      parentId?: string;
      createdAt: string;
      replies?: any[];
    }>;
    totalCount: number;
  }> {
    const params = new URLSearchParams();

    if (options.limit) {
      params.set("limit", options.limit.toString());
    }
    if (options.offset) {
      params.set("offset", options.offset.toString());
    }

    const query = params.toString();
    return this.request(`/videos/${videoId}/comments${query ? `?${query}` : ""}`);
  }

  /**
   * Record video view
   */
  async recordView(request: {
    videoId: string;
    watchDurationSeconds: number;
    completed: boolean;
  }): Promise<void> {
    await this.request(`/videos/${request.videoId}/views`, {
      method: "POST",
      body: JSON.stringify({
        watch_duration_seconds: request.watchDurationSeconds,
        completed: request.completed,
      }),
    });
  }

  /**
   * Retry a failed job
   */
  async retryJob(jobId: string): Promise<JobStatusResponse> {
    return this.request(`/jobs/${jobId}/retry`, {
      method: "POST",
    });
  }

  /**
   * Get storage statistics
   */
  async getStorageStats(): Promise<{
    videos: { count: number; total_bytes: number };
    thumbnails: { count: number; total_bytes: number };
    captions: { count: number; total_bytes: number };
    total: {
      count: number;
      total_bytes: number;
      total_gb: number;
      estimated_monthly_cost_usd: number;
    };
  }> {
    return this.request("/storage/stats");
  }

  /**
   * Delete video files from storage
   */
  async deleteVideoFiles(videoId: string): Promise<{
    videoId: string;
    deletedCount: number;
    totalCount: number;
    results: {
      video: boolean;
      thumbnail: boolean;
      captions: boolean;
    };
  }> {
    return this.request(`/storage/videos/${videoId}`, {
      method: "DELETE",
    });
  }

  /**
   * Estimate batch cost
   */
  async estimateBatchCost(request: {
    lessonCount: number;
    targetDuration?: number;
  }): Promise<{
    lessonCount: number;
    costPerVideoUsd: number;
    totalCostUsd: number;
    breakdown: {
      scriptGenerationUsd: number;
      visualGenerationUsd: number;
      audioGenerationUsd: number;
      storageUsd: number;
    };
  }> {
    const params = new URLSearchParams({
      lesson_count: request.lessonCount.toString(),
      target_duration: (request.targetDuration || 60).toString(),
    });

    return this.request(`/batch/estimate-cost?${params.toString()}`);
  }

  /**
   * Get aggregate analytics
   */
  async getAggregateAnalytics(): Promise<{
    total_generated: number;
    total_cost_usd: number;
    avg_cost_per_video_usd: number;
    total_likes: number;
    total_comments: number;
    total_views: number;
    total_engagement: number;
  }> {
    return this.request("/analytics/aggregate");
  }

  /**
   * Get video analytics
   */
  async getVideoAnalytics(videoId: string): Promise<{
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
  }> {
    return this.request(`/analytics/videos/${videoId}`);
  }

  /**
   * Get top performing videos
   */
  async getTopPerforming(options: {
    limit?: number;
    sortBy?: "views" | "likes" | "engagement";
  } = {}): Promise<{
    sort_by: string;
    videos: Array<{
      video_id: string;
      title: string;
      lesson_path: string;
      metric_count: number;
      like_count: number;
      comment_count: number;
      view_count: number;
    }>;
  }> {
    const params = new URLSearchParams();
    if (options.limit) params.set("limit", options.limit.toString());
    if (options.sortBy) params.set("sort_by", options.sortBy);

    const query = params.toString();
    return this.request(`/analytics/top-performing${query ? `?${query}` : ""}`);
  }

  /**
   * Get CTR to lesson
   */
  async getCTRTOLesson(): Promise<{
    message: string;
    implementation_notes: string;
    placeholder_ctr: number;
  }> {
    return this.request("/analytics/ctr-to-lesson");
  }

  /**
   * Get personalized "For You" recommendations
   */
  async getForYouRecommendations(request: {
    userId?: string;
    limit?: number;
    currentLessonPath?: string;
    excludeWatched?: boolean;
    weakerAreas?: string[];
  }): Promise<{
    user_id: string;
    videos: Array<{
      video_id: string;
      title: string;
      lesson_path: string;
      duration_seconds: number;
      thumbnail_url: string;
      video_url: string;
      view_count: number;
      like_count: number;
    }>;
    count: number;
  }> {
    return this.request("/recommendations/for-you", {
      method: "POST",
      body: JSON.stringify({
        user_id: request.userId,
        limit: request.limit || 10,
        current_lesson_path: request.currentLessonPath,
        exclude_watched: request.excludeWatched !== false,
        weaker_areas: request.weakerAreas || [],
      }),
    });
  }

  /**
   * Get continue watching list
   */
  async getContinueWatching(request: {
    userId: string;
    limit?: number;
  }): Promise<{
    user_id: string;
    videos: Array<{
      video_id: string;
      title: string;
      lesson_path: string;
      duration_seconds: number;
      thumbnail_url: string;
      video_url: string;
    }>;
    count: number;
  }> {
    return this.request("/recommendations/continue-watching", {
      method: "POST",
      body: JSON.stringify({
        user_id: request.userId,
        limit: request.limit || 5,
      }),
    });
  }

  /**
   * Get trending shorts
   */
  async getTrending(options: {
    limit?: number;
  } = {}): Promise<{
    videos: Array<{
      video_id: string;
      title: string;
      lesson_path: string;
      duration_seconds: number;
      thumbnail_url: string;
      video_url: string;
      generation_cost_usd: number;
    }>;
    count: number;
  }> {
    const params = new URLSearchParams();
    if (options.limit) params.set("limit", options.limit.toString());

    const query = params.toString();
    return this.request(`/recommendations/trending${query ? `?${query}` : ""}`);
  }

  /**
   * Get daily cost breakdown
   */
  async getDailyCost(date?: string): Promise<{
    date: string;
    total_cost_usd: number;
    job_count: number;
    video_count: number;
    avg_cost_per_video: number;
    breakdown: {
      script_generation: number;
      visual_generation: number;
      audio_generation: number;
      video_assembly: number;
    };
    alert_threshold: number;
    alert_exceeded: boolean;
  }> {
    const query = date ? `?date=${date}` : "";
    return this.request(`/cost/daily${query}`);
  }

  /**
   * Get monthly cost breakdown
   */
  async getMonthlyCost(options?: {
    year?: number;
    month?: number;
  }): Promise<{
    year: number;
    month: number;
    total_cost_usd: number;
    job_count: number;
    video_count: number;
    avg_cost_per_video: number;
    breakdown: {
      script_generation: number;
      visual_generation: number;
      audio_generation: number;
      video_assembly: number;
    };
    alert_threshold: number;
    alert_exceeded: boolean;
    projected_monthly: {
      projected_usd: number;
      method: string;
      days_so_far: number;
      days_remaining: number;
      daily_average: number;
    };
  }> {
    const params = new URLSearchParams();
    if (options?.year) params.set("year", options.year.toString());
    if (options?.month) params.set("month", options.month.toString());

    const query = params.toString();
    return this.request(`/cost/monthly${query ? `?${query}` : ""}`);
  }

  /**
   * Get job cost breakdown
   */
  async getJobCostBreakdown(jobId: string): Promise<{
    job_id: string;
    lesson_path: string;
    status: string;
    created_at: string;
    completed_at: string | null;
    total_cost_usd: number;
    breakdown: {
      script_generation: number;
      visual_generation: number;
      audio_generation: number;
      video_assembly: number;
    };
    retry_count: number;
  }> {
    return this.request(`/cost/job/${jobId}`);
  }

  /**
   * Get cache hit rate statistics
   */
  async getCacheStats(days?: number): Promise<{
    message: string;
    implementation_notes: string;
    placeholder_data?: {
      lookups: number;
      hits: number;
      misses: number;
      hit_rate_percent: number;
      days_analyzed: number;
    };
  }> {
    const query = days ? `?days=${days}` : "";
    return this.request(`/cost/cache-stats${query}`);
  }

  /**
   * Get API usage by service
   */
  async getAPIUsage(days?: number): Promise<{
    period_days: number;
    since: string;
    services: {
      gemini_script: {
        calls: number;
        cost_per_call_usd: number;
        total_cost_usd: number;
      };
      flux_images: {
        calls: number;
        cost_per_call_usd: number;
        total_cost_usd: number;
      };
      edge_tts: {
        calls: number;
        cost_per_call_usd: number;
        total_cost_usd: number;
      };
    };
  }> {
    const query = days ? `?days=${days}` : "";
    return this.request(`/cost/api-usage${query}`);
  }

  /**
   * Check budget alerts
   */
  async checkBudgetAlerts(): Promise<{
    alerts: Array<{
      severity: "warning" | "critical";
      type: string;
      threshold: number;
      actual: number;
      message: string;
      date?: string;
      year?: number;
      month?: number;
    }>;
    alert_count: number;
    has_critical: boolean;
    has_warning: boolean;
  }> {
    return this.request("/cost/alerts");
  }

  /**
   * Get cost summary
   */
  async getCostSummary(): Promise<{
    today: {
      cost_usd: number;
      video_count: number;
      alert_exceeded: boolean;
    };
    this_month: {
      cost_usd: number;
      video_count: number;
      alert_exceeded: boolean;
      projected_usd: number;
    };
    all_time: {
      total_videos: number;
      total_cost_usd: number;
      avg_cost_per_video: number;
    };
  }> {
    return this.request("/cost/summary");
  }

  /**
   * Update automation settings
   */
  async updateAutomationSettings(settings: {
    enabled: boolean;
    scheduleTime: string;
    timezone: string;
    batchLimit: number;
    targetDuration: number;
    autoRetry: boolean;
    retryAttempts: number;
    notifyOnComplete: boolean;
    selectedParts: string[];
  }): Promise<{
    success: boolean;
    message: string;
    settings?: Record<string, unknown>;
  }> {
    return this.request("/automation/settings", {
      method: "POST",
      body: JSON.stringify({
        enabled: settings.enabled,
        schedule_time: settings.scheduleTime,
        timezone: settings.timezone,
        batch_limit: settings.batchLimit,
        target_duration: settings.targetDuration,
        auto_retry: settings.autoRetry,
        retry_attempts: settings.retryAttempts,
        notify_on_complete: settings.notifyOnComplete,
        selected_parts: settings.selectedParts,
      }),
    });
  }

  /**
   * Get automation settings
   */
  async getAutomationSettings(): Promise<{
    enabled: boolean;
    scheduleTime: string;
    timezone: string;
    batchLimit: number;
    targetDuration: number;
    autoRetry: boolean;
    retryAttempts: number;
    notifyOnComplete: boolean;
    selectedParts: string[];
    lastRun?: string;
    nextRun?: string;
  }> {
    const data = await this.request("/automation/settings");
    return {
      enabled: data.enabled || false,
      scheduleTime: data.schedule_time || "02:00",
      timezone: data.timezone || "UTC",
      batchLimit: data.batch_limit || 10,
      targetDuration: data.target_duration || 60,
      autoRetry: data.auto_retry ?? true,
      retryAttempts: data.retry_attempts || 3,
      notifyOnComplete: data.notify_on_complete ?? true,
      selectedParts: data.selected_parts || [],
      lastRun: data.last_run,
      nextRun: data.next_run,
    };
  }

  /**
   * Trigger automation run manually
   */
  async triggerAutomationRun(): Promise<{
    success: boolean;
    message: string;
    jobId?: string;
  }> {
    return this.request("/automation/trigger", {
      method: "POST",
    });
  }
}

/**
 * Singleton API client instance
 */
let apiClient: ShortsApiClient | null = null;

/**
 * Get or create the API client singleton
 * The baseUrl is fetched from Docusaurus config or environment on first call
 */
export function getShortsApiClient(): ShortsApiClient {
  if (!apiClient) {
    apiClient = new ShortsApiClient(getShortsApiBaseUrl());
  }
  return apiClient;
}

/**
 * Reset the API client singleton (useful for testing or config changes)
 */
export function resetShortsApiClient(): void {
  apiClient = null;
}
