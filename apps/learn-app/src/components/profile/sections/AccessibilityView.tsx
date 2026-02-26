import React from "react";
import type { AccessibilitySection } from "@/lib/learner-profile-types";

export function AccessibilityView({ data }: { data: unknown }) {
  const a11y = data as AccessibilitySection;

  const enabledFeatures: string[] = [];
  if (a11y?.screen_reader) enabledFeatures.push("Screen Reader");
  if (a11y?.dyslexia_friendly) enabledFeatures.push("Dyslexia-Friendly");
  if (a11y?.color_blind_safe) enabledFeatures.push("Color Blind Safe");

  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">
          Accessibility Features
        </dt>
        <dd>
          {enabledFeatures.length > 0 ? enabledFeatures.join(", ") : "None enabled"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Cognitive Load</dt>
        <dd className="capitalize">
          {a11y?.cognitive_load_preference || "standard"}
        </dd>
      </div>
      {a11y?.notes && (
        <div>
          <dt className="font-medium text-muted-foreground">Notes</dt>
          <dd>{a11y.notes}</dd>
        </div>
      )}
    </dl>
  );
}
