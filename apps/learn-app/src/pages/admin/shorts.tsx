/**
 * Admin Shorts Generation Dashboard Page
 *
 * Route: /admin/shorts
 *
 * Admin-only page for:
 * - Job queue visualization
 * - Real-time progress tracking
 * - Cost breakdown
 * - Retry failed jobs
 * - Batch generation status
 * - Automation settings
 *
 * Password protected with simple client-side auth.
 * For production, use proper server-side authentication.
 */

import { GenerationDashboard, GenerationDashboardMini, AnalyticsDashboard, CostMonitorWidget } from "../../components/shorts/admin";
import { useState, useEffect } from "react";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { Lock, AlertCircle, LogOut, LayoutDashboard, BarChart3, DollarSign, Sparkles, Settings, Clock, Play, Pause, Save, Calendar, BookOpen, ChevronDown, ChevronRight, Loader2 } from "lucide-react";

// Simple admin password - in production use proper auth
const ADMIN_PASSWORD = "agentfactory2026";

const SESSION_KEY = "admin_authenticated";

// Automation settings interface
interface AutomationSettings {
  enabled: boolean;
  scheduleTime: string; // HH:MM format
  timezone: string;
  batchLimit: number;
  targetDuration: number;
  autoRetry: boolean;
  retryAttempts: number;
  notifyOnComplete: boolean;
  selectedParts: string[];
}

const DEFAULT_SETTINGS: AutomationSettings = {
  enabled: false,
  scheduleTime: "02:00",
  timezone: "UTC",
  batchLimit: 10,
  targetDuration: 60,
  autoRetry: true,
  retryAttempts: 3,
  notifyOnComplete: true,
  selectedParts: [],
};

// Book structure types
interface Chapter {
  id: string;
  name: string;
  path: string;
}

interface BookPart {
  id: string;
  name: string;
  folder: string;
  chapters: Chapter[];
}

