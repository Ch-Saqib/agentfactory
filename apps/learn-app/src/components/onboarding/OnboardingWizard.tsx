import React, { useState, useEffect, useCallback, useRef } from "react";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import { WizardProgress } from "./WizardProgress";
import { GoalsStep } from "./GoalsStep";
import { ExpertiseStep } from "./ExpertiseStep";
import { ProfessionalStep } from "./ProfessionalStep";
import { AccessibilityStep } from "./AccessibilityStep";
import { ReviewStep } from "./ReviewStep";
import type {
  GoalsSection,
  ExpertiseSection,
  ProfessionalContextSection,
  AccessibilitySection,
  OnboardingPhase,
  ProfileResponse,
} from "@/lib/learner-profile-types";

const STEPS = [
  { key: "goals", label: "Goals", phase: "goals" as const },
  { key: "expertise", label: "Expertise", phase: "expertise" as const },
  {
    key: "professional",
    label: "Professional",
    phase: "professional_context" as const,
  },
  {
    key: "accessibility",
    label: "Accessibility",
    phase: "accessibility" as const,
  },
  { key: "review", label: "Review", phase: "ai_enrichment" as const },
] as const;

const DEFAULT_GOALS: GoalsSection = {
  primary_learning_goal: null,
  secondary_goals: [],
  urgency: null,
  urgency_note: null,
  career_goal: null,
  immediate_application: null,
};

const DEFAULT_EXPERTISE: ExpertiseSection = {
  domain: [],
  programming: { level: "none", languages: [], notes: null },
  ai_ml: { level: "none", notes: null },
  business: { level: "none", notes: null },
  subject_specific: {
    topics_already_mastered: [],
    topics_partially_known: [],
    known_misconceptions: [],
  },
};

const DEFAULT_PROFESSIONAL: ProfessionalContextSection = {
  current_role: null,
  industry: null,
  organization_type: null,
  team_context: null,
  real_projects: [],
  tools_in_use: [],
  constraints: null,
};

const DEFAULT_ACCESSIBILITY: AccessibilitySection = {
  screen_reader: false,
  cognitive_load_preference: "standard",
  color_blind_safe: false,
  dyslexia_friendly: false,
  notes: null,
};

/**
 * Determine the first incomplete onboarding step from a profile's onboarding status.
 * The backend tracks completion via onboarding_progress (0.0 - 1.0) and per-section data.
 */
function resolveResumeStep(profile: ProfileResponse): number {
  // Check each step's section data to determine if it was filled
  const sectionChecks = [
    // Goals: has primary_learning_goal or urgency set
    profile.goals.primary_learning_goal !== null ||
      profile.goals.urgency !== null,
    // Expertise: at least one level changed from "none"
    profile.expertise.programming.level !== "none" ||
      profile.expertise.ai_ml.level !== "none" ||
      profile.expertise.business.level !== "none",
    // Professional: any field filled
    profile.professional_context.current_role !== null ||
      profile.professional_context.industry !== null ||
      profile.professional_context.organization_type !== null,
    // Accessibility: any non-default setting
    profile.accessibility.screen_reader ||
      profile.accessibility.dyslexia_friendly ||
      profile.accessibility.color_blind_safe ||
      profile.accessibility.cognitive_load_preference !== "standard" ||
      profile.accessibility.notes !== null,
  ];

  // Find first incomplete section; if all are complete, go to review
  for (let i = 0; i < sectionChecks.length; i++) {
    if (!sectionChecks[i]) return i;
  }
  return STEPS.length - 1; // review step
}

