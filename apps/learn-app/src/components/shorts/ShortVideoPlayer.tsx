/**
 * ShortVideoPlayer - Individual video player for shorts feed
 *
 * Features:
 * - Auto-play when visible
 * - Pause when scrolled away
 * - Muted by default, tap to unmute
 * - Loop playback
 * - Responsive 9:16 aspect ratio
 */

import React, { useRef, useEffect, useState, useCallback } from "react";
import type { ShortVideo } from "./types";

interface ShortVideoPlayerProps {
  /** The video to play */
  short: ShortVideo;
  /** Whether this video is currently visible in viewport */
  isActive: boolean;
  /** Callback when video is clicked */
  onVideoClick?: () => void;
}

export function ShortVideoPlayer({
  short,
  isActive,
  onVideoClick,
}: ShortVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isMuted, setIsMuted] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [progress, setProgress] = useState(0);

  // Auto-play/pause based on visibility
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isActive && !hasError) {
      // Attempt to play with muted first (autoplay policy)
      video.muted = true;
      setIsMuted(true);

      const playPromise = video.play();

      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            setIsPlaying(true);
          })
          .catch((error) => {
            console.warn("Autoplay prevented:", error);
            setIsPlaying(false);
          });
      }
    } else {
      video.pause();
      setIsPlaying(false);
    }
  }, [isActive, hasError]);

  // Update progress bar
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setProgress((video.currentTime / video.duration) * 100);
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    return () => video.removeEventListener("timeupdate", handleTimeUpdate);
  }, []);

  // Handle video click (toggle mute/play)
  const handleClick = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    // First click: unmute
    if (isMuted) {
      video.muted = false;
      setIsMuted(false);
      if (!isPlaying) {
        video.play();
        setIsPlaying(true);
      }
    } else {
      // Subsequent clicks: toggle play/pause
      if (isPlaying) {
        video.pause();
        setIsPlaying(false);
      } else {
        video.play();
        setIsPlaying(true);
      }
    }

    onVideoClick?.();
  }, [isMuted, isPlaying, onVideoClick]);

  // Handle double tap to like
  const [showHeart, setShowHeart] = useState(false);
  let lastTap = 0;

  const handleDoubleClick = useCallback(() => {
    const now = Date.now();
    if (now - lastTap < 300) {
      // Double tap detected
      setShowHeart(true);
      setTimeout(() => setShowHeart(false), 1000);
      // TODO: Trigger like action
    }
    lastTap = now;
  }, []);

  // Handle video errors
  const handleError = useCallback(() => {
    console.error("Video playback error:", short.videoUrl);
    setHasError(true);
    setIsPlaying(false);
  }, [short.videoUrl]);

  // Handle load start
  const handleLoadStart = useCallback(() => {
    setHasError(false);
  }, []);

  return (
    <div className="relative h-full w-full bg-gray-900">
      {/* Video Element */}
      <video
        ref={videoRef}
        className="h-full w-full object-cover"
        src={short.videoUrl}
        loop
        playsInline
        muted={isMuted}
        onClick={handleClick}
        onDoubleClick={handleDoubleClick}
        onError={handleError}
        onLoadStart={handleLoadStart}
        poster={short.thumbnailUrl}
      />

      {/* Heart Animation (Double Tap) */}
      {showHeart && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="animate-heart-beat text-6xl text-red-500">
            ❤️
          </div>
        </div>
      )}

      {/* Muted Indicator */}
      {isMuted && isPlaying && (
        <div className="absolute right-4 top-4 flex items-center gap-2 rounded-full bg-black/50 px-3 py-1">
          <span className="text-white">🔇</span>
          <span className="text-sm text-white">Tap to unmute</span>
        </div>
      )}

      {/* Paused Indicator */}
      {!isPlaying && isActive && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-black/50 text-4xl text-white">
            ▶️
          </div>
        </div>
      )}

      {/* Error State */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
          <div className="text-center text-white">
            <p className="text-lg font-semibold">Video unavailable</p>
            <p className="text-sm text-gray-400">Please try again later</p>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {isPlaying && !hasError && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-800">
          <div
            className="h-full bg-red-500 transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Gradient Overlay at bottom */}
      <div className="pointer-events-none absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/60 to-transparent" />
    </div>
  );
}
