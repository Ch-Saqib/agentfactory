"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useAuth } from "@/contexts/AuthContext";
import { useLearnerProfile } from "@/contexts/LearnerProfileContext";
import { getOnboardingStatus } from "@/lib/learner-profile-api";
import { useProgress } from "@/contexts/ProgressContext";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { WelcomeStep } from "./WelcomeStep";
import { GoalsStep } from "./GoalsStep";
import { ExpertiseStep } from "./ExpertiseStep";
import { ProfessionalStep } from "./ProfessionalStep";
import { AccessibilityStep } from "./AccessibilityStep";
import { ProjectStep } from "./ProjectStep";
import { FinishStep } from "./FinishStep";
import type {
  GoalsSection,
  ExpertiseSection,
  ProfessionalContextSection,
  AccessibilitySection,
  OnboardingPhase,
  ProfileResponse,
} from "@/lib/learner-profile-types";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

const STEPS = [
  { key: "goals", label: "Goals", phase: "goals" as const },
  { key: "expertise", label: "Background", phase: "expertise" as const },
  {
    key: "professional",
    label: "Professional Context",
    phase: "professional_context" as const,
  },
  {
    key: "accessibility",
    label: "Accessibility",
    phase: "accessibility" as const,
  },
  { key: "project", label: "Project", phase: "ai_enrichment" as const },
] as const;

const DEFAULT_GOALS: GoalsSection = {
  primary_learning_goal: null,
  secondary_goals: [],
  urgency: null,
  urgency_note: null,
  career_goal: null,
  immediate_application: null,
};

