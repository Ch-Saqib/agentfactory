import React from "react";
import type { ProfessionalContextSection } from "@/lib/learner-profile-types";

interface ProfessionalStepProps {
  data: ProfessionalContextSection;
  onChange: (data: ProfessionalContextSection) => void;
}

export function ProfessionalStep({ data, onChange }: ProfessionalStepProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Professional Context</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Tell us about your work context (all optional).
        </p>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="current-role" className="text-sm font-medium">
          Current Role
        </label>
        <input
          id="current-role"
          type="text"
          value={data.current_role || ""}
          onChange={(e) =>
            onChange({ ...data, current_role: e.target.value || null })
          }
          placeholder="e.g., Software Engineer, Product Manager"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          maxLength={100}
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="industry" className="text-sm font-medium">
          Industry
        </label>
        <input
          id="industry"
          type="text"
          value={data.industry || ""}
          onChange={(e) =>
            onChange({ ...data, industry: e.target.value || null })
          }
          placeholder="e.g., Technology, Healthcare, Finance"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          maxLength={100}
        />
      </div>
      <div className="space-y-1.5">
        <label htmlFor="org-type" className="text-sm font-medium">
          Organization Type (optional)
        </label>
        <select
          id="org-type"
          value={data.organization_type || ""}
          onChange={(e) =>
            onChange({ ...data, organization_type: e.target.value || null })
          }
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          <option value="">Select...</option>
          <option value="startup">Startup</option>
          <option value="small_business">Small Business</option>
          <option value="enterprise">Enterprise</option>
          <option value="non_profit">Non-Profit</option>
          <option value="education">Education</option>
          <option value="government">Government</option>
          <option value="freelance">Freelance/Independent</option>
        </select>
      </div>
    </div>
  );
}
