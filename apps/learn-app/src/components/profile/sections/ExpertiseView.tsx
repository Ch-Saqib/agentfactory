import React from "react";
import type { ExpertiseSection } from "@/lib/learner-profile-types";

function levelLabel(level: string): string {
  const labels: Record<string, string> = {
    none: "None",
    beginner: "Beginner",
    intermediate: "Intermediate",
    advanced: "Advanced",
    expert: "Expert",
  };
  return labels[level] || level;
}

export function ExpertiseView({ data }: { data: unknown }) {
  const expertise = data as ExpertiseSection;
  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">Programming</dt>
        <dd>{levelLabel(expertise?.programming?.level || "none")}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">AI / ML</dt>
        <dd>{levelLabel(expertise?.ai_ml?.level || "none")}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Business</dt>
        <dd>{levelLabel(expertise?.business?.level || "none")}</dd>
      </div>
      {expertise?.domain?.length > 0 && (
        <div>
          <dt className="font-medium text-muted-foreground">
            Domain Expertise
          </dt>
          <dd>
            <ul className="list-disc list-inside">
              {expertise.domain.map((d, i) => (
                <li key={i}>
                  {d.domain_name || "Unnamed"} — {levelLabel(d.level)}
                </li>
              ))}
            </ul>
          </dd>
        </div>
      )}
    </dl>
  );
}
