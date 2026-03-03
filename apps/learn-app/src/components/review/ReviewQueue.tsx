import React, { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Brain, RefreshCw, Loader2 } from "lucide-react";
import { getReviewQueue, type ReviewQueueResponse } from "@/lib/progress-api";
import { ReviewCard } from "./ReviewCard";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ReviewQueueProps {
  className?: string;
  onStartReview?: (itemId: number, chapterSlug: string) => void;
}

export function ReviewQueue({ className, onStartReview }: ReviewQueueProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8002";

  const [data, setData] = useState<ReviewQueueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const result = await getReviewQueue(progressApiUrl);
      setData(result);
    } catch (err) {
      console.error("Failed to load review queue:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      const result = await getReviewQueue(progressApiUrl);
      setData(result);
    } catch (err) {
      console.error("Failed to refresh review queue:", err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleStartReview = (itemId: number) => {
    const item = data?.items.find((i) => i.id === itemId);
    if (item && onStartReview) {
      onStartReview(itemId, item.chapter_slug);
    }
  };

  useEffect(() => {
    loadQueue();
  }, [progressApiUrl]);

  if (loading) {
    return (
      <div className={cn("space-y-3", className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-muted rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className={cn("text-center py-8", className)}>
        <Brain className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
        <h3 className="text-sm font-medium text-foreground mb-1">
          All caught up!
        </h3>
        <p className="text-xs text-muted-foreground">
          No reviews due right now. Keep learning!
        </p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-foreground">
            Review Queue
          </h3>
          <p className="text-xs text-muted-foreground">
            {data.total_count} item{data.total_count !== 1 ? "s" : ""} due
            {data.high_priority_count > 0 && (
              <span className="ml-2 text-orange-600 dark:text-orange-400">
                {data.high_priority_count} high priority
              </span>
            )}
          </p>
        </div>

        <Button
          variant="ghost"
          size="icon"
          onClick={handleRefresh}
          disabled={refreshing}
          title="Refresh queue"
        >
          <RefreshCw
            className={cn("h-4 w-4", refreshing && "animate-spin")}
          />
        </Button>
      </div>

      {/* Queue items */}
      <div className="space-y-2">
        {data.items.map((item) => (
          <ReviewCard
            key={item.id}
            item={item}
            onStartReview={handleStartReview}
          />
        ))}
      </div>
    </div>
  );
}
