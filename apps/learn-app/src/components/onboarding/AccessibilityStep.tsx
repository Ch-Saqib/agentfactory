import React from "react";
import { AccessibilityToggles } from "@/components/profile/fields";
import type { AccessibilitySection } from "@/lib/learner-profile-types";

interface AccessibilityStepProps {
  data: AccessibilitySection;
  onChange: (data: AccessibilitySection) => void;
}

export function AccessibilityStep({ data, onChange }: AccessibilityStepProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Accessibility Preferences</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Help us make your experience comfortable.
        </p>
      </div>
      <AccessibilityToggles value={data} onChange={onChange} />
      <fieldset className="space-y-2">
        <legend className="text-sm font-medium">
          Cognitive Load Preference
        </legend>
        <div className="space-y-2">
          {(["standard", "reduced"] as const).map((option) => (
            <label
              key={option}
              className="flex items-center gap-3 rounded-md border border-input p-3 cursor-pointer hover:bg-accent/50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent"
            >
              <input
                type="radio"
                name="onboarding-cognitive-load"
                value={option}
                checked={data.cognitive_load_preference === option}
                onChange={() =>
                  onChange({ ...data, cognitive_load_preference: option })
                }
              />
              <div>
                <div className="text-sm font-medium capitalize">{option}</div>
                <div className="text-xs text-muted-foreground">
                  {option === "standard"
                    ? "Regular content density"
                    : "Simplified, less content per page"}
                </div>
              </div>
            </label>
          ))}
        </div>
      </fieldset>
      <div className="space-y-1.5">
        <label htmlFor="onboarding-a11y-notes" className="text-sm font-medium">
          Additional Notes (optional)
        </label>
        <textarea
          id="onboarding-a11y-notes"
          value={data.notes || ""}
          onChange={(e) =>
            onChange({ ...data, notes: e.target.value || null })
          }
          placeholder="Any other accessibility needs..."
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 min-h-[80px]"
          maxLength={300}
        />
      </div>
    </div>
  );
}
