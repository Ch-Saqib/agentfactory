/**
 * API Globals Client Module
 *
 * Injects API URLs from Docusaurus config into window globals for
 * use by API client modules (shorts-api, etc.).
 *
 * This module runs immediately on client-side load via Docusaurus clientModules.
 * It imports the generated site config (which includes customFields from
 * docusaurus.config.ts) and sets window globals that API clients can read.
 */

import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import siteConfig from '@generated/docusaurus.config';

if (ExecutionEnvironment.canUseDOM) {
  const { customFields } = siteConfig;

  if (customFields) {
    // Inject Study Mode API URL
    if (customFields.studyModeApiUrl) {
      (window as any).__STUDY_MODE_API_URL__ = customFields.studyModeApiUrl;
    }

    // Inject Shorts API URL
    if (customFields.shortsApiUrl) {
      (window as any).__SHORTS_API_URL__ = customFields.shortsApiUrl;
    }

    // Inject Token Metering API URL
    if (customFields.tokenMeteringApiUrl) {
      (window as any).__TOKEN_METERING_API_URL__ = customFields.tokenMeteringApiUrl;
    }

    // Inject Progress API URL
    if (customFields.progressApiUrl) {
      (window as any).__PROGRESS_API_URL__ = customFields.progressApiUrl;
    }
  }
}
