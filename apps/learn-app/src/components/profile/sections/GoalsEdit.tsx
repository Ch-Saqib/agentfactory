import React from "react";
import type { GoalsSection } from "@/lib/learner-profile-types";
import { UrgencyRadio } from "@/components/profile/fields/UrgencyRadio";

export function GoalsEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const goals = data as GoalsSection;

  const update = (field: keyof GoalsSection, value: unknown) => {
    onChange({ ...goals, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label
          htmlFor="settings-primary-goal"
          className="text-sm font-medium"
        >
          Primary Learning Goal
        </label>
        <input
          id="settings-primary-goal"
          type="text"
          value={goals?.primary_learning_goal || ""}
          onChange={(e) =>
            update("primary_learning_goal", e.target.value || null)
          }
          placeholder="What do you most want to learn?"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
      <UrgencyRadio
        value={goals?.urgency || null}
        onChange={(v) => update("urgency", v)}
        name="settings-urgency"
      />
      <div className="space-y-1.5">
        <label
          htmlFor="settings-career-goal"
          className="text-sm font-medium"
        >
          Career Goal
        </label>
        <input
          id="settings-career-goal"
          type="text"
          value={goals?.career_goal || ""}
          onChange={(e) => update("career_goal", e.target.value || null)}
          placeholder="Where do you want your career to go?"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
      <div className="space-y-1.5">
        <label
          htmlFor="settings-immediate-application"
          className="text-sm font-medium"
        >
          Immediate Application
        </label>
        <input
          id="settings-immediate-application"
          type="text"
          value={goals?.immediate_application || ""}
          onChange={(e) =>
            update("immediate_application", e.target.value || null)
          }
          placeholder="What will you use this knowledge for right away?"
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        />
      </div>
    </div>
  );
}
