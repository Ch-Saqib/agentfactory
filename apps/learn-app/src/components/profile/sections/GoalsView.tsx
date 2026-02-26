import React from "react";
import type { GoalsSection } from "@/lib/learner-profile-types";

export function GoalsView({ data }: { data: unknown }) {
  const goals = data as GoalsSection;
  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">Primary Goal</dt>
        <dd>{goals?.primary_learning_goal || "Not set"}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Urgency</dt>
        <dd className="capitalize">{goals?.urgency || "Not set"}</dd>
      </div>
      {goals?.career_goal && (
        <div>
          <dt className="font-medium text-muted-foreground">Career Goal</dt>
          <dd>{goals.career_goal}</dd>
        </div>
      )}
      {goals?.immediate_application && (
        <div>
          <dt className="font-medium text-muted-foreground">
            Immediate Application
          </dt>
          <dd>{goals.immediate_application}</dd>
        </div>
      )}
      {goals?.secondary_goals?.length > 0 && (
        <div>
          <dt className="font-medium text-muted-foreground">
            Secondary Goals
          </dt>
          <dd>
            <ul className="list-disc list-inside">
              {goals.secondary_goals.map((g, i) => (
                <li key={i}>{g}</li>
              ))}
            </ul>
          </dd>
        </div>
      )}
    </dl>
  );
}
