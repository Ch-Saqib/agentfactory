import React, { useState, useEffect, useRef } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Brain, X, Check, RotateCcw } from "lucide-react";
import {
  getCheckpoint,
  submitCheckpointAnswer,
  type CheckpointResponse,
  type CheckpointAnswerResponse,
} from "@/lib/progress-api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useProgress } from "@/contexts/ProgressContext";
import "@/components/progress/gamification.css";

interface KnowledgeCheckpointProps {
  lessonSlug: string;
  positionPct: number; // 50 or 75
  open: boolean;
  onClose: () => void;
  onAnswered?: (correct: boolean) => void;
}

export function KnowledgeCheckpoint({
  lessonSlug,
  positionPct,
  open,
  onClose,
  onAnswered,
}: KnowledgeCheckpointProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8002";

  const [checkpoint, setCheckpoint] = useState<CheckpointResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<CheckpointAnswerResponse | null>(null);

  const { refreshProgress } = useProgress();
  const hasShownRef = useRef(false);

  useEffect(() => {
    if (open && !hasShownRef.current) {
      hasShownRef.current = true;
      loadCheckpoint();
    }
  }, [open, lessonSlug, positionPct]);

  async function loadCheckpoint() {
    try {
      setLoading(true);
      const data = await getCheckpoint(progressApiUrl, lessonSlug, positionPct);
      setCheckpoint(data);
    } catch (err) {
      console.error("Failed to load checkpoint:", err);
      onClose();
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit() {
    if (selectedAnswer === null || !checkpoint) return;

    try {
      setSubmitting(true);
      const data = await submitCheckpointAnswer(progressApiUrl, {
        checkpoint_id: checkpoint.id,
        answer: selectedAnswer,
      });
      setResult(data);
      onAnswered?.(data.correct);

      // Refresh progress to update XP display if answer was correct
      if (data.correct && data.xp_awarded > 0) {
        await refreshProgress();
      }
    } catch (err) {
      console.error("Failed to submit answer:", err);
    } finally {
      setSubmitting(false);
    }
  }

  function handleContinue() {
    onClose();
    // Reset state after delay
    setTimeout(() => {
      setCheckpoint(null);
      setSelectedAnswer(null);
      setResult(null);
      hasShownRef.current = false;
    }, 300);
  }

  if (!checkpoint) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={handleContinue}>
      <DialogContent
        className="sm:max-w-lg"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => {
          if (!result) e.preventDefault();
        }}
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            Knowledge Checkpoint
          </DialogTitle>
        </DialogHeader>

        <div className="mt-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : result ? (
            // Result view
            <div className="text-center py-4">
              <div
                className={cn(
                  "w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4",
                  result.correct
                    ? "bg-green-100 dark:bg-green-900/20"
                    : "bg-orange-100 dark:bg-orange-900/20"
                )}
              >
                {result.correct ? (
                  <Check className="h-8 w-8 text-green-600 dark:text-green-400" />
                ) : (
                  <RotateCcw className="h-8 w-8 text-orange-600 dark:text-orange-400" />
                )}
              </div>

              <h3
                className={cn(
                  "text-lg font-semibold mb-2",
                  result.correct ? "text-green-600 dark:text-green-400" : "text-orange-600 dark:text-orange-400"
                )}
              >
                {result.correct ? "Correct!" : "Not quite right"}
              </h3>

              <p className="text-sm text-muted-foreground mb-4">
                {result.explanation}
              </p>

              {!result.correct && (
                <p className="text-xs text-muted-foreground mb-4">
                  The correct answer was option #{result.correct_answer + 1}
                </p>
              )}

              {result.xp_awarded > 0 && (
                <div className="inline-flex items-center gap-1 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
                  <span>+{result.xp_awarded} XP</span>
                </div>
              )}

              <Button onClick={handleContinue} className="w-full">
                Continue Reading
              </Button>
            </div>
          ) : (
            // Question view
            <div className="space-y-4">
              <div>
                <h3 className="text-base font-medium text-foreground mb-3">
                  {checkpoint.question.question}
                </h3>

                <div className="space-y-2">
                  {checkpoint.question.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedAnswer(index)}
                      disabled={submitting}
                      className={cn(
                        "w-full text-left p-3 rounded-lg border transition-all",
                        "hover:bg-accent",
                        selectedAnswer === index
                          ? "border-primary bg-primary/10 ring-1 ring-primary"
                          : "border-border"
                      )}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={cn(
                            "flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium",
                            selectedAnswer === index
                              ? "border-primary bg-primary text-primary-foreground"
                              : "border-muted-foreground text-muted-foreground"
                          )}
                        >
                          {String.fromCharCode(65 + index)}
                        </div>
                        <span className="text-sm">{option}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2">
                <Button
                  variant="outline"
                  onClick={handleContinue}
                  disabled={submitting}
                >
                  Skip
                </Button>

                <Button
                  onClick={handleSubmit}
                  disabled={selectedAnswer === null || submitting}
                >
                  {submitting ? "Checking..." : "Submit Answer"}
                </Button>
              </div>

              <p className="text-xs text-muted-foreground text-center">
                Bonus XP: {checkpoint.xp_bonus}
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
