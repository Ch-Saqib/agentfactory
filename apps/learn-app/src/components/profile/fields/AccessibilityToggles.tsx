import React from "react";
import type { AccessibilitySection } from "@/lib/learner-profile-types";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { ACCESSIBILITY_TOGGLES } from "@/lib/profile-field-definitions";

interface AccessibilityTogglesProps {
  value: AccessibilitySection;
  onChange: (value: AccessibilitySection) => void;
  includeColorBlindSafe?: boolean;
}

export function AccessibilityToggles({
  value,
  onChange,
  includeColorBlindSafe,
}: AccessibilityTogglesProps) {
  const toggles = ACCESSIBILITY_TOGGLES.filter(
    (toggle) =>
      toggle.key !== "color_blind_safe" || (includeColorBlindSafe ?? true),
  );

  type ToggleKey = "screen_reader" | "dyslexia_friendly" | "color_blind_safe";

  const handleToggle = (key: string) => {
    onChange({ ...value, [key]: !value[key as ToggleKey] });
  };

  return (
    <fieldset className="space-y-4">
      <legend className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        Accessibility Options
      </legend>
      <div className="space-y-3 mt-4">
        {toggles.map((toggle) => (
          <div
            key={toggle.key}
            className="flex items-center justify-between gap-4 rounded-xl border-2 border-border/50 bg-background/50 p-4 transition-colors hover:border-border/80"
          >
            <div className="space-y-1">
              <Label
                className="text-base font-medium leading-none cursor-pointer"
                htmlFor={toggle.key}
              >
                {toggle.label}
              </Label>
              <p className="text-sm text-muted-foreground pt-1">
                {toggle.hint}
              </p>
            </div>
            <Switch
              id={toggle.key}
              checked={value[toggle.key as ToggleKey]}
              onCheckedChange={() => handleToggle(toggle.key)}
              className="data-[state=checked]:bg-primary"
            />
          </div>
        ))}
      </div>
    </fieldset>
  );
}
