import { useState, useEffect, useRef } from "react";

interface CheckpointTrigger {
  position: number; // 50 or 75
  triggered: boolean;
}

export function useCheckpoints(enabled: boolean, lessonSlug: string) {
  const [activeCheckpoint, setActiveCheckpoint] = useState<number | null>(null);
  const checkpointsRef = useRef<CheckpointTrigger[]>([
    { position: 50, triggered: false },
    { position: 75, triggered: false },
  ]);

  useEffect(() => {
    if (!enabled) return;

    const handleScroll = () => {
      const scrollHeight = document.documentElement.scrollHeight;
      const scrollTop = window.scrollY;
      const clientHeight = window.innerHeight;

      // Calculate scroll percentage
      const scrollPercent = Math.round(
        ((scrollTop + clientHeight) / scrollHeight) * 100
      );

      // Check if we've passed any checkpoint thresholds
      checkpointsRef.current.forEach((checkpoint) => {
        if (
          !checkpoint.triggered &&
          scrollPercent >= checkpoint.position
        ) {
          checkpoint.triggered = true;
          setActiveCheckpoint(checkpoint.position);

          // Auto-reset after showing (user will close the modal)
          setTimeout(() => {
            setActiveCheckpoint(null);
          }, 30000); // 30 second timeout
        }
      });
    };

    // Throttled scroll handler
    let ticking = false;
    const throttledScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener("scroll", throttledScroll, { passive: true });
    return () => window.removeEventListener("scroll", throttledScroll);
  }, [enabled, lessonSlug]);

  const closeCheckpoint = () => setActiveCheckpoint(null);

  return {
    activeCheckpoint,
    closeCheckpoint,
  };
}
