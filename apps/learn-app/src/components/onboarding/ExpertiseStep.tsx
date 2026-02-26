import React from "react";
import { ExpertiseLevelSelect } from "@/components/profile/fields";
import type { ExpertiseSection } from "@/lib/learner-profile-types";

interface ExpertiseStepProps {
  data: ExpertiseSection;
  onChange: (data: ExpertiseSection) => void;
}

export function ExpertiseStep({ data, onChange }: ExpertiseStepProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Expertise &amp; Skills</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Help us understand your current skill levels.
        </p>
      </div>
      <ExpertiseLevelSelect
        label="Programming"
        value={data.programming.level}
        onChange={(level) =>
          onChange({
            ...data,
            programming: { ...data.programming, level: level as any },
          })
        }
      />
      <ExpertiseLevelSelect
        label="AI & Machine Learning"
        value={data.ai_ml.level}
        onChange={(level) =>
          onChange({
            ...data,
            ai_ml: { ...data.ai_ml, level: level as any },
          })
        }
      />
      <ExpertiseLevelSelect
        label="Business"
        value={data.business.level}
        onChange={(level) =>
          onChange({
            ...data,
            business: { ...data.business, level: level as any },
          })
        }
      />
      <div className="space-y-3">
        <div className="space-y-1.5">
          <label htmlFor="domain-name" className="text-sm font-medium">
            Domain Expertise (optional)
          </label>
          <input
            id="domain-name"
            type="text"
            value={data.domain[0]?.domain_name || ""}
            onChange={(e) => {
              const domain =
                data.domain.length > 0
                  ? [...data.domain]
                  : [
                      {
                        level: "beginner" as const,
                        domain_name: null,
                        is_primary: true,
                        notes: null,
                      },
                    ];
              domain[0] = { ...domain[0], domain_name: e.target.value || null };
              onChange({ ...data, domain });
            }}
            placeholder="e.g., Healthcare, Finance, Education"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            maxLength={100}
          />
        </div>
        {data.domain[0]?.domain_name && (
          <ExpertiseLevelSelect
            label="Domain Level"
            value={data.domain[0]?.level || "beginner"}
            onChange={(level) => {
              const domain = [...data.domain];
              domain[0] = { ...domain[0], level: level as any };
              onChange({ ...data, domain });
            }}
          />
        )}
      </div>
    </div>
  );
}