export default function OnboardingWizard() {
  const {
    profile,
    isLoading: contextLoading,
    needsOnboarding,
    createNewProfile,
    completeOnboardingPhase,
  } = useLearnerProfile();

  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(
    new Set(),
  );
  const [isSaving, setIsSaving] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initDoneRef = useRef(false);

  // Form data state
  const [goalsData, setGoalsData] = useState<GoalsSection>(DEFAULT_GOALS);
  const [expertiseData, setExpertiseData] =
    useState<ExpertiseSection>(DEFAULT_EXPERTISE);
  const [professionalData, setProfessionalData] =
    useState<ProfessionalContextSection>(DEFAULT_PROFESSIONAL);
  const [accessibilityData, setAccessibilityData] =
    useState<AccessibilitySection>(DEFAULT_ACCESSIBILITY);

  // Initialize: get-or-create profile on mount
  // Wait for context to finish loading before making decisions.
  // The context uses lazy-fetch: isLoading starts false, goes true during fetch,
  // then back to false. We must wait until loading completes to distinguish
  // "no profile yet" from "haven't checked yet".
  useEffect(() => {
    // Still loading — wait
    if (contextLoading) return;
    // Already initialized — skip
    if (initDoneRef.current) return;

    if (profile) {
      initDoneRef.current = true;

      // Resume: populate form data from existing profile
      setGoalsData(profile.goals);
      setExpertiseData(profile.expertise);
      setProfessionalData(profile.professional_context);
      setAccessibilityData(profile.accessibility);

      if (profile.onboarding_completed) {
        // Already completed — redirect to home
        window.location.href = "/";
        return;
      }

      // Resume at correct step
      const resumeStep = resolveResumeStep(profile);
      setCurrentStep(resumeStep);

      // Mark earlier steps as completed
      const completed = new Set<number>();
      for (let i = 0; i < resumeStep; i++) {
        completed.add(i);
      }
      setCompletedSteps(completed);
      setIsInitializing(false);
    } else if (needsOnboarding) {
      // Context confirmed: no profile exists (404). Create one.
      initDoneRef.current = true;
      createNewProfile({ consent_given: true })
        .then(() => {
          setIsInitializing(false);
        })
        .catch((err) => {
          console.error("[OnboardingWizard] Failed to create profile:", err);
          setError("Failed to create your profile. Please try again.");
          setIsInitializing(false);
        });
    }
    // If neither profile nor needsOnboarding, context hasn't fetched yet — wait
  }, [contextLoading, profile, needsOnboarding, createNewProfile]);

  const handleNext = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      const step = STEPS[currentStep];
      const phaseDataMap: Record<string, unknown> = {
        goals: goalsData,
        expertise: expertiseData,
        professional: professionalData,
        accessibility: accessibilityData,
      };
      const data = phaseDataMap[step.key];
      await completeOnboardingPhase(step.phase, data);

      setCompletedSteps((prev) => new Set(prev).add(currentStep));
      setCurrentStep((prev) => prev + 1);
    } catch (err) {
      console.error("[OnboardingWizard] Failed to save step:", err);
      setError("Failed to save. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [
    currentStep,
    goalsData,
    expertiseData,
    professionalData,
    accessibilityData,
    completeOnboardingPhase,
  ]);

  const handleSkip = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      const step = STEPS[currentStep];
      await completeOnboardingPhase(step.phase);

      setCompletedSteps((prev) => new Set(prev).add(currentStep));
      setCurrentStep((prev) => prev + 1);
    } catch (err) {
      console.error("[OnboardingWizard] Failed to skip step:", err);
      setError("Failed to skip. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [currentStep, completeOnboardingPhase]);

  const handleBack = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [currentStep]);

  const handleComplete = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      await completeOnboardingPhase("ai_enrichment");
      window.location.href = "/";
    } catch (err) {
      console.error("[OnboardingWizard] Failed to complete onboarding:", err);
      setError("Failed to complete setup. Please try again.");
      setIsSaving(false);
    }
  }, [completeOnboardingPhase]);

  if (isInitializing || contextLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <div
            className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"
            data-testid="loading-spinner"
          />
          <p className="text-sm text-muted-foreground">
            Setting up your profile...
          </p>
        </div>
      </div>
    );
  }

  const isReviewStep = currentStep === STEPS.length - 1;

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <WizardProgress
        steps={STEPS}
        currentStep={currentStep}
        completedSteps={completedSteps}
      />

      <div className="min-h-[400px]">
        {currentStep === 0 && (
          <GoalsStep data={goalsData} onChange={setGoalsData} />
        )}
        {currentStep === 1 && (
          <ExpertiseStep data={expertiseData} onChange={setExpertiseData} />
        )}
        {currentStep === 2 && (
          <ProfessionalStep
            data={professionalData}
            onChange={setProfessionalData}
          />
        )}
        {currentStep === 3 && (
          <AccessibilityStep
            data={accessibilityData}
            onChange={setAccessibilityData}
          />
        )}
        {isReviewStep && (
          <ReviewStep
            goals={goalsData}
            expertise={expertiseData}
            professional={professionalData}
            accessibility={accessibilityData}
          />
        )}
      </div>

      {error && (
        <div
          className="mt-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="flex items-center justify-between mt-8 pt-4 border-t">
        <div>
          {currentStep > 0 && (
            <button
              type="button"
              onClick={handleBack}
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium rounded-md border border-input bg-background hover:bg-accent transition-colors disabled:opacity-50"
            >
              Back
            </button>
          )}
        </div>
        <div className="flex gap-3">
          {!isReviewStep && (
            <button
              type="button"
              onClick={handleSkip}
              disabled={isSaving}
              className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
            >
              Skip
            </button>
          )}
          {isReviewStep ? (
            <button
              type="button"
              onClick={handleComplete}
              disabled={isSaving}
              className="px-6 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
              data-testid="complete-setup-btn"
            >
              {isSaving ? "Completing..." : "Complete Setup"}
            </button>
          ) : (
            <button
              type="button"
              onClick={handleNext}
              disabled={isSaving}
              className="px-6 py-2 text-sm font-medium rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
              data-testid="next-btn"
            >
              {isSaving ? "Saving..." : "Next"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
