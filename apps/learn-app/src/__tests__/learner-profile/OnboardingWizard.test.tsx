import { describe, it, expect, beforeEach, vi, type Mock } from "vitest";
import React from "react";
import {
  render,
  screen,
  act,
  waitFor,
  fireEvent,
  within,
} from "@testing-library/react";
import OnboardingWizard from "@/components/onboarding/OnboardingWizard";
import { LearnerProfileProvider } from "@/contexts/LearnerProfileContext";
import type { ProfileResponse } from "@/lib/learner-profile-types";

// ---- Mocks ----

const mockSession = { user: { id: "test-user" } };
let currentSession: typeof mockSession | null = mockSession;

vi.mock("@/contexts/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    session: currentSession,
    isLoading: false,
    signOut: vi.fn(),
    refreshUserData: vi.fn(),
  })),
}));

const mockGetMyProfileOrNull = vi.fn();
const mockCreateProfile = vi.fn();
const mockUpdateMyProfile = vi.fn();
const mockApiUpdateSection = vi.fn();
const mockApiCompleteOnboardingPhase = vi.fn();

vi.mock("@/lib/learner-profile-api", () => ({
  getMyProfileOrNull: (...args: unknown[]) => mockGetMyProfileOrNull(...args),
  createProfile: (...args: unknown[]) => mockCreateProfile(...args),
  updateMyProfile: (...args: unknown[]) => mockUpdateMyProfile(...args),
  updateSection: (...args: unknown[]) => mockApiUpdateSection(...args),
  completeOnboardingPhase: (...args: unknown[]) =>
    mockApiCompleteOnboardingPhase(...args),
}));

// Mock window.location
const locationAssignSpy = vi.fn();
const originalLocation = window.location;

beforeEach(() => {
  Object.defineProperty(window, "location", {
    writable: true,
    value: { ...originalLocation, href: "/onboarding", assign: locationAssignSpy },
  });
});

// ---- Test data ----