export default function AdminShortsPage() {
  const { siteConfig } = useDocusaurusContext();
  const shortsApiUrl = (siteConfig.customFields?.shortsApiUrl as string) || "http://localhost:8001";

  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"generation" | "analytics" | "cost" | "automation">("generation");
  const [settings, setSettings] = useState<AutomationSettings>(DEFAULT_SETTINGS);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [bookParts, setBookParts] = useState<BookPart[]>([]);
  const [expandedParts, setExpandedParts] = useState<Set<string>>(new Set());
  const [loadingParts, setLoadingParts] = useState(true);

  // Check session on mount
  useEffect(() => {
    const auth = sessionStorage.getItem(SESSION_KEY);
    if (auth === "true") {
      setIsAuthenticated(true);
    }
    // Load settings from API
    loadAutomationSettings();
    // Load book parts
    loadBookParts();
  }, []);

  const loadAutomationSettings = async () => {
    try {
      const response = await fetch(`${shortsApiUrl}/api/v1/automation/settings`);
      if (response.ok) {
        const data = await response.json();
        // Convert snake_case from API to camelCase for state
        setSettings({
          enabled: data.enabled ?? false,
          scheduleTime: data.schedule_time ?? "02:00",
          timezone: data.timezone ?? "UTC",
          batchLimit: data.batch_limit ?? 10,
          targetDuration: data.target_duration ?? 60,
          autoRetry: data.auto_retry ?? true,
          retryAttempts: data.retry_attempts ?? 3,
          notifyOnComplete: data.notify_on_complete ?? true,
          selectedParts: data.selected_parts ?? [],
        });
      }
    } catch (e) {
      console.error("Failed to load settings from API", e);
      // Fallback to localStorage
      const savedSettings = localStorage.getItem("shorts_automation_settings");
      if (savedSettings) {
        try {
          setSettings(JSON.parse(savedSettings));
        } catch (err) {
          console.error("Failed to load settings from localStorage", err);
        }
      }
    }
  };

  const loadBookParts = async () => {
    try {
      const response = await fetch(`${shortsApiUrl}/api/v1/automation/available-parts`);
      if (response.ok) {
        const data = await response.json();
        setBookParts(data.parts || []);
      }
    } catch (e) {
      console.error("Failed to load book parts:", e);
    } finally {
      setLoadingParts(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === ADMIN_PASSWORD) {
      sessionStorage.setItem(SESSION_KEY, "true");
      setIsAuthenticated(true);
      setError("");
    } else {
      setError("Invalid password");
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem(SESSION_KEY);
    setIsAuthenticated(false);
    setPassword("");
  };

  const handleSaveSettings = async () => {
    setSaveStatus("saving");
    try {
      // Save to localStorage
      localStorage.setItem("shorts_automation_settings", JSON.stringify(settings));

      // Call the API to update settings
      // Convert camelCase to snake_case for backend
      const apiSettings = {
        enabled: settings.enabled,
        schedule_time: settings.scheduleTime,
        timezone: settings.timezone,
        batch_limit: settings.batchLimit,
        target_duration: settings.targetDuration,
        auto_retry: settings.autoRetry,
        retry_attempts: settings.retryAttempts,
        notify_on_complete: settings.notifyOnComplete,
        selected_parts: settings.selectedParts,
      };

      const response = await fetch(`${shortsApiUrl}/api/v1/automation/settings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(apiSettings),
      });

      if (!response.ok) {
        throw new Error("Failed to save settings to server");
      }

      // Reload settings from API to confirm
      await loadAutomationSettings();

      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 2000);
    } catch (err) {
      console.error("Failed to save settings", err);
      setSaveStatus("error");
      setTimeout(() => setSaveStatus("idle"), 3000);
    }
  };

  const togglePartExpanded = (partId: string) => {
    setExpandedParts((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(partId)) {
        newSet.delete(partId);
      } else {
        newSet.add(partId);
      }
      return newSet;
    });
  };

  const toggleChapterSelection = (partId: string, chapterId: string) => {
    const newSelected = settings.selectedParts.includes(chapterId)
      ? settings.selectedParts.filter((id) => id !== chapterId)
      : [...settings.selectedParts, chapterId];
    setSettings({ ...settings, selectedParts: newSelected });
  };

  const toggleAllChaptersInPart = (partId: string) => {
    const part = bookParts.find((p) => p.id === partId);
    if (!part) return;

    const chapterIds = part.chapters.map((c) => c.id);
    const allSelected = chapterIds.every((id) => settings.selectedParts.includes(id));

    const newSelected = allSelected
      ? settings.selectedParts.filter((id) => !chapterIds.includes(id))
      : [...new Set([...settings.selectedParts, ...chapterIds])];

    setSettings({ ...settings, selectedParts: newSelected });
  };

  const tabs = [
    { id: "generation" as const, label: "Generation", icon: LayoutDashboard },
    { id: "analytics" as const, label: "Analytics", icon: BarChart3 },
    { id: "cost" as const, label: "Cost Monitor", icon: DollarSign },
    { id: "automation" as const, label: "Automation", icon: Settings },
  ];

  // Show password prompt if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="w-full max-w-md border border-border bg-card p-8 shadow-lg">
          <div className="mb-6 flex items-center justify-center">
            <div className="flex h-12 w-12 items-center justify-center bg-primary/10">
              <Lock className="h-6 w-6 text-primary" />
            </div>
          </div>
          <h1 className="mb-2 text-center text-2xl font-bold text-foreground">
            Admin Access
          </h1>
          <p className="mb-6 text-center text-muted-foreground">
            Enter password to access the shorts admin dashboard
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-medium text-foreground">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                placeholder="Enter admin password"
                autoFocus
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-destructive">
                <AlertCircle className="h-4 w-4 flex-shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}

            <button
              type="submit"
              className="w-full rounded-lg bg-primary px-4 py-2.5 font-medium text-primary-foreground transition-colors hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary/20"
            >
              Access Dashboard
            </button>
          </form>

          <div className="mt-6 rounded-lg bg-muted p-4">
            <p className="mb-2 text-xs font-medium text-muted-foreground">Hint for development:</p>
            <code className="text-xs text-muted-foreground">{ADMIN_PASSWORD}</code>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-primary/10 rounded-xl">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-primary/50 bg-clip-text text-transparent">
                  Shorts Admin Dashboard
                </h1>
                <p className="text-sm text-muted-foreground">
                  Monitor and manage automated short video generation
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4">
          <nav className="flex gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 font-medium border-b-2 transition-all ${
                    activeTab === tab.id
                      ? "border-primary text-foreground"
                      : "border-transparent text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <div className="mx-auto max-w-7xl px-4 py-6">
        {/* Cost widget on all pages */}
        <div className="mb-6">
          <CostMonitorWidget />
        </div>

        {activeTab === "generation" && <GenerationDashboard />}
        {activeTab === "analytics" && <AnalyticsDashboard />}
        {activeTab === "cost" && (
          <div className="rounded-lg border border-border bg-card p-6">
            <h2 className="mb-4 text-xl font-semibold text-foreground">
              Cost Monitoring Details
            </h2>
            <p className="text-muted-foreground">
              Detailed cost metrics are displayed in the widget above.
              For more detailed analysis, check the API endpoints:
            </p>
            <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <code className="rounded bg-muted px-2 py-1 text-foreground">
                  GET /api/v1/cost/daily
                </code>
                <span>- Daily cost breakdown</span>
              </li>
              <li className="flex items-center gap-2">
                <code className="rounded bg-muted px-2 py-1 text-foreground">
                  GET /api/v1/cost/monthly
                </code>
                <span>- Monthly cost with projections</span>
              </li>
              <li className="flex items-center gap-2">
                <code className="rounded bg-muted px-2 py-1 text-foreground">
                  GET /api/v1/cost/job/{'{job_id}'}
                </code>
                <span>- Per-job cost breakdown</span>
              </li>
            </ul>
          </div>
        )}
        {activeTab === "automation" && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Settings className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-foreground">Automation Settings</h2>
                  <p className="text-sm text-muted-foreground">
                    Configure automatic video generation and upload schedules
                  </p>
                </div>
              </div>
              <button
                onClick={handleSaveSettings}
                disabled={saveStatus === "saving"}
                className={`flex items-center gap-2 rounded-lg px-4 py-2 font-medium transition-colors ${
                  saveStatus === "saved"
                    ? "bg-success text-success-foreground"
                    : saveStatus === "error"
                    ? "bg-destructive text-destructive-foreground"
                    : "bg-primary text-primary-foreground hover:bg-primary/90"
                }`}
              >
                {saveStatus === "saving" ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    Saving...
                  </>
                ) : saveStatus === "saved" ? (
                  <>
                    <Save className="h-4 w-4" />
                    Saved!
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    Save Settings
                  </>
                )}
              </button>
            </div>

            {/* Status Card */}
            <div className={`rounded-lg border p-6 ${
              settings.enabled
                ? "bg-success/10 border-success/20"
                : "bg-muted border-border"
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-3 rounded-lg ${
                    settings.enabled
                      ? "bg-success/20"
                      : "bg-muted-foreground/10"
                  }`}>
                    {settings.enabled ? (
                      <Play className="h-6 w-6 text-success" />
                    ) : (
                      <Pause className="h-6 w-6 text-muted-foreground" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">
                      {settings.enabled ? "Automation Enabled" : "Automation Disabled"}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {settings.enabled
                        ? `Videos will be generated daily at ${settings.scheduleTime} ${settings.timezone}`
                        : "Toggle the switch below to enable automatic video generation"
                      }
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enabled}
                    onChange={(e) => setSettings({ ...settings, enabled: e.target.checked })}
                    className="sr-only peer"
                  />
                  <div className="w-14 h-7 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[4px] after:bg-white after:border-border after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>

            {/* Settings Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Schedule Settings */}
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
                  <Clock className="h-5 w-5 text-primary" />
                  Schedule Settings
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-foreground">
                      Daily Generation Time
                    </label>
                    <input
                      type="time"
                      value={settings.scheduleTime}
                      onChange={(e) => setSettings({ ...settings, scheduleTime: e.target.value })}
                      className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      disabled={!settings.enabled}
                    />
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-foreground">
                      Timezone
                    </label>
                    <select
                      value={settings.timezone}
                      onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                      className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      disabled={!settings.enabled}
                    >
                      <option value="UTC">UTC (Coordinated Universal Time)</option>
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="Europe/London">London (GMT/BST)</option>
                      <option value="Europe/Paris">Central European (CET)</option>
                      <option value="Asia/Kolkata">India (IST)</option>
                      <option value="Asia/Karachi">Pakistan (PKT)</option>
                      <option value="Asia/Tokyo">Japan (JST)</option>
                      <option value="Asia/Shanghai">China (CST)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Generation Settings */}
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Generation Settings
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-foreground">
                      Daily Batch Limit
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="100"
                      value={settings.batchLimit}
                      onChange={(e) => setSettings({ ...settings, batchLimit: parseInt(e.target.value) || 1 })}
                      className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      disabled={!settings.enabled}
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Maximum videos to generate per day
                    </p>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-foreground">
                      Target Duration (seconds)
                    </label>
                    <input
                      type="number"
                      min="30"
                      max="180"
                      step="10"
                      value={settings.targetDuration}
                      onChange={(e) => setSettings({ ...settings, targetDuration: parseInt(e.target.value) || 60 })}
                      className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      disabled={!settings.enabled}
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Target length for generated videos
                    </p>
                  </div>
                </div>
              </div>

              {/* Retry Settings */}
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
                  <Play className="h-5 w-5 text-primary" />
                  Retry Settings
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-foreground">Auto-Retry Failed Jobs</p>
                      <p className="text-sm text-muted-foreground">
                        Automatically retry failed generation jobs
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.autoRetry}
                        onChange={(e) => setSettings({ ...settings, autoRetry: e.target.checked })}
                        className="sr-only peer"
                        disabled={!settings.enabled}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-foreground">
                      Maximum Retry Attempts
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="10"
                      value={settings.retryAttempts}
                      onChange={(e) => setSettings({ ...settings, retryAttempts: parseInt(e.target.value) || 1 })}
                      className="w-full rounded-lg border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                      disabled={!settings.enabled || !settings.autoRetry}
                    />
                  </div>
                </div>
              </div>

              {/* Notification Settings */}
              <div className="rounded-lg border border-border bg-card p-6">
                <h3 className="mb-4 flex items-center gap-2 font-semibold text-foreground">
                  <Calendar className="h-5 w-5 text-primary" />
                  Notification Settings
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-foreground">Notify on Batch Complete</p>
                      <p className="text-sm text-muted-foreground">
                        Get notified when daily batch generation completes
                      </p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifyOnComplete}
                        onChange={(e) => setSettings({ ...settings, notifyOnComplete: e.target.checked })}
                        className="sr-only peer"
                        disabled={!settings.enabled}
                      />
                      <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/20 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Content Selection with Real Chapters */}
            <div className="rounded-lg border border-border bg-card p-6">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="flex items-center gap-2 font-semibold text-foreground">
                  <BookOpen className="h-5 w-5 text-primary" />
                  Content Selection
                </h3>
                <div className="text-sm text-muted-foreground">
                  {settings.selectedParts.length} chapter{settings.selectedParts.length !== 1 ? "s" : ""} selected
                </div>
              </div>
              <p className="mb-4 text-sm text-muted-foreground">
                Select which parts/chapters to include in automatic generation. Leave empty to process all new lessons.
              </p>

              {loadingParts ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                  <span className="ml-2 text-muted-foreground">Loading book structure...</span>
                </div>
              ) : bookParts.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  No book content found. Check the docs directory.
                </div>
              ) : (
                <div className="space-y-2">
                  {bookParts.map((part) => {
                    const isExpanded = expandedParts.has(part.id);
                    const partChapterIds = part.chapters.map((c) => c.id);
                    const allSelected = partChapterIds.length > 0 && partChapterIds.every((id) => settings.selectedParts.includes(id));
                    const someSelected = partChapterIds.some((id) => settings.selectedParts.includes(id));

                    return (
                      <div key={part.id} className="border border-border rounded-lg overflow-hidden">
                        <button
                          onClick={() => togglePartExpanded(part.id)}
                          className="w-full flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <input
                              type="checkbox"
                              checked={allSelected}
                              ref={(el) => {
                                if (el && someSelected && !allSelected) {
                                  el.indeterminate = true;
                                }
                              }}
                              onChange={(e) => {
                                e.stopPropagation();
                                toggleAllChaptersInPart(part.id);
                              }}
                              className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                              disabled={!settings.enabled}
                            />
                            <span className="font-medium text-foreground">
                              Part {part.id}: {part.name}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              ({part.chapters.length} chapters)
                            </span>
                          </div>
                          {isExpanded ? (
                            <ChevronDown className="h-5 w-5 text-muted-foreground" />
                          ) : (
                            <ChevronRight className="h-5 w-5 text-muted-foreground" />
                          )}
                        </button>

                        {isExpanded && part.chapters.length > 0 && (
                          <div className="border-t border-border bg-muted/30 p-2">
                            {part.chapters.map((chapter) => (
                              <label
                                key={chapter.id}
                                className={`flex items-center gap-3 px-4 py-2 rounded-lg cursor-pointer transition-colors ${
                                  settings.selectedParts.includes(chapter.id)
                                    ? "bg-primary/10"
                                    : "hover:bg-muted/50"
                                }`}
                              >
                                <input
                                  type="checkbox"
                                  checked={settings.selectedParts.includes(chapter.id)}
                                  onChange={() => toggleChapterSelection(part.id, chapter.id)}
                                  className="h-4 w-4 rounded border-border text-primary focus:ring-primary"
                                  disabled={!settings.enabled}
                                />
                                <span className="text-sm text-foreground">{chapter.name}</span>
                              </label>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Quick Actions */}
              <div className="mt-4 pt-4 border-t border-border flex gap-2">
                <button
                  onClick={() => setSettings({ ...settings, selectedParts: [] })}
                  disabled={!settings.enabled}
                  className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Clear All
                </button>
                <button
                  onClick={() => {
                    const allIds = bookParts.flatMap((p) => p.chapters.map((c) => c.id));
                    setSettings({ ...settings, selectedParts: allIds });
                  }}
                  disabled={!settings.enabled}
                  className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Select All
                </button>
              </div>
            </div>

            {/* Info Box */}
            <div className="rounded-lg border border-primary/50 bg-primary/10 p-6">
              <h4 className="mb-2 font-semibold text-primary">How Automation Works</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>At the scheduled time, the system scans for new or updated lessons</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Videos are generated in batches according to your batch limit setting</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Only selected chapters will be processed (or all if none selected)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Failed jobs are automatically retried if auto-retry is enabled</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">•</span>
                  <span>Completed videos are automatically uploaded to the CDN</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
