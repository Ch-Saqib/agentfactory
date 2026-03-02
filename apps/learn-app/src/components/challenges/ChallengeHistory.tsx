import React, { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Trophy, X, Calendar } from "lucide-react";
import {
  getChallengeHistory,
  type ChallengeHistoryResponse,
} from "@/lib/progress-api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import "@/components/progress/gamification.css";

interface ChallengeHistoryProps {
  className?: string;
}

export function ChallengeHistory({ className }: ChallengeHistoryProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8001";

  const [history, setHistory] = useState<ChallengeHistoryResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (open) {
      loadHistory();
    }
  }, [open, progressApiUrl]);

  async function loadHistory() {
    try {
      setLoading(true);
      const data = await getChallengeHistory(progressApiUrl, 7);
      setHistory(data);
    } catch (err) {
      console.error("Failed to load challenge history:", err);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateStr: string): string {
    const date = new Date(dateStr);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return "Today";
    }
    if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    }
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className={className}>
          <Calendar className="h-4 w-4 mr-2" />
          History
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Challenge History</DialogTitle>
        </DialogHeader>

        <div className="mt-4">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-16 bg-muted rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : history && history.challenges.length > 0 ? (
            <div className="space-y-2">
              {history.challenges.map((challenge) => (
                <div
                  key={challenge.id}
                  className={cn(
                    "flex items-center gap-3 p-3 rounded-lg border",
                    challenge.completed
                      ? "bg-primary/5 border-primary/20"
                      : "bg-muted/30 border-border"
                  )}
                >
                  <div
                    className={cn(
                      "p-2 rounded-md",
                      challenge.completed
                        ? "bg-primary/20 text-primary"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    <Trophy className="h-4 w-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-foreground truncate">
                        {challenge.title}
                      </h4>
                      <span className="text-xs text-muted-foreground ml-2">
                        {formatDate(challenge.challenge_date)}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 mt-1">
                      {challenge.completed ? (
                        <span className="text-xs text-primary font-medium">
                          +{challenge.xp_awarded} XP earned
                        </span>
                      ) : (
                        <span className="text-xs text-muted-foreground">
                          Not completed
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Trophy className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No challenge history yet</p>
              <p className="text-xs mt-1">Complete your first challenge!</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
