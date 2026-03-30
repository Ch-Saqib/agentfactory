/**
 * CostMonitorWidget - Cost monitoring and visualization component
 *
 * Features:
 * - Daily/monthly cost tracking
 * - Budget alerts when thresholds exceeded
 * - Cost breakdown by service
 * - API usage visualization
 * - Projected monthly cost
 */

import React, { useState, useCallback, useEffect } from "react";
import { getShortsApiClient } from "../../../lib/shorts-api";
import { DollarSign, TrendingUp, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";

/**
 * Cost summary data
 */
interface CostSummary {
  today: {
    cost_usd: number;
    video_count: number;
    alert_exceeded: boolean;
  };
  this_month: {
    cost_usd: number;
    video_count: number;
    alert_exceeded: boolean;
    projected_usd: number;
  };
  all_time: {
    total_videos: number;
    total_cost_usd: number;
    avg_cost_per_video: number;
  };
}

/**
 * Budget alert data
 */
interface BudgetAlert {
  severity: "warning" | "critical";
  type: string;
  threshold: number;
  actual: number;
  message: string;
  date?: string;
  year?: number;
  month?: number;
}

/**
 * Props for CostMonitorWidget
 */
interface CostMonitorWidgetProps {
  /** Auto-refresh interval in milliseconds */
  refreshInterval?: number;
}

/**
 * Cost monitoring widget component
 */
export function CostMonitorWidget({
  refreshInterval = 60000, // 1 minute
}: CostMonitorWidgetProps) {
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [alerts, setAlerts] = useState<BudgetAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const apiClient = getShortsApiClient();

  // Load cost data
  const loadData = useCallback(async () => {
    try {
      setError(null);
      const [summaryData, alertsData] = await Promise.all([
        apiClient.getCostSummary(),
        apiClient.checkBudgetAlerts(),
      ]);
      setSummary(summaryData);
      setAlerts(alertsData.alerts);
    } catch (err: any) {
      setError(err.message || "Failed to load cost data");
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(loadData, refreshInterval);
    return () => clearInterval(interval);
  }, [loadData, refreshInterval]);

  if (loading && !summary) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-border border-t-primary" />
        <div className="text-sm text-muted-foreground">Loading cost data...</div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-card">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <DollarSign className="h-5 w-5 text-primary" />
          </div>
          <h3 className="font-semibold text-foreground">Cost Monitor</h3>
          {alerts.length > 0 && (
            <span className="rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-medium text-destructive">
              {alerts.length} alert{alerts.length > 1 ? "s" : ""}
            </span>
          )}
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          {showDetails ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Hide Details
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              Show Details
            </>
          )}
        </button>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="border-b border-border p-4">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`mb-2 flex items-start gap-3 rounded-md p-3 last:mb-0 ${
                alert.severity === "critical"
                  ? "bg-destructive/10 text-destructive"
                  : "bg-warning/10 text-warning"
              }`}
            >
              <AlertTriangle className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="font-medium">{alert.message}</div>
                <div className="mt-1 text-xs opacity-75">
                  Threshold: ${alert.threshold.toFixed(2)} | Actual: $
                  {alert.actual.toFixed(2)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div className="p-4">
          <div className="grid grid-cols-3 gap-4">
            {/* Today */}
            <div className="text-center">
              <div className="text-xs text-muted-foreground">Today</div>
              <div
                className={`text-lg font-semibold ${
                  summary.today.alert_exceeded ? "text-destructive" : "text-foreground"
                }`}
              >
                ${summary.today.cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                {summary.today.video_count} video{summary.today.video_count !== 1 ? "s" : ""}
              </div>
            </div>

            {/* This Month */}
            <div className="text-center">
              <div className="text-xs text-muted-foreground">This Month</div>
              <div
                className={`text-lg font-semibold ${
                  summary.this_month.alert_exceeded ? "text-destructive" : "text-foreground"
                }`}
              >
                ${summary.this_month.cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                {summary.this_month.video_count} video{summary.this_month.video_count !== 1 ? "s" : ""}
              </div>
            </div>

            {/* All Time */}
            <div className="text-center">
              <div className="text-xs text-muted-foreground">All Time</div>
              <div className="text-lg font-semibold text-foreground">
                ${summary.all_time.total_cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-muted-foreground">
                {summary.all_time.total_videos} video{summary.all_time.total_videos !== 1 ? "s" : ""}
              </div>
            </div>
          </div>

          {/* Projected */}
          {showDetails && summary.this_month.projected_usd > 0 && (
            <div className="mt-4 rounded-md bg-muted p-3">
              <div className="mb-1 flex items-center justify-center gap-2 text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3" />
                Projected Monthly
              </div>
              <div className="text-lg font-semibold text-foreground">
                ${summary.this_month.projected_usd.toFixed(2)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="border-t border-border p-4 text-center text-sm text-destructive">
          {error}
        </div>
      )}
    </div>
  );
}

/**
 * Compact inline version for dashboards
 */
export function CostMonitorInline() {
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [hasAlerts, setHasAlerts] = useState(false);
  const apiClient = getShortsApiClient();

  useEffect(() => {
    const load = async () => {
      try {
        const [data, alerts] = await Promise.all([
          apiClient.getCostSummary(),
          apiClient.checkBudgetAlerts(),
        ]);
        setSummary(data);
        setHasAlerts(alerts.alert_count > 0);
      } catch (err) {
        console.warn("Failed to load cost summary:", err);
      }
    };
    load();
    const interval = setInterval(load, 120000); // 2 minutes
    return () => clearInterval(interval);
  }, [apiClient]);

  if (!summary) {
    return <div className="text-sm text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4">
      <div>
        <div className="text-xs text-muted-foreground">Month to Date</div>
        <div
          className={`text-lg font-semibold ${
            summary.this_month.alert_exceeded ? "text-destructive" : "text-foreground"
          }`}
        >
          ${summary.this_month.cost_usd.toFixed(2)}
        </div>
      </div>
      {hasAlerts && (
        <>
          <div className="h-8 w-px bg-border" />
          <div className="rounded-full bg-destructive/10 px-3 py-1 text-xs font-medium text-destructive">
            Budget Alert
          </div>
        </>
      )}
    </div>
  );
}
