import React from "react";
import type { ProfessionalContextSection } from "@/lib/learner-profile-types";

const ORG_TYPES = [
  { value: "", label: "Select..." },
  { value: "startup", label: "Startup" },
  { value: "enterprise", label: "Enterprise" },
  { value: "agency", label: "Agency" },
  { value: "freelance", label: "Freelance" },
  { value: "academic", label: "Academic" },
  { value: "nonprofit", label: "Nonprofit" },
  { value: "government", label: "Government" },
];

export function ProfessionalEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const ctx = data as ProfessionalContextSection;

  const update = (field: keyof ProfessionalContextSection, value: unknown) => {
    onChange({ ...ctx, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label htmlFor="settings-current-role" className="text-sm font-medium">
          Current Role
        </label>
        <input
          id="settings-current-role"
          type="text"
          value={ctx?.current_role || ""}
          onChange={(e) => update("current_role", e.target.value || null)}
          placeholder="e.g. Senior Developer"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-industry" className="text-sm font-medium">
          Industry
        </label>
        <input
          id="settings-industry"
          type="text"
          value={ctx?.industry || ""}
          onChange={(e) => update("industry", e.target.value || null)}
          placeholder="e.g. FinTech, Healthcare"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-org-type" className="text-sm font-medium">
          Organization Type
        </label>
        <select
          id="settings-org-type"
          value={ctx?.organization_type || ""}
          onChange={(e) => update("organization_type", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {ORG_TYPES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-team-context" className="text-sm font-medium">
          Team Context
        </label>
        <input
          id="settings-team-context"
          type="text"
          value={ctx?.team_context || ""}
          onChange={(e) => update("team_context", e.target.value || null)}
          placeholder="e.g. 5-person engineering team"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
    </div>
  );
}