const DEFAULT_EXPERTISE: any = {
  domain: [],
  programming: { level: "", languages: [], notes: null },
  ai_fluency: { level: "", notes: null },
  business: { level: "", notes: null },
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

function resolveResumeStep(profile: ProfileResponse): number {
  const sectionChecks = [
    profile.goals.primary_learning_goal !== null ||
    profile.goals.urgency !== null,
    profile.expertise.programming.level !== "none" ||
    profile.expertise.ai_fluency.level !== "none" ||
    profile.expertise.business.level !== "none",
    profile.professional_context.current_role !== null ||
    profile.professional_context.industry !== null ||
    profile.professional_context.organization_type !== null,
    profile.accessibility.screen_reader ||
    profile.accessibility.dyslexia_friendly ||
    profile.accessibility.color_blind_safe ||
    profile.accessibility.cognitive_load_preference !== "standard" ||
    profile.accessibility.notes !== null,
  ];

  for (let i = 0; i < sectionChecks.length; i++) {
    if (!sectionChecks[i]) return i;
  }
  return STEPS.length - 1;
}

export default function OnboardingWizard() {
  const { siteConfig } = useDocusaurusContext();
  const apiUrl = (siteConfig.customFields?.learnerProfileApiUrl as string) || "http://localhost:8004";

  const { session, isLoading: authLoading } = useAuth();
  const {
    profile,
    isLoading: contextLoading,
    needsOnboarding,
    createNewProfile,
    completeOnboardingPhase,
    updateProfile,
  } = useLearnerProfile();

  const { refreshProgress } = useProgress();

  const [currentStep, setCurrentStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(
    new Set(),
  );
  const [isSaving, setIsSaving] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initDoneRef = useRef(false);

  const [goalsData, setGoalsData] = useState<GoalsSection>(DEFAULT_GOALS);
  const [expertiseData, setExpertiseData] =
    useState<ExpertiseSection>(DEFAULT_EXPERTISE);
  const [professionalData, setProfessionalData] =
    useState<ProfessionalContextSection>(DEFAULT_PROFESSIONAL);
  const [accessibilityData, setAccessibilityData] =
    useState<AccessibilitySection>(DEFAULT_ACCESSIBILITY);

  useEffect(() => {
    if (authLoading || contextLoading) return;

    // Redirect unauthenticated users back to the homepage to prevent infinite loading
    if (!session?.user) {
      window.location.href = "/";
      return;
    }

    if (initDoneRef.current) return;

    if (profile) {
      initDoneRef.current = true;
      setGoalsData(profile.goals);
      setExpertiseData(profile.expertise);
      setProfessionalData(profile.professional_context);
      setAccessibilityData(profile.accessibility);

      if (profile.onboarding_completed) {
        window.location.href = "/";
        return;
      }

      getOnboardingStatus(apiUrl)
        .then((status) => {
          const nextPhase = status.next_section;
          let stepIdx = STEPS.length - 1;
          if (nextPhase) {
            const found = STEPS.findIndex((s) => s.phase === nextPhase);
            if (found !== -1) stepIdx = found;
          }
          setCurrentStep(stepIdx);

          const completed = new Set<number>();
          STEPS.forEach((s, idx) => {
            if (status.sections_completed[s.phase]) {
              completed.add(idx);
            }
          });
          setCompletedSteps(completed);
        })
        .catch((err) => {
          console.error("[OnboardingWizard] Failed to get progress:", err);
          // Fallback heuristic
          const resumeStep = resolveResumeStep(profile);
          setCurrentStep(resumeStep);
          const completed = new Set<number>();
          for (let i = 0; i < resumeStep; i++) completed.add(i);
          setCompletedSteps(completed);
        })
        .finally(() => {
          setIsInitializing(false);
        });
    } else if (needsOnboarding) {
      initDoneRef.current = true;
      setCurrentStep(-1);
      setIsInitializing(false);
    }
  }, [authLoading, contextLoading, session, profile, needsOnboarding]);

  const handleAgree = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      await createNewProfile({ consent_given: true });
      setCurrentStep(0);
    } catch (err) {
      console.error("[OnboardingWizard] Failed to create profile:", err);
      setError("Failed to create your profile. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }, [createNewProfile]);

  const handleDecline = useCallback(() => {
    if (window.history.length > 2) {
      window.history.back();
    } else {
      window.location.href = "/";
    }
  }, []);

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

      // Simulate XP award locally until API natively issues XP for profile events
      toast.success("+20 XP Earned!", {
        description: `You completed the ${step.label} section.`,
        className: "bg-green-500/10 border-green-500/20 text-green-500",
      });

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
      await updateProfile({
        professional_context: professionalData,
        goals: goalsData,
      });
      await completeOnboardingPhase("ai_enrichment", {});
      setCurrentStep(STEPS.length);
    } catch (err) {
      console.error("[OnboardingWizard] Failed to finish setup:", err);
      setError("Failed to complete setup. Please try again.");
      setIsSaving(false);
    }
  }, [completeOnboardingPhase, updateProfile, professionalData, goalsData]);

  // Framer Motion Variants
  const containerVariants = {
    initial: { opacity: 0, y: 20, filter: "blur(4px)", scale: 0.98 },
    animate: {
      opacity: 1,
      y: 0,
      filter: "blur(0px)",
      scale: 1,
      transition: { type: "spring" as const, stiffness: 400, damping: 30, mass: 1 }
    },
    exit: {
      opacity: 0,
      y: -20,
      filter: "blur(4px)",
      scale: 0.98,
      transition: { duration: 0.2, ease: "easeOut" as const }
    }
  };

  if (isInitializing || contextLoading) {
    return (
      <div className="fixed inset-0 bg-background flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center gap-4 text-muted-foreground"
        >
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <p className="text-sm tracking-wide">Initializing your profile...</p>
        </motion.div>
      </div>
    );
  }

  const isReviewStep = currentStep === STEPS.length - 1;

  return (
    <div className="fixed inset-0 bg-background flex flex-col font-sans z-[100] overflow-y-auto">
      {/* Minimal Top Bar */}
      {currentStep >= 0 && currentStep < STEPS.length && (
        <header className="fixed top-0 left-0 w-full h-16 border-b border-border/40 bg-background/80 backdrop-blur-md z-[110] flex items-center justify-between px-4 sm:px-6">
          <div className="flex items-center gap-4">
            <div className="md:hidden font-semibold">Step {currentStep + 1} of {STEPS.length}</div>
            <div className="hidden md:flex flex-col">
              <span className="text-sm font-semibold">Setup Profile</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground hidden sm:inline-block">~90 seconds &middot; You can skip anything</span>
            <Button variant="ghost" size="sm" onClick={() => window.location.href = "/"} className="text-muted-foreground hover:text-foreground">
              Exit
            </Button>
          </div>
          {/* Mobile progress bar along the bottom of the header */}
          <Progress
            value={(currentStep / (STEPS.length - 1)) * 100}
            className="absolute bottom-0 left-0 w-full h-[2px] rounded-none bg-transparent [&>div]:bg-primary md:hidden"
          />
        </header>
      )}

      {/* Main Content Area - Split Layout on Desktop */}
      <div className={`flex-1 flex overflow-hidden ${currentStep >= 0 && currentStep < STEPS.length ? "pt-16" : ""}`}>
        {/* Left Stepper Desktop */}
        {currentStep >= 0 && currentStep < STEPS.length && (
          <aside className="hidden md:flex w-[280px] lg:w-[320px] flex-col border-r border-border/40 bg-accent/20 p-6 overflow-y-auto">
            <div className="space-y-6 mt-8">
              {STEPS.map((step, idx) => {
                const isActive = idx === currentStep;
                const isPast = idx < currentStep;
                return (
                  <div key={idx} className={`flex items-start gap-4 ${isActive ? "text-primary" : isPast ? "text-primary/70" : "text-muted-foreground/60"}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium shrink-0 border-2 transition-colors ${isActive ? "bg-primary text-primary-foreground border-primary" :
                      isPast ? "bg-primary/20 border-primary/30 text-primary" :
                        "bg-transparent border-muted-foreground/30"
                      }`}>
                      {isPast ? "✓" : idx + 1}
                    </div>
                    <div className="flex flex-col mt-1">
                      <span className={`text-sm font-medium ${isActive ? "font-semibold" : ""}`}>{step.label}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </aside>
        )}

        {/* Main Form Area */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 relative pb-12">
          <div className={`mx-auto w-full relative min-h-[100dvh] flex flex-col justify-center py-12 ${currentStep === -1 || currentStep === STEPS.length ? 'max-w-2xl' : 'max-w-xl'}`}>
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                variants={containerVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="w-full"
              >
                {currentStep === -1 && (
                  <WelcomeStep
                    onAgree={handleAgree}
                    onDecline={handleDecline}
                    isSaving={isSaving}
                  />
                )}
                {currentStep === 0 && (
                  <GoalsStep data={goalsData} onChange={setGoalsData} autoAdvance={handleNext} />
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
                  <ProjectStep
                    professional={professionalData}
                    goals={goalsData}
                    onChangeProfessional={setProfessionalData}
                    onChangeGoals={setGoalsData}
                  />
                )}
                {currentStep === STEPS.length && (
                  <FinishStep />
                )}
              </motion.div>
            </AnimatePresence>

            {/* Inline Controls (Replacing Floating Dock) */}
            {currentStep >= 0 && currentStep < STEPS.length && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-10 flex items-center justify-between w-full pt-6 border-t border-border/40"
              >
                <div className="flex">
                  {currentStep > 0 ? (
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={handleBack}
                      disabled={isSaving}
                      className="rounded-xl px-3 md:px-4 py-2 hover:bg-accent transition-colors"
                      aria-label="Go back to previous step"
                    >
                      Back
                    </Button>
                  ) : (
                    <div className="w-[60px]" />
                  )}
                </div>

                <div className="flex items-center gap-1 md:gap-3">
                  {!isReviewStep && (
                    <Button
                      type="button"
                      variant="link"
                      onClick={handleSkip}
                      disabled={isSaving}
                      className="text-muted-foreground/60 hover:text-foreground hover:no-underline rounded-xl px-3 md:px-4 transition-colors font-normal text-sm"
                      aria-label="Skip to next step"
                    >
                      Skip for now
                    </Button>
                  )}
                  {isReviewStep ? (
                    <Button
                      type="button"
                      onClick={handleComplete}
                      disabled={isSaving}
                      className="rounded-xl px-5 md:px-6 font-medium shadow-md shadow-primary/20 whitespace-nowrap"
                    >
                      {isSaving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                      {isSaving ? "Processing..." : (
                        <>
                          <span className="hidden sm:inline">Enter Agent Factory</span>
                          <span className="sm:hidden">Finish</span>
                        </>
                      )}
                    </Button>
                  ) : (
                    <Button
                      type="button"
                      onClick={handleNext}
                      disabled={isSaving}
                      className="rounded-xl px-5 md:px-6 font-medium shadow-md shadow-primary/20 whitespace-nowrap"
                    >
                      {isSaving && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                      {isSaving ? "Saving..." : "Continue"}
                    </Button>
                  )}
                </div>
              </motion.div>
            )}

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 5, scale: 0.95 }}
                  className="mt-4 mx-auto w-max max-w-[90vw] text-center text-destructive text-sm font-medium px-4 py-3 bg-destructive/10 rounded-xl border border-destructive/20 shadow-lg"
                >
                  {error}
                </motion.div>
              )}
            </AnimatePresence>

          </div>
        </div>
      </div>
    </div>
  );
}
