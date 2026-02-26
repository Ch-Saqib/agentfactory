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
    path: "programming" | "ai_ml" | "business",
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
        label="AI / ML"
        value={expertise?.ai_ml?.level || "none"}
        onChange={(v) => updateNested("ai_ml", v)}
      />
      <ExpertiseLevelSelect
        label="Business"
        value={expertise?.business?.level || "none"}
        onChange={(v) => updateNested("business", v)}
      />
    </div>
  );
}
