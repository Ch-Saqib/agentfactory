import React from "react";
import { UrgencyRadio } from "@/components/profile/fields";
import type { GoalsSection } from "@/lib/learner-profile-types";

interface GoalsStepProps {
  data: GoalsSection;
  onChange: (data: GoalsSection) => void;
}

export function GoalsStep({ data, onChange }: GoalsStepProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Goals &amp; Motivation</h2>
        <p className="text-sm text-muted-foreground mt-1">
          What do you want to learn and why?
        </p>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="primary-goal" className="text-sm font-medium">
          Primary Learning Goal
        </label>
        <input
          id="primary-goal"
          type="text"
          value={data.primary_learning_goal || ""}
          onChange={(e) =>
            onChange({
              ...data,
              primary_learning_goal: e.target.value || null,
            })
          }
          placeholder="e.g., Build AI agents for my business"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          maxLength={500}
        />
      </div>
      <UrgencyRadio
        value={data.urgency}
        onChange={(value) =>
          onChange({ ...data, urgency: value as GoalsSection["urgency"] })
        }
      />
    </div>
  );
}
