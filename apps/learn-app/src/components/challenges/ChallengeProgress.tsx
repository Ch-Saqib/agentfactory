import React from "react";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface ChallengeProgressProps {
  current: number;
  target: number;
  unit: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function ChallengeProgress({
  current,
  target,
  unit,
  size = "md",
  className,
}: ChallengeProgressProps) {
  const percentage = Math.min((current / target) * 100, 100);
  const isComplete = current >= target;

  const sizeMap = {
    sm: { container: "h-8 w-8", text: "text-xs" },
    md: { container: "h-12 w-12", text: "text-sm" },
    lg: { container: "h-16 w-16", text: "text-lg" },
  };

  const textSize = sizeMap[size].text;
  const containerSize = sizeMap[size].container;

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)}>
      {/* Background circle */}
      <svg
        className={cn(containerSize, "transform -rotate-90")}
        viewBox="0 0 36 36"
      >
        {/* Background path */}
        <path
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className="text-muted stroke-current opacity-20"
        />
        {/* Progress path */}
        <path
          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={`${percentage}, 100`}
          className={cn(
            "stroke-current transition-all duration-500 ease-out",
            isComplete
              ? "text-primary"
              : "text-[oklch(0.68_0.16_142)]"
          )}
        />
      </svg>

      {/* Center content */}
      <div className="absolute inset-0 flex items-center justify-center">
        {isComplete ? (
          <Check
            className={cn(
              "text-primary",
              size === "sm" ? "h-3 w-3" : size === "md" ? "h-5 w-5" : "h-6 w-6"
            )}
          />
        ) : (
          <span className={cn(textSize, "font-bold tabular-nums text-foreground")}>
            {current}
          </span>
        )}
      </div>
    </div>
  );
}
