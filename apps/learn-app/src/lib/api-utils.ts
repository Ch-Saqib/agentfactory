import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

export function getAuthHeaders(): Record<string, string> {
  // Check for explicit dev mode first (for local testing)
  const devUserId = localStorage.getItem("dev_user_id");
  if (devUserId) {
    return { "X-User-ID": devUserId };
  }

  // For production: use OAuth token (Bearer)
  const token =
    localStorage.getItem("ainative_id_token") ||
    localStorage.getItem("ainative_access_token");
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }

  // Fallback: if user_id exists (from SSO), use it
  const userId = localStorage.getItem("ainative_user_id");
  if (userId) {
    return { "X-User-ID": userId };
  }

  console.warn("[getAuthHeaders] No auth token found in localStorage");
  return {};
}

/**
 * Get the current user ID from localStorage
 */
export function getCurrentUserId(): string | null {
  return localStorage.getItem("ainative_user_id");
}

/**
 * Enable dev mode for local testing (bypasses OAuth).
 * Sets a dev user ID that will be sent via X-User-ID header.
 */
export function enableDevMode(userId: string = "dev-user-123") {
  localStorage.setItem("dev_user_id", userId);
  console.log(`[Dev Mode] Enabled with user ID: ${userId}`);
  // Reload to apply changes
  window.location.reload();
}

/**
 * Disable dev mode and clear dev user ID.
 */
export function disableDevMode() {
  localStorage.removeItem("dev_user_id");
  console.log("[Dev Mode] Disabled");
  window.location.reload();
}

/**
 * Check if dev mode is enabled.
 */
export function isDevModeEnabled(): boolean {
  return import.meta.env.DEV && !!localStorage.getItem("dev_user_id");
}

export function useLearnerProfileApiUrl(): string {
  const { siteConfig } = useDocusaurusContext();
  return (
    (siteConfig.customFields?.learnerProfileApiUrl as string) ||
    "http://localhost:8004"
  );
}

/**
 * Returns true only if learnerProfileApiUrl is explicitly configured.
 * Use as a feature flag: no URL configured = all profile features off.
 */
export function useLearnerProfileEnabled(): boolean {
  const { siteConfig } = useDocusaurusContext();
  return Boolean(siteConfig.customFields?.learnerProfileApiUrl);
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
