/**
 * useShortsFeed - Hook for fetching shorts feed data
 *
 * Features:
 * - Fetch shorts with filters
 * - Pagination support
 * - Caching with react-query style
 * - Error handling and retry
 */

import { useState, useCallback, useEffect } from "react";
import { getShortsApiClient, ShortsApiError } from "../../../lib/shorts-api";
import type { ShortsFilters, ShortVideo } from "../types";

interface UseShortsFeedOptions extends ShortsFilters {
  /** Page size (default: 20) */
  pageSize?: number;
  /** Initial page (default: 0) */
  initialPage?: number;
}

interface UseShortsFeedResult {
  /** List of shorts */
  shorts: ShortVideo[];
  /** Loading state */
  loading: boolean;
  /** Error state */
  error: Error | null;
  /** Whether there are more results */
  hasMore: boolean;
  /** Current page */
  page: number;
  /** Load more shorts */
  loadMore: () => void;
  /** Refresh the feed */
  refresh: () => void;
  /** Total count */
  totalCount: number;
}

/**
 * Hook for fetching shorts feed
 */
export function useShortsFeed(
  options: UseShortsFeedOptions = {}
): UseShortsFeedResult {
  const {
    part,
    chapter,
    search,
    sort = "recent",
    pageSize = 20,
    initialPage = 0,
  } = options;

  const [shorts, setShorts] = useState<ShortVideo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [page, setPage] = useState(initialPage);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  const apiClient = getShortsApiClient();

  // Build filters key for cache invalidation
  const filtersKey = JSON.stringify({ part, chapter, search, sort });

  // Load initial data
  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiClient.getVideos({
          part,
          chapter,
          search,
          sort,
          limit: pageSize,
          offset: 0,
        });

        if (isMounted) {
          setShorts(result.shorts);
          setTotalCount(result.totalCount);
          setHasMore(result.hasMore);
          setPage(1);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, [filtersKey, pageSize, apiClient]); // Reload when filters change

  // Load more (pagination)
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const offset = page * pageSize;
      const result = await apiClient.getVideos({
        part,
        chapter,
        search,
        sort,
        limit: pageSize,
        offset,
      });

      setShorts((prev) => [...prev, ...result.shorts]);
      setTotalCount(result.totalCount);
      setHasMore(result.hasMore);
      setPage((prev) => prev + 1);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [loading, hasMore, page, part, chapter, search, sort, pageSize, apiClient]);

  // Refresh (reload from scratch)
  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.getVideos({
        part,
        chapter,
        search,
        sort,
        limit: pageSize,
        offset: 0,
      });

      setShorts(result.shorts);
      setTotalCount(result.totalCount);
      setHasMore(result.hasMore);
      setPage(1);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [part, chapter, search, sort, pageSize, apiClient]);

  return {
    shorts,
    loading,
    error,
    hasMore,
    page,
    loadMore,
    refresh,
    totalCount,
  };
}

/**
 * Hook for liking/unliking a video
 */
export function useVideoLike(videoId: string): {
  isLiked: boolean;
  likeCount: number;
  toggleLike: () => Promise<void>;
  loading: boolean;
} {
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const apiClient = getShortsApiClient();

  const toggleLike = useCallback(async () => {
    setLoading(true);

    try {
      if (isLiked) {
        await apiClient.unlikeVideo(videoId);
        setIsLiked(false);
        setLikeCount((prev) => prev - 1);
      } else {
        await apiClient.likeVideo(videoId);
        setIsLiked(true);
        setLikeCount((prev) => prev + 1);
      }
    } finally {
      setLoading(false);
    }
  }, [isLiked, videoId, apiClient]);

  return {
    isLiked,
    likeCount,
    toggleLike,
    loading,
  };
}

/**
 * Hook for commenting on a video
 */
export function useVideoComments(videoId: string): {
  comments: Array<{
    id: string;
    userId: string;
    videoId: string;
    text: string;
    parentId?: string;
    createdAt: string;
  }>;
  loading: boolean;
  error: Error | null;
  addComment: (text: string, parentId?: string) => Promise<void>;
  loadComments: () => Promise<void>;
  totalCount: number;
} {
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [totalCount, setTotalCount] = useState(0);

  const apiClient = getShortsApiClient();

  const loadComments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient.getComments(videoId);
      setComments(result.comments);
      setTotalCount(result.totalCount);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [videoId, apiClient]);

  const addComment = useCallback(
    async (text: string, parentId?: string) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiClient.commentOnVideo({
          videoId,
          text,
          parentId,
        });

        // Add new comment to list
        setComments((prev) => [
          {
            id: result.commentId,
            userId: "current-user", // TODO: Get actual user ID
            videoId,
            text: result.text,
            parentId,
            createdAt: result.createdAt,
          },
          ...prev,
        ]);

        setTotalCount((prev) => prev + 1);
      } catch (err) {
        setError(err as Error);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [videoId, apiClient]
  );

  return {
    comments,
    loading,
    error,
    addComment,
    loadComments,
    totalCount,
  };
}

/**
 * Hook for tracking video views
 */
export function useVideoViewTracking(): {
  recordView: (videoId: string, watchDuration: number, completed: boolean) => Promise<void>;
} {
  const apiClient = getShortsApiClient();

  const recordView = useCallback(
    async (videoId: string, watchDuration: number, completed: boolean) => {
      try {
        await apiClient.recordView({
          videoId,
          watchDurationSeconds: watchDuration,
          completed,
        });
      } catch (err) {
        // Don't throw errors for view tracking (non-critical)
        console.warn("Failed to record view:", err);
      }
    },
    [apiClient]
  );

  return { recordView };
}

// Export types for use in other modules
export type { UseShortsFeedOptions, UseShortsFeedResult };
