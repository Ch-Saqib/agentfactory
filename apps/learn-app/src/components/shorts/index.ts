/**
 * Shorts Components - TikTok-style short video feed
 *
 * This module provides components for displaying and interacting
 * with lesson shorts in a TikTok-style vertical video feed.
 */

export { ShortsFeed } from "./ShortsFeed";
export { ShortVideoPlayer } from "./ShortVideoPlayer";
export { ShortsControls } from "./ShortsControls";
export { ShortsComments } from "./ShortsComments";
export { ShortsFilters } from "./ShortsFilters";
export { ShortsSearch, RecommendedShorts } from "./ShortsSearch";

// Admin components
export {
  GenerationDashboard,
  GenerationDashboardMini,
  AnalyticsDashboard,
  AnalyticsDashboardMini,
} from "./admin";

export type { ShortVideo, ShortsFilters, EngagementAction, EngagementEvent } from "./types";
export type { UseShortsFeedOptions, UseShortsFeedResult } from "./hooks/useShortsFeed";
export type { UseVideoPlaybackOptions, UseVideoPlaybackResult } from "./hooks/useVideoPlayback";
export type { UseEngagementOptions, UseEngagementResult } from "./hooks/useEngagement";
export { useEngagement, useBatchEngagement } from "./hooks/useEngagement";
export { useVideoLike, useVideoComments, useVideoViewTracking } from "./hooks/useShortsFeed";
