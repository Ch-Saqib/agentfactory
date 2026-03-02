import React from "react";
import { Brain, TrendingUp, BookOpen, Clock, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ReviewItem } from "@/lib/progress-types";

interface ReviewCardProps {
  item: ReviewItem;
  onStartReview: (itemId: number) => void;
  className?: string;
}

export function ReviewCard({ item, onStartReview, className }: ReviewCardProps) {
  const getReasonIcon = () => {
    switch (item.reason) {
      case "weak_area":
        return <AlertTriangle className="h-4 w-4" />;
      case "spaced_repetition":
        return <TrendingUp className="h-4 w-4" />;
      case "prerequisite":
        return <BookOpen className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const getReasonLabel = () => {
    switch (item.reason) {
      case "weak_area":
        return "Needs Practice";
      case "spaced_repetition":
        return "Due for Review";
      case "prerequisite":
        return "Prerequisite";
      default:
        return "Review";
    }
  };

  const getPriorityStyles = () => {
    switch (item.priority) {
      case "high":
        return {
          border: "border-orange-500/30",
          bg: "bg-orange-500/5",
          badge: "bg-orange-500 text-white",
        };
      case "medium":
        return {
          border: "border-yellow-500/30",
          bg: "bg-yellow-500/5",
          badge: "bg-yellow-500 text-white",
        };
      default:
        return {
          border: "border-border",
          bg: "bg-card",
          badge: "bg-muted text-muted-foreground",
        };
    }
  };

  const styles = getPriorityStyles();

  // Format chapter slug for display
  const chapterName = item.chapter_slug
    .split("/")
    .pop()
    ?.replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase()) || item.chapter_slug;

  return (
    <div
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border transition-all hover:shadow-md",
        styles.border,
        styles.bg,
        className
      )}
    >
      {/* Reason icon */}
      <div
        className={cn(
          "p-2 rounded-md",
          item.priority === "high"
            ? "bg-orange-500/20 text-orange-600 dark:text-orange-400"
            : "bg-muted text-muted-foreground"
        )}
      >
        {getReasonIcon()}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h4 className="text-sm font-medium text-foreground truncate">
            {chapterName}
          </h4>
          <span
            className={cn(
              "text-[10px] px-1.5 py-0.5 rounded font-medium",
              styles.badge
            )}
          >
            {getReasonLabel()}
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            Due {new Date(item.due_date).toLocaleDateString()}
          </span>
          {item.interval_days > 1 && (
            <span>· {item.interval_days} day interval</span>
          )}
        </div>
      </div>

      {/* Action button */}
      <button
        onClick={() => onStartReview(item.id)}
        className={cn(
          "px-3 py-1.5 rounded-md text-xs font-medium transition-colors",
          "bg-primary text-primary-foreground hover:bg-primary/90"
        )}
      >
        Review
      </button>
    </div>
  );
}
