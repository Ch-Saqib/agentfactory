/**
 * Types for Shorts components
 */

/**
 * A short video generated from lesson content
 */
export interface ShortVideo {
  /** Unique identifier */
  id: string;
  /** Path to the source lesson (e.g., "01-General-Agents-Foundations/01-agent-factory-paradigm/...") */
  lessonPath: string;
  /** Video title */
  title: string;
  /** Duration in seconds */
  durationSeconds: number;
  /** CDN URL for the video file */
  videoUrl: string;
  /** CDN URL for the thumbnail image */
  thumbnailUrl: string;
  /** Number of views */
  viewCount?: number;
  /** Number of likes */
  likeCount?: number;
  /** Number of comments */
  commentCount?: number;
  /** Generation cost in USD */
  generationCost?: number;
  /** Internal note (not displayed on UI) */
  note?: string;
}

/**
 * Filters for shorts feed
 */
export interface ShortsFilters {
  /** Part filter (01-09) */
  part?: string;
  /** Chapter filter within part */
  chapter?: string;
  /** Search keyword */
  search?: string;
  /** Sort order */
  sort?: "recent" | "popular" | "relevant";
}

/**
 * Response from shorts API
 */
export interface ShortsApiResponse {
  /** List of short videos */
  shorts: ShortVideo[];
  /** Total count (for pagination) */
  totalCount: number;
  /** Current page */
  page: number;
  /** Page size */
  pageSize: number;
  /** Whether there are more results */
  hasMore: boolean;
}

/**
 * Engagement action types
 */
export type EngagementAction = "like" | "unlike" | "comment" | "share";

/**
 * Engagement event data
 */
export interface EngagementEvent {
  /** Type of action */
  action: EngagementAction;
  /** Video ID */
  videoId: string;
  /** Optional comment text (for comment actions) */
  comment?: string;
  /** Timestamp */
  timestamp: Date;
}
