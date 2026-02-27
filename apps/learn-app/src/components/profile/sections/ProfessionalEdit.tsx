import React from "react";
import type { ProfessionalContextSection } from "@/lib/learner-profile-types";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
        <Input
          id="settings-current-role"
          type="text"
          value={ctx?.current_role || ""}
          onChange={(e) => update("current_role", e.target.value || null)}
          placeholder="e.g. Senior Developer"
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-industry" className="text-sm font-medium">
          Industry
        </label>
        <Input
          id="settings-industry"
          type="text"
          value={ctx?.industry || ""}
          onChange={(e) => update("industry", e.target.value || null)}
          placeholder="e.g. FinTech, Healthcare"
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-org-type" className="text-sm font-medium">
          Organization Type
        </label>
        <Select
          value={ctx?.organization_type || "none"}
          onValueChange={(val) => update("organization_type", val === "none" ? null : val)}
        >
          <SelectTrigger id="settings-org-type" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {ORG_TYPES.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="settings-team-context" className="text-sm font-medium">
          Team Context
        </label>
        <Input
          id="settings-team-context"
          type="text"
          value={ctx?.team_context || ""}
          onChange={(e) => update("team_context", e.target.value || null)}
          placeholder="e.g. 5-person engineering team"
        />
      </div>
    </div>
  );
}