const emptyProfile: ProfileResponse = {
  learner_id: "test-user",
  name: null,
  profile_version: "1.0",
  consent_given: true,
  consent_date: "2026-01-01T00:00:00Z",
  expertise: {
    domain: [],
    programming: { level: "none", languages: [], notes: null },
    ai_ml: { level: "none", notes: null },
    business: { level: "none", notes: null },
    subject_specific: {
      topics_already_mastered: [],
      topics_partially_known: [],
      known_misconceptions: [],
    },
  },
  professional_context: {
    current_role: null,
    industry: null,
    organization_type: null,
    team_context: null,
    real_projects: [],
    tools_in_use: [],
    constraints: null,
  },
  goals: {
    primary_learning_goal: null,
    secondary_goals: [],
    urgency: null,
    urgency_note: null,
    career_goal: null,
    immediate_application: null,
  },
  communication: {
    language_complexity: null,
    preferred_structure: null,
    verbosity: null,
    analogy_domain: null,
    tone: null,
    wants_summaries: null,
    wants_check_in_questions: null,
    format_notes: null,
  },
  delivery: {
    output_format: null,
    target_length: null,
    include_code_samples: null,
    code_verbosity: null,
    include_visual_descriptions: null,
    language: "English",
    language_proficiency: null,
  },
  accessibility: {
    screen_reader: false,
    cognitive_load_preference: "standard",
    color_blind_safe: false,
    dyslexia_friendly: false,
    notes: null,
  },
  onboarding_completed: false,
  onboarding_progress: 0,
  profile_completeness: 0.1,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const partiallyCompletedProfile: ProfileResponse = {
  ...emptyProfile,
  goals: {
    ...emptyProfile.goals,
    primary_learning_goal: "Build AI agents",
    urgency: "medium",
  },
  expertise: {
    ...emptyProfile.expertise,
    programming: { level: "intermediate", languages: ["Python"], notes: null },
  },
  onboarding_progress: 0.4,
};

// ---- Helper ----

function renderWizard() {
  return render(
    <LearnerProfileProvider>
      <OnboardingWizard />
    </LearnerProfileProvider>,
  );
}

// ---- Tests ----

describe("OnboardingWizard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    currentSession = { user: { id: "test-user" } };
    // Default: profile exists (empty)
    mockGetMyProfileOrNull.mockResolvedValue(emptyProfile);
    // completeOnboardingPhase returns updated profile
    mockApiCompleteOnboardingPhase.mockResolvedValue(emptyProfile);
    mockCreateProfile.mockResolvedValue(emptyProfile);
  });

  // ---- Loading / init ----

  it("shows loading spinner while initializing", async () => {
    // Slow down profile fetch so we can catch the loading state
    mockGetMyProfileOrNull.mockImplementation(
      () => new Promise(() => {}), // never resolves
    );

    renderWizard();
    expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
  });

  it("creates a new profile when none exists (404)", async () => {
    mockGetMyProfileOrNull.mockResolvedValue(null);

    renderWizard();

    await waitFor(() => {
      expect(mockCreateProfile).toHaveBeenCalledWith(
        "http://localhost:8004",
        { consent_given: true },
      );
    });
  });

  it("displays the Goals step first for a new profile", async () => {
    renderWizard();

    await waitFor(() => {
      expect(
        screen.getByText("Goals & Motivation"),
      ).toBeInTheDocument();
    });

    // Should show the primary learning goal input
    expect(screen.getByLabelText("Primary Learning Goal")).toBeInTheDocument();
  });

  // ---- Step navigation ----

  it("advances to Expertise step when Next is clicked", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });
  });

  it("goes back to Goals step when Back is clicked from Expertise", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Go to Expertise
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });

    // Go back
    fireEvent.click(screen.getByText("Back"));

    expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
  });

  it("does not show Back button on the first step", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    expect(screen.queryByText("Back")).not.toBeInTheDocument();
  });

  it("navigates through all 5 steps sequentially", async () => {
    renderWizard();

    // Step 1: Goals
    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Advance to Expertise
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });
    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });

    // Advance to Professional
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });
    await waitFor(() => {
      expect(screen.getByText("Professional Context")).toBeInTheDocument();
    });

    // Advance to Accessibility
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });
    await waitFor(() => {
      expect(
        screen.getByText("Accessibility Preferences"),
      ).toBeInTheDocument();
    });

    // Advance to Review
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });
    await waitFor(() => {
      expect(screen.getByText("Review Your Profile")).toBeInTheDocument();
    });
  });

  // ---- Skip ----

  it("calls completeOnboardingPhase without data when Skip is clicked", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByText("Skip for now"));
    });

    expect(mockApiCompleteOnboardingPhase).toHaveBeenCalledWith(
      "http://localhost:8004",
      "goals",
      undefined,
    );

    // Should advance to Expertise
    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });
  });

  it("does not show Skip on the Review step", async () => {
    renderWizard();

    // Navigate to Review
    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        fireEvent.click(screen.getByTestId("next-btn"));
      });
    }

    await waitFor(() => {
      expect(screen.getByText("Review Your Profile")).toBeInTheDocument();
    });
    expect(screen.queryByText("Skip for now")).not.toBeInTheDocument();
  });

  // ---- Complete ----

  it("shows 'Complete Setup' button on Review step and redirects on click", async () => {
    renderWizard();

    // Navigate to Review
    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        fireEvent.click(screen.getByTestId("next-btn"));
      });
    }

    await waitFor(() => {
      expect(screen.getByTestId("complete-setup-btn")).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId("complete-setup-btn"));
    });

    expect(mockApiCompleteOnboardingPhase).toHaveBeenCalledWith(
      "http://localhost:8004",
      "ai_enrichment",
      undefined,
    );

    expect(window.location.href).toBe("/");
  });

  // ---- Loading state / disabled button ----

  it("disables Next button during save", async () => {
    // Make completeOnboardingPhase slow
    let resolvePhase: (v: ProfileResponse) => void;
    mockApiCompleteOnboardingPhase.mockImplementation(
      () => new Promise<ProfileResponse>((r) => { resolvePhase = r; }),
    );

    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Click Next — should become disabled
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    expect(screen.getByTestId("next-btn")).toBeDisabled();
    expect(screen.getByTestId("next-btn")).toHaveTextContent("Saving...");

    // Resolve the pending save
    await act(async () => {
      resolvePhase!(emptyProfile);
    });
  });

  // ---- Resume on refresh ----

  it("resumes at correct step when profile has some phases completed", async () => {
    mockGetMyProfileOrNull.mockResolvedValue(partiallyCompletedProfile);

    renderWizard();

    // Goals and Expertise are done -> should start at Professional (step 2)
    await waitFor(() => {
      expect(screen.getByText("Professional Context")).toBeInTheDocument();
    });
  });

  it("populates form data from existing profile when resuming", async () => {
    mockGetMyProfileOrNull.mockResolvedValue(partiallyCompletedProfile);

    renderWizard();

    // Should resume at Professional step. Go back to Goals to verify data was loaded.
    await waitFor(() => {
      expect(screen.getByText("Professional Context")).toBeInTheDocument();
    });

    // Go back to Expertise
    fireEvent.click(screen.getByText("Back"));
    expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();

    // Go back to Goals
    fireEvent.click(screen.getByText("Back"));
    expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();

    // Verify the goal text was populated
    const goalInput = screen.getByLabelText(
      "Primary Learning Goal",
    ) as HTMLInputElement;
    expect(goalInput.value).toBe("Build AI agents");
  });

  // ---- Progress bar updates ----

  it("updates progress bar when steps are completed", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Step 0 indicator should be active
    const step0 = screen.getByTestId("step-indicator-0");
    expect(step0).toHaveAttribute("aria-current", "step");

    // Advance
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });

    // Step 1 indicator should now be active
    const step1 = screen.getByTestId("step-indicator-1");
    expect(step1).toHaveAttribute("aria-current", "step");

    // Step 0 should no longer be aria-current
    expect(screen.getByTestId("step-indicator-0")).not.toHaveAttribute(
      "aria-current",
    );
  });

  // ---- Step renders correct fields ----

  it("GoalsStep shows learning goal input and urgency radio", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    expect(screen.getByLabelText("Primary Learning Goal")).toBeInTheDocument();
    expect(screen.getByText("Learning Urgency")).toBeInTheDocument();
    // 3 urgency radio options
    expect(screen.getAllByRole("radio")).toHaveLength(3);
  });

  it("ExpertiseStep shows 3 expertise selects and domain input", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Navigate to Expertise
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });

    expect(screen.getByLabelText("Programming")).toBeInTheDocument();
    expect(screen.getByLabelText("AI & Machine Learning")).toBeInTheDocument();
    expect(screen.getByLabelText("Business")).toBeInTheDocument();
    expect(screen.getByLabelText("Domain Expertise (optional)")).toBeInTheDocument();
  });

  it("ProfessionalStep shows role, industry, and org type fields", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Navigate to Professional (step 2)
    for (let i = 0; i < 2; i++) {
      await act(async () => {
        fireEvent.click(screen.getByTestId("next-btn"));
      });
    }

    await waitFor(() => {
      expect(screen.getByText("Professional Context")).toBeInTheDocument();
    });

    expect(screen.getByLabelText("Current Role")).toBeInTheDocument();
    expect(screen.getByLabelText("Industry")).toBeInTheDocument();
    expect(screen.getByLabelText("Organization Type (optional)")).toBeInTheDocument();
  });

  it("AccessibilityStep shows toggles and cognitive load radio", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Navigate to Accessibility (step 3)
    for (let i = 0; i < 3; i++) {
      await act(async () => {
        fireEvent.click(screen.getByTestId("next-btn"));
      });
    }

    await waitFor(() => {
      expect(
        screen.getByText("Accessibility Preferences"),
      ).toBeInTheDocument();
    });

    // Accessibility toggles
    expect(screen.getAllByRole("switch")).toHaveLength(3);
    // Cognitive load radio
    expect(screen.getByText("Cognitive Load Preference")).toBeInTheDocument();
    // Notes textarea
    expect(
      screen.getByLabelText("Additional Notes (optional)"),
    ).toBeInTheDocument();
  });

  it("ReviewStep shows summary with completeness indicator", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Fill in some data in goals step
    fireEvent.change(screen.getByLabelText("Primary Learning Goal"), {
      target: { value: "Learn AI agents" },
    });

    // Navigate to Review step
    for (let i = 0; i < 4; i++) {
      await act(async () => {
        fireEvent.click(screen.getByTestId("next-btn"));
      });
    }

    await waitFor(() => {
      expect(screen.getByText("Review Your Profile")).toBeInTheDocument();
    });

    // Should show completeness percent
    expect(screen.getByTestId("completeness-percent")).toBeInTheDocument();
    // Should show a progress bar
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  // ---- Error handling ----

  it("shows error message when save fails", async () => {
    mockApiCompleteOnboardingPhase.mockRejectedValueOnce(
      new Error("Network error"),
    );

    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Failed to save. Please try again.",
      );
    });

    // Should stay on Goals step
    expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
  });

  it("shows error when profile creation fails", async () => {
    mockGetMyProfileOrNull.mockResolvedValue(null);
    mockCreateProfile.mockRejectedValue(new Error("Server error"));

    renderWizard();

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Failed to create your profile. Please try again.",
      );
    });
  });

  // ---- Calls completeOnboardingPhase with correct phase and data ----

  it("sends goals data when completing goals step", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Fill in goal
    fireEvent.change(screen.getByLabelText("Primary Learning Goal"), {
      target: { value: "Build agents" },
    });
    // Select urgency
    fireEvent.click(screen.getByDisplayValue("high"));

    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    expect(mockApiCompleteOnboardingPhase).toHaveBeenCalledWith(
      "http://localhost:8004",
      "goals",
      expect.objectContaining({
        primary_learning_goal: "Build agents",
        urgency: "high",
      }),
    );
  });

  it("sends expertise data when completing expertise step", async () => {
    renderWizard();

    await waitFor(() => {
      expect(screen.getByText("Goals & Motivation")).toBeInTheDocument();
    });

    // Go to Expertise
    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    await waitFor(() => {
      expect(screen.getByText("Expertise & Skills")).toBeInTheDocument();
    });

    // Change programming level
    fireEvent.change(screen.getByLabelText("Programming"), {
      target: { value: "advanced" },
    });

    await act(async () => {
      fireEvent.click(screen.getByTestId("next-btn"));
    });

    expect(mockApiCompleteOnboardingPhase).toHaveBeenCalledWith(
      "http://localhost:8004",
      "expertise",
      expect.objectContaining({
        programming: expect.objectContaining({ level: "advanced" }),
      }),
    );
  });
});
