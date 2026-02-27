import React, { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";

/**
 * Initializes the LearnerProfileContext for authenticated users.
 * Does NOT force redirects to /onboarding anymore, allowing a progressively 
 * disclosed "opt-in" personalization strategy.
 */
export function RequireProfile({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  const { needsOnboarding, isLoading } = useLearnerProfile();

  // We maintain the hook to ensure useLearnerProfile triggers its lazy load 
  // on mount for authenticated users, but we no longer block them or redirect them.
  useEffect(() => {
    if (!session?.user || isLoading) return;

    // The profile is checked, if they need onboarding, we will just let 
    // the ProfileNudgeBanner (in Root.tsx) handle the messaging.
  }, [session?.user, needsOnboarding, isLoading]);

  return <>{children}</>;
}
