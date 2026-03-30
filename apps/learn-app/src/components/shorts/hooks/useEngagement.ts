/**
 * useEngagement - Hook for managing video engagement actions
 *
 * Features:
 * - Like/unlike videos
 * - Add comments
 * - Share videos
 * - Track view progress
 */

import { useState, useCallback } from "react";
import { getShortsApiClient } from "../../../lib/shorts-api";

interface UseEngagementOptions {
  /** Video ID to engage with */
  videoId: string;
}

interface UseEngagementResult {
  /** Whether video is liked */
  isLiked: boolean;
  /** Like count */
  likeCount: number;
  /** Comment count */
  commentCount: number;
  /** Loading state */
  loading: boolean;
  /** Toggle like */
  toggleLike: () => Promise<void>;
  /** Add comment */
  addComment: (text: string, parentId?: string) => Promise<void>;
  /** Share video */
  shareVideo: () => Promise<void>;
  /** Record view progress */
  recordView: (watchDuration: number, completed: boolean) => Promise<void>;
}

/**
 * Hook for managing video engagement
 */
export function useEngagement({ videoId }: UseEngagementOptions): UseEngagementResult {
  const apiClient = getShortsApiClient();

  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(0);
  const [commentCount, setCommentCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // Toggle like/unlike
  const toggleLike = useCallback(async () => {
    setLoading(true);

    try {
      if (isLiked) {
        await apiClient.unlikeVideo(videoId);
        setIsLiked(false);
        setLikeCount((prev) => Math.max(0, prev - 1));
      } else {
        await apiClient.likeVideo(videoId);
        setIsLiked(true);
        setLikeCount((prev) => prev + 1);
      }
    } catch (error) {
      console.error("Failed to toggle like:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [isLiked, videoId, apiClient]);

  // Add comment
  const addComment = useCallback(
    async (text: string, parentId?: string) => {
      if (!text.trim()) {
        throw new Error("Comment text cannot be empty");
      }

      setLoading(true);

      try {
        await apiClient.commentOnVideo({
          videoId,
          text,
          parentId,
        });

        setCommentCount((prev) => prev + 1);
      } catch (error) {
        console.error("Failed to add comment:", error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [videoId, apiClient]
  );

  // Share video
  const shareVideo = useCallback(async () => {
    // Use native share API if available
    if (navigator.share) {
      try {
        await navigator.share({
          title: "Check out this short!",
          text: "I found this great educational short on Agent Factory.",
          url: window.location.href,
        });
      } catch (error) {
        // User cancelled or error
        console.log("Share cancelled or failed:", error);
      }
    } else {
      // Fallback: copy link to clipboard
      try {
        await navigator.clipboard.writeText(window.location.href);

        // Show toast notification (you could use a toast library here)
        alert("Link copied to clipboard!");
      } catch (error) {
        console.error("Failed to copy link:", error);
      }
    }
  }, []);

  // Record view progress
  const recordView = useCallback(
    async (watchDuration: number, completed: boolean) => {
      try {
        await apiClient.recordView({
          videoId,
          watchDurationSeconds: watchDuration,
          completed,
        });
      } catch (error) {
        // Don't throw for view tracking (non-critical)
        console.warn("Failed to record view:", error);
      }
    },
    [videoId, apiClient]
  );

  return {
    isLiked,
    likeCount,
    commentCount,
    loading,
    toggleLike,
    addComment,
    shareVideo,
    recordView,
  };
}

/**
 * Hook for batch engagement actions (like multiple videos)
 */
interface UseBatchEngagementOptions {
  /** List of video IDs */
  videoIds: string[];
}

interface UseBatchEngagementResult {
  /** Like all videos */
  likeAll: () => Promise<void>;
  /** Unlike all videos */
  unlikeAll: () => Promise<void>;
  /** Get engagement stats */
  getStats: () => Promise<{
    totalLikes: number;
    totalComments: number;
    totalViews: number;
  }>;
}

/**
 * Hook for batch engagement operations
 */
export function useBatchEngagement({
  videoIds,
}: UseBatchEngagementOptions): UseBatchEngagementResult {
  const apiClient = getShortsApiClient();

  const likeAll = useCallback(async () => {
    const promises = videoIds.map((id) => apiClient.likeVideo(id));
    await Promise.all(promises);
  }, [videoIds, apiClient]);

  const unlikeAll = useCallback(async () => {
    const promises = videoIds.map((id) => apiClient.unlikeVideo(id));
    await Promise.all(promises);
  }, [videoIds, apiClient]);

  const getStats = useCallback(async () => {
    // Fetch stats for each video
    const videos = await Promise.all(
      videoIds.map((id) => apiClient.getVideo(id))
    );

    const totalLikes = videos.reduce((sum, v) => sum + (v.likeCount || 0), 0);
    const totalComments = videos.reduce((sum, v) => sum + (v.commentCount || 0), 0);
    const totalViews = videos.reduce((sum, v) => sum + (v.viewCount || 0), 0);

    return {
      totalLikes,
      totalComments,
      totalViews,
    };
  }, [videoIds, apiClient]);

  return {
    likeAll,
    unlikeAll,
    getStats,
  };
}
