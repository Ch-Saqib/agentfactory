import React from "react";
import type { AccessibilitySection } from "@/lib/learner-profile-types";

interface AccessibilityTogglesProps {
  value: AccessibilitySection;
  onChange: (value: AccessibilitySection) => void;
}

const TOGGLES = [
  { key: "screen_reader" as const, label: "Screen Reader", description: "Optimize content for screen reader users" },
  { key: "dyslexia_friendly" as const, label: "Dyslexia-Friendly", description: "Use dyslexia-friendly formatting" },
  { key: "color_blind_safe" as const, label: "Color Blind Safe", description: "Avoid relying on color alone for information" },
] as const;

export function AccessibilityToggles({ value, onChange }: AccessibilityTogglesProps) {
  const handleToggle = (key: "screen_reader" | "dyslexia_friendly" | "color_blind_safe") => {
    onChange({ ...value, [key]: !value[key] });
  };

  return (
    <fieldset className="space-y-3">
      <legend className="text-sm font-medium">Accessibility Options</legend>
      {TOGGLES.map((toggle) => (
        <label key={toggle.key} className="flex items-center justify-between gap-3 rounded-md border border-input p-3 cursor-pointer hover:bg-accent/50 transition-colors">
          <div>
            <div className="text-sm font-medium">{toggle.label}</div>
            <div className="text-xs text-muted-foreground">{toggle.description}</div>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={value[toggle.key]}
            aria-label={toggle.label}
            onClick={() => handleToggle(toggle.key)}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
              value[toggle.key] ? "bg-primary" : "bg-muted"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-background shadow-lg ring-0 transition-transform ${
                value[toggle.key] ? "translate-x-5" : "translate-x-0"
              }`}
            />
          </button>
        </label>
      ))}
    </fieldset>
  );
}
