import React from "react";
import { User, Trophy, Flame, Clock } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import type { FriendInfo } from "@/lib/progress-types";

interface FriendCardProps {
  friend: FriendInfo;
  className?: string;
}

export function FriendCard({ friend, className }: FriendCardProps) {
  const initials = friend.display_name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const formatLastActivity = (dateStr: string | null): string => {
    if (!dateStr) return "No recent activity";
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return "Over a week ago";
  };

  return (
    <div
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border border-border bg-card",
        "hover:bg-accent transition-colors",
        className
      )}
    >
      {/* Avatar */}
      <Avatar className="h-10 w-10">
        <AvatarImage src={friend.avatar_url || undefined} />
        <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
          {initials}
        </AvatarFallback>
      </Avatar>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h4 className="text-sm font-medium text-foreground truncate">
            {friend.display_name}
          </h4>
          {friend.current_streak > 0 && (
            <div className="flex items-center gap-0.5 text-[10px] text-[oklch(0.77_0.16_77)]">
              <Flame className="h-3 w-3 fill-current" />
              <span>{friend.current_streak}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Trophy className="h-3 w-3" />
            {friend.total_xp.toLocaleString()} XP
          </span>

          {friend.last_activity && (
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatLastActivity(friend.last_activity.completed_at)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
