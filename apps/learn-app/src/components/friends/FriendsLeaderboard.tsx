import React, { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Trophy, Medal } from "lucide-react";
import { getFriendsLeaderboard, type FriendsLeaderboardResponse } from "@/lib/progress-api";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import "@/components/progress/gamification.css";

interface FriendsLeaderboardProps {
  className?: string;
}

export function FriendsLeaderboard({ className }: FriendsLeaderboardProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8002";

  const [data, setData] = useState<FriendsLeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, [progressApiUrl]);

  async function loadLeaderboard() {
    try {
      setLoading(true);
      const result = await getFriendsLeaderboard(progressApiUrl);
      setData(result);
    } catch (err) {
      console.error("Failed to load friends leaderboard:", err);
    } finally {
      setLoading(false);
    }
  }

  function getRankIcon(rank: number): React.ReactNode {
    if (rank === 1) return <Medal className="h-5 w-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-700" />;
    return <span className="text-sm font-medium text-muted-foreground w-5">#{rank}</span>;
  }

  if (loading) {
    return (
      <div className={cn("space-y-2", className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data || data.entries.length === 0) {
    return (
      <div className={cn("text-center py-8", className)}>
        <Trophy className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
        <h3 className="text-sm font-medium text-foreground mb-1">
          No friends on leaderboard
        </h3>
        <p className="text-xs text-muted-foreground">
          Add friends to compete!
        </p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {data.entries.map((entry, index) => {
        const initials = entry.display_name
          .split(" ")
          .map((n) => n[0])
          .join("")
          .toUpperCase()
          .slice(0, 2);

        return (
          <div
            key={entry.user_id}
            className={cn(
              "flex items-center gap-3 p-3 rounded-lg border transition-colors",
              entry.is_you
                ? "border-primary bg-primary/5"
                : "border-border bg-card hover:bg-accent"
            )}
          >
            {/* Rank */}
            <div className="w-8 flex justify-center">
              {getRankIcon(entry.rank)}
            </div>

            {/* Avatar */}
            <Avatar className="h-10 w-10">
              <AvatarImage src={entry.avatar_url || undefined} />
              <AvatarFallback
                className={cn(
                  "text-xs font-semibold",
                  entry.is_you
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                {initials}
              </AvatarFallback>
            </Avatar>

            {/* Name and stats */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h4
                  className={cn(
                    "text-sm font-medium truncate",
                    entry.is_you && "text-primary"
                  )}
                >
                  {entry.display_name}
                  {entry.is_you && (
                    <span className="ml-2 text-xs">(You)</span>
                  )}
                </h4>
              </div>

              <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Trophy className="h-3 w-3 text-[oklch(0.68_0.16_142)]" />
                  {entry.total_xp.toLocaleString()} XP
                </span>

                {entry.current_streak > 0 && (
                  <span>🔥 {entry.current_streak}</span>
                )}
              </div>
            </div>

            {/* Badges */}
            <div className="text-sm font-semibold text-muted-foreground">
              {entry.badge_count}
            </div>
          </div>
        );
      })}

      {/* Your rank indicator */}
      {data.your_rank && (
        <div className="mt-4 pt-4 border-t border-border text-center text-xs text-muted-foreground">
          Your rank: <span className="font-semibold text-foreground">#{data.your_rank}</span>
          {" "}/ {data.entries.length}
        </div>
      )}
    </div>
  );
}
