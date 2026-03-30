import React from "react";

interface WizardProgressProps {
  steps: readonly { key: string; label: string }[];
  currentStep: number;
  completedSteps: Set<number>;
}

export function WizardProgress({
  steps,
  currentStep,
  completedSteps,
}: WizardProgressProps) {
  return (
    <nav aria-label="Onboarding progress" className="mb-8">
      <ol className="flex items-center gap-2">
        {steps.map((step, index) => {
          const isActive = index === currentStep;
          const isComplete = completedSteps.has(index);
          const isPending = !isActive && !isComplete;

          return (
            <li
              key={step.key}
              className="flex items-center gap-2 flex-1"
            >
              <div className="flex flex-col items-center flex-1 min-w-0">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold border-2 transition-colors ${
                    isActive
                      ? "border-primary bg-primary text-primary-foreground"
                      : isComplete
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-muted bg-muted text-muted-foreground"
                  }`}
                  role="img"
                  aria-label={`Step ${index + 1}: ${step.label} — ${isActive ? "current" : isComplete ? "completed" : "not started"}`}
                  aria-current={isActive ? "step" : undefined}
                  data-testid={`step-indicator-${index}`}
                >
                  {isComplete ? (
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    index + 1
                  )}
                </div>
                <span
                  className={`text-xs mt-1 truncate max-w-full text-center ${
                    isActive
                      ? "font-semibold text-foreground"
                      : isPending
                        ? "text-muted-foreground"
                        : "text-foreground"
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`h-0.5 flex-1 min-w-[16px] ${
                    isComplete ? "bg-primary" : "bg-muted"
                  }`}
                  aria-hidden="true"
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
