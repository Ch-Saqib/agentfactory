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
      <div className="flex items-center gap-3 rounded-lg border border-gray-800 bg-gray-900 p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-700 border-t-blue-500" />
        <div className="text-sm text-gray-400">Loading cost data...</div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-gray-800 bg-gray-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 p-4">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-white">💰 Cost Monitor</h3>
          {alerts.length > 0 && (
            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-xs font-medium text-red-400">
              {alerts.length} alert{alerts.length > 1 ? "s" : ""}
            </span>
          )}
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-gray-400 hover:text-white"
        >
          {showDetails ? "Hide" : "Show"} Details
        </button>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="border-b border-gray-800 p-4">
          {alerts.map((alert, index) => (
            <div
              key={index}
              className={`mb-2 flex items-start gap-3 rounded-md p-3 ${
                alert.severity === "critical"
                  ? "bg-red-500/10 text-red-400"
                  : "bg-yellow-500/10 text-yellow-400"
              }`}
            >
              <span className="text-xl">
                {alert.severity === "critical" ? "🚨" : "⚠️"}
              </span>
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
              <div className="text-xs text-gray-500">Today</div>
              <div
                className={`text-lg font-semibold ${
                  summary.today.alert_exceeded ? "text-red-400" : "text-white"
                }`}
              >
                ${summary.today.cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">
                {summary.today.video_count} videos
              </div>
            </div>

            {/* This Month */}
            <div className="text-center">
              <div className="text-xs text-gray-500">This Month</div>
              <div
                className={`text-lg font-semibold ${
                  summary.this_month.alert_exceeded ? "text-red-400" : "text-white"
                }`}
              >
                ${summary.this_month.cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">
                {summary.this_month.video_count} videos
              </div>
            </div>

            {/* All Time */}
            <div className="text-center">
              <div className="text-xs text-gray-500">All Time</div>
              <div className="text-lg font-semibold text-white">
                ${summary.all_time.total_cost_usd.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">
                {summary.all_time.total_videos} videos
              </div>
            </div>
          </div>

          {/* Projected */}
          {showDetails && summary.this_month.projected_usd > 0 && (
            <div className="mt-4 rounded-md bg-gray-950 p-3">
              <div className="mb-1 text-xs text-gray-500">Projected Monthly</div>
              <div className="text-lg font-semibold text-white">
                ${summary.this_month.projected_usd.toFixed(2)}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="border-t border-gray-800 p-4 text-center text-sm text-red-400">
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
    return <div className="text-sm text-gray-500">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4">
      <div>
        <div className="text-xs text-gray-500">Month to Date</div>
        <div
          className={`text-lg font-semibold ${
            summary.this_month.alert_exceeded ? "text-red-400" : "text-white"
          }`}
        >
          ${summary.this_month.cost_usd.toFixed(2)}
        </div>
      </div>
      {hasAlerts && (
        <>
          <div className="h-8 w-px bg-gray-800" />
          <div className="rounded-full bg-red-500/20 px-3 py-1 text-xs font-medium text-red-400">
            Budget Alert
          </div>
        </>
      )}
    </div>
  );
}
