import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

export function getAuthHeaders(): Record<string, string> {
  const token =
    localStorage.getItem("ainative_id_token") ||
    localStorage.getItem("ainative_access_token");
  if (!token) {
    console.warn("[getAuthHeaders] No auth token found in localStorage");
    return {};
  }
  return { Authorization: `Bearer ${token}` };
}

export function useLearnerProfileApiUrl(): string {
  const { siteConfig } = useDocusaurusContext();
  return (
    (siteConfig.customFields?.learnerProfileApiUrl as string) ||
    "http://localhost:8004"
  );
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
