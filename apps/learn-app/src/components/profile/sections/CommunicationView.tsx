import React from "react";
import type { CommunicationSection } from "@/lib/learner-profile-types";

export function CommunicationView({ data }: { data: unknown }) {
  const comm = data as CommunicationSection;
  return (
    <dl className="space-y-3 text-sm">
      <div>
        <dt className="font-medium text-muted-foreground">
          Language Complexity
        </dt>
        <dd className="capitalize">
          {comm?.language_complexity || "Not set"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">
          Preferred Structure
        </dt>
        <dd className="capitalize">
          {comm?.preferred_structure?.replace(/-/g, " ") || "Not set"}
        </dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Verbosity</dt>
        <dd className="capitalize">{comm?.verbosity || "Not set"}</dd>
      </div>
      <div>
        <dt className="font-medium text-muted-foreground">Tone</dt>
        <dd className="capitalize">
          {comm?.tone?.replace(/-/g, " ") || "Not set"}
        </dd>
      </div>
      {comm?.analogy_domain && (
        <div>
          <dt className="font-medium text-muted-foreground">Analogy Domain</dt>
          <dd>{comm.analogy_domain}</dd>
        </div>
      )}
    </dl>
  );
}
