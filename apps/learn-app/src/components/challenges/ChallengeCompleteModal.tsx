import React from "react";
import { Trophy, Zap, Flame, X } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import "@/components/progress/gamification.css";

interface ChallengeCompleteModalProps {
  open: boolean;
  onClose: () => void;
  xpEarned: number;
  totalXp: number;
  streak?: { current: number; longest: number };
  challengeTitle: string;
}

export function ChallengeCompleteModal({
  open,
  onClose,
  xpEarned,
  totalXp,
  streak,
  challengeTitle,
}: ChallengeCompleteModalProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        className="sm:max-w-md border-none bg-gradient-to-b from-primary/10 to-background p-0 overflow-hidden"
        onPointerDownOutside={onClose}
        onEscapeKeyDown={onClose}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </button>

        <div className="p-6">
          {/* Trophy icon with animation */}
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse" />
              <Trophy className="relative h-16 w-16 text-primary gf-trophy-bounce" />
            </div>
          </div>

          {/* Title */}
          <DialogHeader className="text-center mb-4">
            <DialogTitle className="text-2xl font-bold text-foreground">
              Challenge Complete!
            </DialogTitle>
            <p className="text-muted-foreground mt-2">{challengeTitle}</p>
          </DialogHeader>

          {/* XP Bonus */}
          <div className="bg-card/50 rounded-lg border border-border p-4 mb-4">
            <div className="flex items-center justify-center gap-3">
              <Zap
                className="h-8 w-8 text-[oklch(0.68_0.16_142)] gf-xp-pulse"
                fill="currentColor"
              />
              <div>
                <div className="text-3xl font-bold text-foreground tabular-nums">
                  +{xpEarned}
                </div>
                <div className="text-xs text-muted-foreground uppercase tracking-wider">
                  Bonus XP
                </div>
              </div>
            </div>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-3 mb-6">
            <div className="bg-card/30 rounded-lg border border-border p-3 text-center">
              <Zap className="h-5 w-5 text-[oklch(0.68_0.16_142)] mx-auto mb-1" />
              <div className="text-lg font-bold text-foreground tabular-nums">
                {totalXp.toLocaleString()}
              </div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider">
                Total XP
              </div>
            </div>

            {streak && (
              <div className="bg-card/30 rounded-lg border border-border p-3 text-center">
                <Flame
                  className={cn(
                    "h-5 w-5 mx-auto mb-1",
                    streak.current > 0
                      ? "text-[oklch(0.77_0.16_77)] gf-streak-flame"
                      : "text-muted-foreground"
                  )}
                  fill={streak.current > 0 ? "currentColor" : "none"}
                />
                <div className="text-lg font-bold text-foreground tabular-nums">
                  {streak.current}
                </div>
                <div className="text-[10px] text-muted-foreground uppercase tracking-wider">
                  Day Streak
                </div>
              </div>
            )}
          </div>

          {/* Confetti effect placeholder - CSS animation in gamification.css */}

          {/* Close button */}
          <Button onClick={onClose} className="w-full">
            Continue Learning
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
