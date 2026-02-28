/**
 * API Globals Client Module
 *
 * Injects API URLs from Docusaurus config into window globals for
 * backwards compatibility with code that expects these values.
 *
 * This module runs immediately on client-side load.
 */

import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

if (ExecutionEnvironment.canUseDOM) {
  // Get the site config from the injected global variable
  // Docusaurus injects this as __INITIAL_STATE__ or similar
  const siteConfig = (window as any).__DOCUSAURUS_SITE_CONFIG__;

  if (siteConfig?.customFields) {
    // Inject Study Mode API URL
    if (siteConfig.customFields.studyModeApiUrl) {
      (window as any).__STUDY_MODE_API_URL__ = siteConfig.customFields.studyModeApiUrl;
    }

    // Inject Shorts API URL
    if (siteConfig.customFields.shortsApiUrl) {
      (window as any).__SHORTS_API_URL__ = siteConfig.customFields.shortsApiUrl;
    }

    // Inject Token Metering API URL
    if (siteConfig.customFields.tokenMeteringApiUrl) {
      (window as any).__TOKEN_METERING_API_URL__ = siteConfig.customFields.tokenMeteringApiUrl;
    }

    // Inject Progress API URL
    if (siteConfig.customFields.progressApiUrl) {
      (window as any).__PROGRESS_API_URL__ = siteConfig.customFields.progressApiUrl;
    }
  }
}
