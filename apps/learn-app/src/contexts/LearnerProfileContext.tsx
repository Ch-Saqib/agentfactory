import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
  ReactNode,
} from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useAuth } from "./AuthContext";
import {
  getMyProfileOrNull,
  createProfile,
  updateMyProfile,
  updateSection as apiUpdateSection,
  completeOnboardingPhase as apiCompleteOnboardingPhase,
} from "@/lib/learner-profile-api";
import type {
  ProfileResponse,
  ProfileCreateRequest,
  ProfileUpdateRequest,
  OnboardingPhase,
} from "@/lib/learner-profile-types";

// =============================================================================
// localStorage Cache
// =============================================================================

const CACHE_KEY = "learner_profile_cache";
const CACHE_TTL_MS = 30 * 60 * 1000; // 30 minutes

interface CachedProfile {
  profile: ProfileResponse;
  timestamp: number;
}

function getCachedProfile(): ProfileResponse | null {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const cached: CachedProfile = JSON.parse(raw);
    if (Date.now() - cached.timestamp > CACHE_TTL_MS) {
      localStorage.removeItem(CACHE_KEY);
      return null;
    }
    return cached.profile;
  } catch {
    localStorage.removeItem(CACHE_KEY);
    return null;
  }
}

function setCachedProfile(profile: ProfileResponse): void {
  try {
    localStorage.setItem(
      CACHE_KEY,
      JSON.stringify({ profile, timestamp: Date.now() }),
    );
  } catch {
    // localStorage full or unavailable — ignore
  }
}

function clearCachedProfile(): void {
  try {
    localStorage.removeItem(CACHE_KEY);
  } catch {
    // ignore
  }
}

// =============================================================================
// Context
// =============================================================================

interface LearnerProfileContextType {
  profile: ProfileResponse | null;
  isLoading: boolean;
  needsOnboarding: boolean;
  refreshProfile: () => Promise<void>;
  updateProfile: (data: ProfileUpdateRequest) => Promise<ProfileResponse>;
  updateSection: (section: string, data: unknown) => Promise<ProfileResponse>;
  completeOnboardingPhase: (
    phase: OnboardingPhase,
    data?: unknown,
  ) => Promise<ProfileResponse>;
  createNewProfile: (data?: ProfileCreateRequest) => Promise<ProfileResponse>;
  /** @internal Trigger lazy fetch — called automatically by useLearnerProfile */
  ensureProfileLoaded: () => Promise<void>;
}

const LearnerProfileContext = createContext<
  LearnerProfileContextType | undefined
>(undefined);

export function LearnerProfileProvider({
  children,
}: {
  children: ReactNode;
}) {
  const { session } = useAuth();
  const { siteConfig } = useDocusaurusContext();
  const apiUrl =
    (siteConfig.customFields?.learnerProfileApiUrl as string) ||
    "http://localhost:8004";

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [needsOnboarding, setNeedsOnboarding] = useState(false);
  const [hasAttemptedFetch, setHasAttemptedFetch] = useState(false);
  const fetchingRef = useRef(false);

  // Helper: set profile in both React state and localStorage
  const setProfileWithCache = useCallback((data: ProfileResponse) => {
    setProfile(data);
    setCachedProfile(data);
  }, []);

  // Lazy trigger — called when context is consumed via useLearnerProfile
  const ensureProfileLoaded = useCallback(async () => {
    if (hasAttemptedFetch || fetchingRef.current || !session?.user) return;
    fetchingRef.current = true;

    // Check localStorage cache first — avoids API call on hard refresh
    const cached = getCachedProfile();
    if (cached) {
      setProfile(cached);
      setNeedsOnboarding(false);
      setHasAttemptedFetch(true);
      fetchingRef.current = false;
      return;
    }

    setIsLoading(true);
    try {
      const data = await getMyProfileOrNull(apiUrl);
      if (data) {
        setProfileWithCache(data);
        setNeedsOnboarding(false);
      } else {
        setNeedsOnboarding(true);
      }
    } catch (err) {
      console.error("[LearnerProfileContext] Failed to load profile:", err);
    } finally {
      setIsLoading(false);
      setHasAttemptedFetch(true);
      fetchingRef.current = false;
    }
  }, [hasAttemptedFetch, session?.user, apiUrl, setProfileWithCache]);

  // Clear state on sign-out
  useEffect(() => {
    if (!session?.user) {
      setProfile(null);
      setNeedsOnboarding(false);
      setHasAttemptedFetch(false);
      fetchingRef.current = false;
      clearCachedProfile();
    }
  }, [session?.user]);

  // Force-refresh: clear cache, fetch fresh from API
  const refreshProfile = useCallback(async () => {
    if (!session?.user) return;
    clearCachedProfile();
    setIsLoading(true);
    try {
      const data = await getMyProfileOrNull(apiUrl);
      if (data) {
        setProfileWithCache(data);
        setNeedsOnboarding(false);
      } else {
        setProfile(null);
        setNeedsOnboarding(true);
      }
    } catch (err) {
      console.error("[LearnerProfileContext] Failed to refresh profile:", err);
    } finally {
      setIsLoading(false);
    }
  }, [session?.user, apiUrl, setProfileWithCache]);

  const updateProfile = useCallback(
    async (data: ProfileUpdateRequest): Promise<ProfileResponse> => {
      const updated = await updateMyProfile(apiUrl, data);
      setProfileWithCache(updated);
      setNeedsOnboarding(false);
      return updated;
    },
    [apiUrl, setProfileWithCache],
  );

  const updateSectionFn = useCallback(
    async (section: string, data: unknown): Promise<ProfileResponse> => {
      const updated = await apiUpdateSection(apiUrl, section, data);
      setProfileWithCache(updated);
      return updated;
    },
    [apiUrl, setProfileWithCache],
  );

  const completeOnboardingPhaseFn = useCallback(
    async (
      phase: OnboardingPhase,
      data?: unknown,
    ): Promise<ProfileResponse> => {
      const updated = await apiCompleteOnboardingPhase(apiUrl, phase, data);
      setProfileWithCache(updated);
      setNeedsOnboarding(false);
      return updated;
    },
    [apiUrl, setProfileWithCache],
  );

  const createNewProfile = useCallback(
    async (data?: ProfileCreateRequest): Promise<ProfileResponse> => {
      const created = await createProfile(apiUrl, data || {});
      setProfileWithCache(created);
      setNeedsOnboarding(false);
      return created;
    },
    [apiUrl, setProfileWithCache],
  );

  return (
    <LearnerProfileContext.Provider
      value={{
        profile,
        isLoading,
        needsOnboarding,
        refreshProfile,
        updateProfile,
        updateSection: updateSectionFn,
        completeOnboardingPhase: completeOnboardingPhaseFn,
        createNewProfile,
        ensureProfileLoaded,
      }}
    >
      {children}
    </LearnerProfileContext.Provider>
  );
}

export function useLearnerProfile() {
  const context = useContext(LearnerProfileContext);
  if (context === undefined) {
    throw new Error(
      "useLearnerProfile must be used within a LearnerProfileProvider",
    );
  }

  // Trigger lazy fetch on first render of a consumer
  useEffect(() => {
    context.ensureProfileLoaded();
  }, [context.ensureProfileLoaded]);

  return context;
}
