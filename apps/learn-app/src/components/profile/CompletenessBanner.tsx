import React from "react";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";

export function CompletenessBanner() {
  const { profile } = useLearnerProfile();
  if (!profile || profile.profile_completeness >= 50) return null;

  const percent = Math.round(profile.profile_completeness);

  return (
    <div className="rounded-lg border border-border bg-card p-4 mb-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">
          Profile {percent}% complete
        </span>
        <a href="/profile" className="text-sm text-primary hover:underline">
          Complete your profile
        </a>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
