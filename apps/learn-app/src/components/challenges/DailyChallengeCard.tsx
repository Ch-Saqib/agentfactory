import React, { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Target, Trophy, Clock } from "lucide-react";
import {
  getTodayChallenge,
  updateChallengeProgress,
  type ChallengeResponse,
} from "@/lib/progress-api";
import { cn } from "@/lib/utils";
import "@/components/progress/gamification.css";

interface DailyChallengeCardProps {
  className?: string;
  onChallengeComplete?: (xpEarned: number) => void;
}

export default function DailyChallengeCard({
  className,
  onChallengeComplete,
}: DailyChallengeCardProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8002";

  const [challenge, setChallenge] = useState<ChallengeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadChallenge();
  }, [progressApiUrl]);

  async function loadChallenge() {
    try {
      setLoading(true);
      setError(null);
      const data = await getTodayChallenge(progressApiUrl);
      setChallenge(data);
    } catch (err) {
      console.error("Failed to load challenge:", err);
      setError("Failed to load today's challenge");
    } finally {
      setLoading(false);
    }
  }

  function getProgressPercentage(): number {
    if (!challenge) return 0;
    return Math.min(
      (challenge.progress.current / challenge.progress.target) * 100,
      100
    );
  }

  function getIconForType(type: string): React.ReactNode {
    const iconMap: Record<string, React.ReactNode> = {
      quiz_master: <Target className="h-5 w-5" />,
      learning_spree: <Trophy className="h-5 w-5" />,
      perfect_week: <Clock className="h-5 w-5" />,
      explorer: <Target className="h-5 w-5" />,
      night_owl: <Clock className="h-5 w-5" />,
      early_bird: <Clock className="h-5 w-5" />,
      flashcard_fanatic: <Trophy className="h-5 w-5" />,
      review_master: <Target className="h-5 w-5" />,
    };
    return iconMap[type] || <Target className="h-5 w-5" />;
  }

  if (loading) {
    return (
      <div
        className={cn(
          "rounded-lg border border-border bg-card p-4 animate-pulse",
          className
        )}
      >
        <div className="h-4 bg-muted rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-muted rounded w-1/2"></div>
      </div>
    );
  }

  if (error || !challenge) {
    return null;
  }

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border border-border bg-card",
        "transition-all duration-300 hover:shadow-lg",
        challenge.completed && "border-primary/50 bg-primary/5",
        className
      )}
    >
      {/* Gradient accent */}
      <div
        className={cn(
          "absolute top-0 left-0 w-1 h-full transition-colors",
          challenge.completed
            ? "bg-primary"
            : "bg-[oklch(0.68_0.16_142)]"
        )}
      />

      <div className="p-4 pl-5">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "p-2 rounded-md",
                challenge.completed
                  ? "bg-primary/20 text-primary"
                  : "bg-[oklch(0.68_0.16_142)]/20 text-[oklch(0.68_0.16_142)]"
              )}
            >
              {getIconForType(challenge.challenge_type)}
            </div>
            <div>
              <div className="text-xs text-muted-foreground uppercase tracking-wider font-medium">
                {challenge.completed ? "Completed" : "Today's Challenge"}
              </div>
              <h3 className="text-lg font-bold text-foreground">
                {challenge.title}
              </h3>
            </div>
          </div>

          {/* XP Badge */}
          <div
            className={cn(
              "flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold",
              challenge.completed
                ? "bg-primary/20 text-primary"
                : "bg-[oklch(0.68_0.16_142)]/20 text-[oklch(0.68_0.16_142)]"
            )}
          >
            <span>+</span>
            <span>{challenge.xp_bonus}</span>
            <span className="text-[10px]">XP</span>
          </div>
        </div>

        {/* Description */}
        <p className="text-sm text-muted-foreground mb-4">
          {challenge.description}
        </p>

        {/* Progress Bar */}
        {!challenge.completed && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">
                {challenge.progress.current} / {challenge.progress.target}{" "}
                {challenge.progress.unit}
              </span>
              <span className="text-muted-foreground">
                {Math.round(getProgressPercentage())}%
              </span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all duration-500 ease-out gf-progress-fill",
                  "bg-gradient-to-r from-[oklch(0.68_0.16_142)] to-[oklch(0.70_0.20_142)]"
                )}
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
          </div>
        )}

        {/* Completed State */}
        {challenge.completed && (
          <div className="flex items-center gap-2 text-sm text-primary font-medium">
            <Trophy className="h-4 w-4" />
            <span>Challenge completed!</span>
          </div>
        )}
      </div>
    </div>
  );
}
