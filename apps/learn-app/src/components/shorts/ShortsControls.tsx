/**
 * ShortsControls - Like, Comment, and Share actions
 *
 * Features:
 * - Like button with heart animation
 * - Comment button with count
 * - Share button with native share API
 * - Persistent engagement state
 */

import React, { useState, useCallback } from "react";
import type { ShortVideo } from "./types";

interface ShortsControlsProps {
  /** The video this controls are for */
  short: ShortVideo;
  /** Callback when like button is pressed */
  onLike?: () => void;
  /** Callback when comment button is pressed */
  onComment?: () => void;
  /** Callback when share button is pressed */
  onShare?: () => void;
}

interface ControlButtonProps {
  icon: string;
  label: string;
  count?: number;
  onPress: () => void;
  isActive?: boolean;
}

function ControlButton({
  icon,
  label,
  count,
  onPress,
  isActive = false,
}: ControlButtonProps) {
  return (
    <button
      onClick={onPress}
      className={`flex flex-col items-center gap-1 transition-transform active:scale-95 ${
        isActive ? "text-red-500" : "text-white"
      }`}
    >
      <div
        className={`flex h-10 w-10 items-center justify-center rounded-full ${
          isActive ? "bg-red-500/20" : "bg-white/10"
        } text-xl`}
      >
        {icon}
      </div>
      <span className="text-xs font-medium">{count || label}</span>
    </button>
  );
}

export function ShortsControls({
  short,
  onLike,
  onComment,
  onShare,
}: ShortsControlsProps) {
  const [isLiked, setIsLiked] = useState(false);
  const [likeCount, setLikeCount] = useState(short.likeCount || 0);
  const [showHeartAnimation, setShowHeartAnimation] = useState(false);

  // Handle like action
  const handleLike = useCallback(() => {
    setIsLiked((prev) => !prev);
    setLikeCount((prev) => prev + (isLiked ? -1 : 1));

    if (!isLiked) {
      // Trigger heart animation
      setShowHeartAnimation(true);
      setTimeout(() => setShowHeartAnimation(false), 1000);
    }

    onLike?.();
  }, [isLiked, onLike]);

  // Handle comment action
  const handleComment = useCallback(() => {
    onComment?.();
  }, [onComment]);

  // Handle share action
  const handleShare = useCallback(() => {
    onShare?.();
  }, [onShare]);

  return (
    <div className="flex items-center justify-between">
      {/* Left Side: View Lesson Link */}
      <button className="flex items-center gap-2 rounded-full bg-white/20 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-white/30">
        <span>📖</span>
        <span>View Lesson</span>
      </button>

      {/* Right Side: Action Buttons */}
      <div className="flex items-center gap-4">
        {/* Like Button */}
        <ControlButton
          icon={showHeartAnimation ? "❤️" : isLiked ? "❤️" : "🤍"}
          label={likeCount > 0 ? likeCount.toString() : "Like"}
          count={likeCount > 0 ? likeCount : undefined}
          onPress={handleLike}
          isActive={isLiked}
        />

        {/* Comment Button */}
        <ControlButton
          icon="💬"
          label={short.commentCount > 0 ? short.commentCount.toString() : "Comment"}
          count={short.commentCount > 0 ? short.commentCount : undefined}
          onPress={handleComment}
        />

        {/* Share Button */}
        <ControlButton
          icon="🔗"
          label="Share"
          onPress={handleShare}
        />
      </div>
    </div>
  );
}
