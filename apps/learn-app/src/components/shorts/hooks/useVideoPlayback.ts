/**
 * useVideoPlayback - Hook for managing video playback
 *
 * Features:
 * - Play/pause control
 * - Mute/unmute control
 * - Seek control
 * - Volume control
 * - Playback rate control
 */

import { useRef, useState, useCallback, useEffect } from "react";

interface UseVideoPlaybackOptions {
  /** Initial muted state */
  initiallyMuted?: boolean;
  /** Auto-play on mount */
  autoPlay?: boolean;
}

interface UseVideoPlaybackResult {
  /** Video element ref */
  videoRef: React.RefObject<HTMLVideoElement>;
  /** Whether video is currently playing */
  isPlaying: boolean;
  /** Whether video is currently muted */
  isMuted: boolean;
  /** Current playback time in seconds */
  currentTime: number;
  /** Total duration in seconds */
  duration: number;
  /** Volume (0-1) */
  volume: number;
  /** Playback rate */
  playbackRate: number;
  /** Toggle play/pause */
  togglePlay: () => void;
  /** Toggle mute */
  toggleMute: () => void;
  /** Seek to specific time */
  seek: (time: number) => void;
  /** Set volume */
  setVolume: (volume: number) => void;
  /** Set playback rate */
  setPlaybackRate: (rate: number) => void;
  /** Restart video */
  restart: () => void;
}

/**
 * Hook for managing video playback
 */
export function useVideoPlayback(
  options: UseVideoPlaybackOptions = {}
): UseVideoPlaybackResult {
  const { initiallyMuted = true, autoPlay = false } = options;

  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(initiallyMuted);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolumeState] = useState(1);
  const [playbackRate, setPlaybackRateState] = useState(1);

  // Update duration when metadata loads
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    return () => video.removeEventListener("loadedmetadata", handleLoadedMetadata);
  }, []);

  // Update current time during playback
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    return () => video.removeEventListener("timeupdate", handleTimeUpdate);
  }, []);

  // Auto-play on mount if enabled
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !autoPlay) return;

    video.play().then(() => {
      setIsPlaying(true);
    }).catch(() => {
      // Autoplay prevented, that's okay
      setIsPlaying(false);
    });
  }, [autoPlay]);

  // Toggle play/pause
  const togglePlay = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
      setIsPlaying(false);
    } else {
      video.play().then(() => {
        setIsPlaying(true);
      }).catch(() => {
        setIsPlaying(false);
      });
    }
  }, [isPlaying]);

  // Toggle mute
  const toggleMute = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !video.muted;
    setIsMuted(!video.muted);
  }, []);

  // Seek to specific time
  const seek = useCallback((time: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = time;
    setCurrentTime(time);
  }, []);

  // Set volume
  const setVolume = useCallback((newVolume: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.volume = Math.max(0, Math.min(1, newVolume));
    setVolumeState(video.volume);
  }, []);

  // Set playback rate
  const setPlaybackRate = useCallback((rate: number) => {
    const video = videoRef.current;
    if (!video) return;

    video.playbackRate = rate;
    setPlaybackRateState(rate);
  }, []);

  // Restart video
  const restart = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = 0;
    setCurrentTime(0);

    if (!isPlaying) {
      video.play().then(() => {
        setIsPlaying(true);
      });
    }
  }, [isPlaying]);

  return {
    videoRef,
    isPlaying,
    isMuted,
    currentTime,
    duration,
    volume,
    playbackRate,
    togglePlay,
    toggleMute,
    seek,
    setVolume,
    setPlaybackRate,
    restart,
  };
}
