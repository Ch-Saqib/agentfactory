import React from "react";
import type { GoalsSection } from "@/lib/learner-profile-types";
import { Badge } from "@/components/ui/badge";

export function GoalsView({ data }: { data: unknown }) {
  const goals = data as GoalsSection;
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Primary Goal</div>
        <div className="text-lg font-medium leading-snug">{goals?.primary_learning_goal || "Not set"}</div>
      </div>

      <div className="space-y-2">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Urgency</div>
        <Badge variant={goals?.urgency === "high" ? "destructive" : goals?.urgency === "medium" ? "default" : "secondary"} className="text-sm px-3 py-1 capitalize">
          {goals?.urgency || "Not set"}
        </Badge>
      </div>

      {(goals?.career_goal || goals?.immediate_application) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border/50">
          {goals?.career_goal && (
            <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
              <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Career Goal</div>
              <div className="text-sm">{goals.career_goal}</div>
            </div>
          )}
          {goals?.immediate_application && (
            <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
              <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Immediate Application</div>
              <div className="text-sm">{goals.immediate_application}</div>
            </div>
          )}
        </div>
      )}

      {goals?.secondary_goals?.length > 0 && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Secondary Goals</div>
          <div className="flex flex-wrap gap-2">
            {goals.secondary_goals.map((g, i) => (
              <Badge key={i} variant="outline" className="text-sm px-3 py-1">
                {g}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
