import React from "react";
import type { CommunicationSection } from "@/lib/learner-profile-types";
import { Badge } from "@/components/ui/badge";

export function CommunicationView({ data }: { data: unknown }) {
  const comm = data as CommunicationSection;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Language Complexity</div>
          <Badge variant={comm?.language_complexity === "expert" ? "default" : "secondary"} className="text-sm px-3 py-1 capitalize">
            {comm?.language_complexity || "Not set"}
          </Badge>
        </div>
        <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Verbosity</div>
          <Badge variant={comm?.verbosity === "detailed" ? "outline" : "secondary"} className="text-sm px-3 py-1 capitalize">
            {comm?.verbosity || "Not set"}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border/50">
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Preferred Structure</div>
          <div className="text-sm font-medium capitalize bg-accent/20 px-4 py-3 rounded-xl border border-border/50">
            {comm?.preferred_structure?.replace(/-/g, " ") || "Not set"}
          </div>
        </div>
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Tone</div>
          <div className="text-sm font-medium capitalize bg-accent/20 px-4 py-3 rounded-xl border border-border/50">
            {comm?.tone?.replace(/-/g, " ") || "Not set"}
          </div>
        </div>
      </div>

      {comm?.analogy_domain && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Analogy Domain</div>
          <div className="text-sm bg-accent/20 border border-border/50 rounded-xl p-4">
            {comm.analogy_domain}
          </div>
        </div>
      )}
    </div>
  );
}
