/**
 * Docusaurus Root Component
 *
 * This component wraps the entire site with:
 * 1. AuthProvider - Enables authentication state across the site
 * 2. PyodideProvider - Enables direct Pyodide integration for interactive Python execution
 * 3. AnalyticsTracker - Tracks user interactions (page views, scroll depth, etc.)
 * 4. VoiceReadingProvider - Enables word-by-word reading with speech synthesis
 *
 * GA4 is configured via the GA4_MEASUREMENT_ID environment variable.
 * If not set, analytics will not load.
 */

import React, { useEffect } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { LearnerProfileProvider } from '@/contexts/LearnerProfileContext';
import { ProfileNudgeVisibilityProvider } from '@/contexts/ProfileNudgeVisibilityContext';
import { RequireProfile } from '@/components/RequireProfile';
import { Toaster } from '@/components/ui/sonner';
import { PyodideProvider } from '@/contexts/PyodideContext';
import { AnalyticsTracker } from '@/components/AnalyticsTracker';
import { StudyModeProvider } from '@/contexts/StudyModeContext';
import { VoiceReadingProvider } from '@/contexts/VoiceReadingContext';
import { ProgressProvider } from '@/contexts/ProgressContext';

export default function Root({ children }: { children: React.ReactNode }) {
  const { siteConfig } = useDocusaurusContext();
  const authUrl = (siteConfig.customFields?.authUrl as string) || 'http://localhost:3001';
  const oauthClientId = (siteConfig.customFields?.oauthClientId as string) || 'agent-factory-public-client';

  // Expose dev mode helpers to window for easy testing in browser console
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      (window as any).enableDevMode = (userId: string = 'dev-user-123') => {
        localStorage.setItem('dev_user_id', userId);
        console.log(`[Dev Mode] Enabled with user: ${userId}`);
        window.location.reload();
      };
      (window as any).disableDevMode = () => {
        localStorage.removeItem('dev_user_id');
        console.log('[Dev Mode] Disabled');
        window.location.reload();
      };
      (window as any).isDevMode = () => {
        return !!localStorage.getItem('dev_user_id');
      };
      console.log('[Dev Mode] Available commands: enableDevMode(), disableDevMode(), isDevMode()');
    }
  }, []);

  return (
    <AuthProvider authUrl={authUrl} oauthClientId={oauthClientId}>
      <LearnerProfileProvider>
        <ProfileNudgeVisibilityProvider>
          <RequireProfile>
            <ProgressProvider>
              <PyodideProvider>
                <StudyModeProvider>
                  <VoiceReadingProvider>
                    <AnalyticsTracker>
                      {children}
                      <Toaster />
                    </AnalyticsTracker>
                  </VoiceReadingProvider>
                </StudyModeProvider>
              </PyodideProvider>
            </ProgressProvider>
          </RequireProfile>
        </ProfileNudgeVisibilityProvider>
      </LearnerProfileProvider>
    </AuthProvider>
  );
}
