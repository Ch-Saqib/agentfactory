import React from "react";
import type { AccessibilitySection } from "@/lib/learner-profile-types";
import { Badge } from "@/components/ui/badge";

export function AccessibilityView({ data }: { data: unknown }) {
  const a11y = data as AccessibilitySection;

  const enabledFeatures: string[] = [];
  if (a11y?.screen_reader) enabledFeatures.push("Screen Reader");
  if (a11y?.dyslexia_friendly) enabledFeatures.push("Dyslexia-Friendly");
  if (a11y?.color_blind_safe) enabledFeatures.push("Color Blind Safe");

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Cognitive Load</div>
        <Badge variant={a11y?.cognitive_load_preference === "reduced" ? "secondary" : "default"} className="text-sm px-3 py-1 capitalize">
          {a11y?.cognitive_load_preference || "standard"}
        </Badge>
      </div>

      <div className="space-y-2 pt-4 border-t border-border/50">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Features Enabled</div>
        {enabledFeatures.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {enabledFeatures.map(f => (
              <Badge key={f} variant="outline" className="text-sm px-3 py-1">
                {f}
              </Badge>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground italic">None active</div>
        )}
      </div>

      {a11y?.notes && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Notes</div>
          <div className="text-sm bg-accent/20 border border-border/50 rounded-xl p-4 leading-relaxed whitespace-pre-wrap">
            {a11y.notes}
          </div>
        </div>
      )}
    </div>
  );
}
