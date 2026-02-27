import React from "react";
import type { ExpertiseSection } from "@/lib/learner-profile-types";
import { ExpertiseLevelSelect } from "@/components/profile/fields/ExpertiseLevelSelect";

export function ExpertiseEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const expertise = data as ExpertiseSection;

  const updateNested = (
    path: "programming" | "ai_fluency" | "business",
    value: string,
  ) => {
    onChange({
      ...expertise,
      [path]: { ...expertise[path], level: value },
    });
  };

  return (
    <div className="space-y-4">
      <ExpertiseLevelSelect
        label="Programming"
        value={expertise?.programming?.level || "none"}
        onChange={(v) => updateNested("programming", v)}
      />
      <ExpertiseLevelSelect
        label="AI Fluency"
        value={expertise?.ai_fluency?.level || "none"}
        onChange={(v) => updateNested("ai_fluency", v)}
      />
      <ExpertiseLevelSelect
        label="Business Strategy"
        value={expertise?.business?.level || "none"}
        onChange={(v) => updateNested("business", v)}
      />
    </div>
  );
}
