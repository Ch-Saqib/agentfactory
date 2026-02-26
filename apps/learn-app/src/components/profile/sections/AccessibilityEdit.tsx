import React from "react";
import type { AccessibilitySection } from "@/lib/learner-profile-types";
import { AccessibilityToggles } from "@/components/profile/fields/AccessibilityToggles";

export function AccessibilityEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const a11y = data as AccessibilitySection;

  return (
    <div className="space-y-4">
      <AccessibilityToggles
        value={a11y}
        onChange={(updated) => onChange(updated)}
      />
      <fieldset className="space-y-2">
        <legend className="text-sm font-medium">Cognitive Load</legend>
        <div className="space-y-2">
          {(["standard", "reduced"] as const).map((option) => (
            <label
              key={option}
              className="flex items-center gap-3 rounded-md border border-input p-3 cursor-pointer hover:bg-accent/50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent"
            >
              <input
                type="radio"
                name="cognitive-load"
                value={option}
                checked={a11y?.cognitive_load_preference === option}
                onChange={() =>
                  onChange({ ...a11y, cognitive_load_preference: option })
                }
              />
              <span className="text-sm font-medium capitalize">{option}</span>
            </label>
          ))}
        </div>
      </fieldset>
      <div className="space-y-1.5">
        <label htmlFor="a11y-notes" className="text-sm font-medium">
          Additional Notes
        </label>
        <textarea
          id="a11y-notes"
          value={a11y?.notes || ""}
          onChange={(e) =>
            onChange({ ...a11y, notes: e.target.value || null })
          }
          placeholder="Any other accessibility needs..."
          rows={3}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
    </div>
  );
}
