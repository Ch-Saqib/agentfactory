import React from "react";
import type { ProfessionalContextSection } from "@/lib/learner-profile-types";

export function ProfessionalView({ data }: { data: unknown }) {
  const ctx = data as ProfessionalContextSection;
  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">Current Role</dt>
        <dd>{ctx?.current_role || "Not set"}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Industry</dt>
        <dd>{ctx?.industry || "Not set"}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">
          Organization Type
        </dt>
        <dd className="capitalize">{ctx?.organization_type || "Not set"}</dd>
      </div>
      {ctx?.team_context && (
        <div>
          <dt className="font-medium text-muted-foreground">Team Context</dt>
          <dd>{ctx.team_context}</dd>
        </div>
      )}
      {ctx?.tools_in_use?.length > 0 && (
        <div>
          <dt className="font-medium text-muted-foreground">Tools in Use</dt>
          <dd>{ctx.tools_in_use.join(", ")}</dd>
        </div>
      )}
    </dl>
  );
}
