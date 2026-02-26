import React from "react";

const URGENCY_OPTIONS = [
  { value: "low", label: "Low", description: "Learning at my own pace" },
  { value: "medium", label: "Medium", description: "Want to make steady progress" },
  { value: "high", label: "High", description: "Need to learn quickly" },
] as const;

interface UrgencyRadioProps {
  value: string | null;
  onChange: (value: string) => void;
}

export function UrgencyRadio({ value, onChange }: UrgencyRadioProps) {
  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium">Learning Urgency</legend>
      <div className="space-y-2">
        {URGENCY_OPTIONS.map((option) => (
          <label
            key={option.value}
            className="flex items-start gap-3 rounded-md border border-input p-3 cursor-pointer hover:bg-accent/50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-accent"
          >
            <input
              type="radio"
              name="urgency"
              value={option.value}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className="mt-0.5"
            />
            <div>
              <div className="text-sm font-medium">{option.label}</div>
              <div className="text-xs text-muted-foreground">{option.description}</div>
            </div>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
