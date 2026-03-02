import React, { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Users, UserPlus, Check, X } from "lucide-react";
import { getFriends, acceptFriendRequest, type FriendListResponse } from "@/lib/progress-api";
import { FriendCard } from "./FriendCard";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface FriendListProps {
  className?: string;
}

export function FriendList({ className }: FriendListProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8001";

  const [data, setData] = useState<FriendListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState<string | null>(null);

  const loadFriends = async () => {
    try {
      setLoading(true);
      const result = await getFriends(progressApiUrl);
      setData(result);
    } catch (err) {
      console.error("Failed to load friends:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFriends();
  }, [progressApiUrl]);

  const handleAccept = async (requesterId: string) => {
    try {
      setAccepting(requesterId);
      await acceptFriendRequest(progressApiUrl, requesterId);
      await loadFriends();
    } catch (err) {
      console.error("Failed to accept friend request:", err);
    } finally {
      setAccepting(null);
    }
  };

  if (loading) {
    return (
      <div className={cn("space-y-3", className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const hasContent =
    data.friends.length > 0 ||
    data.pending_requests.length > 0 ||
    data.sent_requests.length > 0;

  if (!hasContent) {
    return (
      <div className={cn("text-center py-8", className)}>
        <Users className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
        <h3 className="text-sm font-medium text-foreground mb-1">
          No friends yet
        </h3>
        <p className="text-xs text-muted-foreground">
          Add friends to compete on leaderboards and earn buddy XP!
        </p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Pending requests */}
      {data.pending_requests.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Pending Requests ({data.pending_requests.length})
          </h3>
          <div className="space-y-2">
            {data.pending_requests.map((friend) => (
              <div
                key={friend.user_id}
                className="flex items-center gap-3 p-3 rounded-lg border border-primary/30 bg-primary/5"
              >
                <FriendCard friend={friend} className="flex-1" />
                <div className="flex items-center gap-1">
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-8 w-8 text-primary hover:bg-primary/20"
                    onClick={() => handleAccept(friend.user_id)}
                    disabled={accepting === friend.user_id}
                  >
                    <Check className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Friends */}
      {data.friends.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Friends ({data.friends.length})
          </h3>
          <div className="space-y-2">
            {data.friends.map((friend) => (
              <FriendCard key={friend.user_id} friend={friend} />
            ))}
          </div>
        </div>
      )}

      {/* Sent requests */}
      {data.sent_requests.length > 0 && (
        <div>
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">
            Sent Requests ({data.sent_requests.length})
          </h3>
          <div className="space-y-2">
            {data.sent_requests.map((friend) => (
              <FriendCard key={friend.user_id} friend={friend} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
