import React, { useState, useMemo } from "react";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import { useAuth } from "@/contexts/AuthContext";
import { useLearnerProfileEnabled } from "@/lib/api-utils";
import { X, Sparkles } from "lucide-react";
import useBaseUrl from "@docusaurus/useBaseUrl";
import { useHistory } from "@docusaurus/router";

/**
 * Inline soft nudge shown inside feature panels (TeachMe, etc.)
 * when the user hasn't completed onboarding.
 * Dismissible per-session — reappears next session.
 */
export function ProfileSoftNudge() {
  const enabled = useLearnerProfileEnabled();
  const { session } = useAuth();
  const { profile, needsOnboarding, isLoading } = useLearnerProfile();
  const [dismissed, setDismissed] = useState(false);
  const history = useHistory();
  const onboardingHref = useBaseUrl("/onboarding");

  const userId = session?.user?.id;
  const isOptedOut = useMemo(() => {
    if (!userId || typeof window === "undefined") return false;
    try {
      return localStorage.getItem(`learner_profile_opt_out:${userId}`) === "1";
    } catch {
      return false;
    }
  }, [userId]);

  if (
    !enabled ||
    dismissed ||
    isLoading ||
    isOptedOut ||
    !session?.user ||
    (profile?.onboarding_completed && !needsOnboarding)
  ) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 px-3 py-2 text-xs bg-primary/5 border-b border-primary/10 text-muted-foreground">
      <Sparkles className="h-3.5 w-3.5 text-primary shrink-0" />
      <span>
        <button
          type="button"
          onClick={() => history.push(onboardingHref)}
          className="font-medium text-primary hover:underline"
        >
          Complete your profile
        </button>{" "}
        for personalized responses.
      </span>
      <button
        type="button"
        onClick={() => setDismissed(true)}
        className="ml-auto p-0.5 hover:text-foreground rounded"
        aria-label="Dismiss"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
}
