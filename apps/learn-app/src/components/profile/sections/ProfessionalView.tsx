import React from "react";
import type { ProfessionalContextSection } from "@/lib/learner-profile-types";
import { Badge } from "@/components/ui/badge";

export function ProfessionalView({ data }: { data: unknown }) {
  const ctx = data as ProfessionalContextSection;
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Current Role</div>
          <div className="text-base font-medium">{ctx?.current_role || "Not set"}</div>
        </div>
        <div className="space-y-2 border border-border/50 rounded-xl p-4 bg-background/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Industry</div>
          <div className="text-base font-medium">{ctx?.industry || "Not set"}</div>
        </div>
      </div>

      <div className="space-y-2 pt-4 border-t border-border/50">
        <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Organization Type</div>
        <Badge variant={ctx?.organization_type ? "secondary" : "outline"} className="text-sm px-3 py-1 capitalize">
          {ctx?.organization_type ? ctx.organization_type.replace(/_/g, " ") : "Not set"}
        </Badge>
      </div>

      {ctx?.team_context && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Team Context</div>
          <div className="text-sm bg-accent/20 border border-border/50 rounded-xl p-4 leading-relaxed">
            {ctx.team_context}
          </div>
        </div>
      )}

      {ctx?.tools_in_use?.length > 0 && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Tools in Use</div>
          <div className="flex flex-wrap gap-2 pt-1">
            {ctx.tools_in_use.map((tool, i) => (
              <Badge key={i} variant="outline" className="text-sm px-3 py-1 shadow-sm bg-background/50">
                {tool}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {ctx?.real_projects?.length > 0 && (
        <div className="space-y-2 pt-4 border-t border-border/50">
          <div className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Real Projects</div>
          <ul className="list-disc pl-5 text-sm space-y-1 mt-2 text-muted-foreground">
            {ctx.real_projects.map((proj, i) => (
              <li key={i}>
                <span className="font-semibold text-foreground">{proj.project_name}</span>
                {proj.description && <span className="text-muted-foreground"> - {proj.description}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
