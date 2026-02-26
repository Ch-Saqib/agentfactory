import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import { SECTION_NAMES } from "@/lib/learner-profile-types";
import type { SectionName } from "@/lib/learner-profile-types";
import { ProfileSectionCard } from "./ProfileSectionCard";
import { CompletenessBanner } from "./CompletenessBanner";
import { DangerZone } from "./DangerZone";
import * as sections from "./sections";

const SECTION_COMPONENTS: Record<
  SectionName,
  { View: React.ComponentType<{ data: unknown }>; Edit: React.ComponentType<{ data: unknown; onChange: (data: unknown) => void }> }
> = {
  goals: { View: sections.GoalsView, Edit: sections.GoalsEdit },
  expertise: { View: sections.ExpertiseView, Edit: sections.ExpertiseEdit },
  professional_context: {
    View: sections.ProfessionalView,
    Edit: sections.ProfessionalEdit,
  },
  communication: {
    View: sections.CommunicationView,
    Edit: sections.CommunicationEdit,
  },
  delivery: { View: sections.DeliveryView, Edit: sections.DeliveryEdit },
  accessibility: {
    View: sections.AccessibilityView,
    Edit: sections.AccessibilityEdit,
  },
};

export default function ProfileSettings() {
  const { session } = useAuth();
  const { profile, isLoading } = useLearnerProfile();

  if (!session?.user) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <p className="text-muted-foreground">
          Sign in to view your learning profile.
        </p>
      </div>
    );
  }

  if (isLoading && !profile) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <p className="text-muted-foreground">Loading your profile...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <p className="text-muted-foreground">
          No profile found.{" "}
          <a href="/onboarding" className="text-primary hover:underline">
            Set up your profile
          </a>
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-8 space-y-6">
      <h1 className="text-2xl font-bold">My Learning Profile</h1>
      <CompletenessBanner />
      {SECTION_NAMES.map((section) => {
        const components = SECTION_COMPONENTS[section];
        if (!components) return null;
        return (
          <ProfileSectionCard
            key={section}
            section={section}
            ViewComponent={components.View}
            EditComponent={components.Edit}
          />
        );
      })}
      <DangerZone />
    </div>
  );
}
