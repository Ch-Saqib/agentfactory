/**
 * GenerationDashboard - Admin dashboard for shorts generation
 *
 * Features:
 * - Job queue visualization
 * - Real-time progress tracking
 * - Cost breakdown (actual vs estimated)
 * - Success/failure rate
 * - Retry failed jobs
 * - Batch generation status
 */

import React, { useState, useCallback, useEffect } from "react";
import { getShortsApiClient } from "../../../lib/shorts-api";
import { RefreshCw, CheckCircle2, XCircle, Clock, Loader2, FileVideo, HardDrive, DollarSign, TrendingUp } from "lucide-react";

/**
 * Job status from API
 */
interface GenerationJob {
  job_id: string;
  lesson_path: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  error_message?: string;
  retry_count: number;
  created_at: string;
  completed_at?: string;
  video_id?: string;
}

/**
 * Dashboard statistics
 */
interface DashboardStats {
  totalJobs: number;
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  successRate: number;
  totalCostUsd: number;
  avgCostPerVideo: number;
}

/**
 * Storage statistics
 */
interface StorageStats {
  videos: { count: number; total_bytes: number };
  thumbnails: { count: number; total_bytes: number };
  captions: { count: number; total_bytes: number };
  total: {
    count: number;
    total_bytes: number;
    total_gb: number;
    estimated_monthly_cost_usd: number;
  };
}

/**
 * Props for GenerationDashboard
 */
interface GenerationDashboardProps {
  /** Auto-refresh interval in milliseconds */
  refreshInterval?: number;
  /** Show only failed jobs */
  showFailedOnly?: boolean;
}

/**
 * Status badge component
 */
function StatusBadge({ status }: { status: GenerationJob["status"] }) {
  const styles = {
    queued: "bg-warning/10 text-warning border-warning/20",
    processing: "bg-primary/10 text-primary border-primary/20",
    completed: "bg-success/10 text-success border-success/20",
    failed: "bg-destructive/10 text-destructive border-destructive/20",
  };

  const icons = {
    queued: <Clock className="h-3 w-3" />,
    processing: <Loader2 className="h-3 w-3 animate-spin" />,
    completed: <CheckCircle2 className="h-3 w-3" />,
    failed: <XCircle className="h-3 w-3" />,
  };

  const labels = {
    queued: "Queued",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${styles[status]}`}
    >
      {icons[status]}
      {labels[status]}
    </span>
  );
}

/**
 * Progress bar component
 */
function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
      <div
        className="absolute h-full bg-primary transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
      <span className="absolute inset-0 flex items-center justify-center text-xs text-foreground">
        {progress}%
      </span>
    </div>
  );
}

/**
 * Stat card component
 */
function StatCard({
  icon: Icon,
  label,
  value,
  subtext,
  variant = "default",
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  subtext?: string;
  variant?: "default" | "success" | "warning" | "destructive";
}) {
  const variantStyles = {
    default: "text-foreground",
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  };

  return (
    <div className="rounded-lg border border-border bg-card p-6">
      <div className="mb-3 flex items-center gap-2 text-muted-foreground">
        <Icon className="h-4 w-4" />
        <span className="text-sm">{label}</span>
      </div>
      <div className={`text-3xl font-bold ${variantStyles[variant]}`}>{value}</div>
      {subtext && <div className="mt-1 text-xs text-muted-foreground">{subtext}</div>}
    </div>
  );
}

/**
 * Main dashboard component
 */
export function GenerationDashboard({
  refreshInterval = 5000,
  showFailedOnly = false,
}: GenerationDashboardProps) {
  const [jobs, setJobs] = useState<GenerationJob[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [storageStats, setStorageStats] = useState<StorageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<
    GenerationJob["status"] | "all"
  >("all");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const apiClient = getShortsApiClient();

  // Load jobs
  const loadJobs = useCallback(async () => {
    try {
      setError(null);
      const statusFilter =
        selectedStatus === "all" ? undefined : (selectedStatus as any);

      const result = await apiClient.listJobs({
        status: showFailedOnly ? "failed" : statusFilter,
        page,
        pageSize,
      });

      setJobs(result.jobs);

      // Calculate statistics from all jobs
      const allJobsResult = await apiClient.listJobs({ pageSize: 1000 });
      const allJobs = allJobsResult.jobs;

      const completed = allJobs.filter((j) => j.status === "completed");
      const failed = allJobs.filter((j) => j.status === "failed");

      setStats({
        totalJobs: allJobs.length,
        queued: allJobs.filter((j) => j.status === "queued").length,
        processing: allJobs.filter((j) => j.status === "processing").length,
        completed: completed.length,
        failed: failed.length,
        successRate: allJobs.length > 0
          ? (completed.length / allJobs.length) * 100
          : 0,
        totalCostUsd: completed.length * 0.006, // $0.006 per video
        avgCostPerVideo: 0.006,
      });
    } catch (err: any) {
      setError(err.message || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  }, [apiClient, selectedStatus, page, pageSize, showFailedOnly]);

  // Load storage stats
  const loadStorageStats = useCallback(async () => {
    try {
      const stats = await apiClient.getStorageStats();
      setStorageStats(stats);
    } catch (err) {
      // Storage stats may not be available
      console.warn("Failed to load storage stats:", err);
    }
  }, [apiClient]);

  // Retry failed job
  const handleRetryJob = useCallback(
    async (jobId: string) => {
      try {
        await apiClient.retryJob(jobId);
        await loadJobs(); // Refresh jobs
      } catch (err: any) {
        setError(err.message || "Failed to retry job");
      }
    },
    [apiClient, loadJobs]
  );

  // Initial load
  useEffect(() => {
    loadJobs();
    loadStorageStats();
  }, [loadJobs, loadStorageStats]);

  // Auto-refresh
  useEffect(() => {
    const interval = setInterval(() => {
      loadJobs();
      loadStorageStats();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [loadJobs, loadStorageStats, refreshInterval]);

  // Format bytes to human readable
  function formatBytes(bytes: number): string {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`;
  }

  // Format lesson path for display
  function formatLessonPath(path: string): string {
    const parts = path.split("/");
    if (parts.length >= 3) {
      return `${parts[0]}/${parts[1]}...`;
    }
    return path;
  }

  // Get stats for a specific status
  const getStatusCount = (status: GenerationJob["status"]): number => {
    if (!stats) return 0;
    switch (status) {
      case "queued":
        return stats.queued;
      case "processing":
        return stats.processing;
      case "completed":
        return stats.completed;
      case "failed":
        return stats.failed;
    }
  };

  if (loading && !stats) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Error Alert */}
      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={FileVideo}
            label="Total Jobs"
            value={stats.totalJobs}
          />
          <StatCard
            icon={Loader2}
            label="Processing"
            value={stats.processing}
          />
          <StatCard
            icon={TrendingUp}
            label="Success Rate"
            value={`${stats.successRate.toFixed(1)}%`}
            variant={
              stats.successRate >= 80
                ? "success"
                : stats.successRate >= 60
                ? "warning"
                : "destructive"
            }
          />
          <StatCard
            icon={DollarSign}
            label="Total Cost"
            value={`$${stats.totalCostUsd.toFixed(2)}`}
            subtext={`$${stats.avgCostPerVideo.toFixed(4)}/video`}
          />
        </div>
      )}

      {/* Storage Statistics */}
      {storageStats && (
        <div className="rounded-lg border border-border bg-card p-6">
          <div className="mb-4 flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <HardDrive className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold text-foreground">
              Storage Statistics
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="rounded-lg bg-muted p-4">
              <div className="text-sm text-muted-foreground">Videos</div>
              <div className="text-lg font-semibold text-foreground">
                {storageStats.videos.count}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatBytes(storageStats.videos.total_bytes)}
              </div>
            </div>
            <div className="rounded-lg bg-muted p-4">
              <div className="text-sm text-muted-foreground">Thumbnails</div>
              <div className="text-lg font-semibold text-foreground">
                {storageStats.thumbnails.count}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatBytes(storageStats.thumbnails.total_bytes)}
              </div>
            </div>
            <div className="rounded-lg bg-muted p-4">
              <div className="text-sm text-muted-foreground">Captions</div>
              <div className="text-lg font-semibold text-foreground">
                {storageStats.captions.count}
              </div>
              <div className="text-xs text-muted-foreground">
                {formatBytes(storageStats.captions.total_bytes)}
              </div>
            </div>
            <div className="rounded-lg bg-muted p-4">
              <div className="text-sm text-muted-foreground">Total Storage</div>
              <div className="text-lg font-semibold text-foreground">
                {storageStats.total.total_gb.toFixed(2)} GB
              </div>
              <div className="text-xs text-muted-foreground">
                ${storageStats.total.estimated_monthly_cost_usd.toFixed(2)}/mo
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status Filter Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-border">
        {(["all", "queued", "processing", "completed", "failed"] as const).map(
          (status) => (
            <button
              key={status}
              onClick={() => {
                setSelectedStatus(status);
                setPage(1);
              }}
              className={`px-4 py-2 font-medium capitalize transition-all ${
                selectedStatus === status
                  ? "border-b-2 border-primary text-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {status === "all" ? "All Jobs" : status}
              {stats && status !== "all" && (
                <span className="ml-2 rounded-full bg-muted px-2 py-0.5 text-xs">
                  {getStatusCount(status)}
                </span>
              )}
            </button>
          )
        )}
      </div>

      {/* Jobs Table */}
      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Job ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Lesson
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Progress
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium uppercase text-muted-foreground">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {jobs.map((job) => (
              <tr key={job.job_id} className="bg-card hover:bg-muted/50">
                <td className="px-6 py-4 text-sm text-foreground">
                  <code className="rounded bg-muted px-2 py-1 text-xs">
                    {job.job_id.slice(0, 8)}
                  </code>
                </td>
                <td className="px-6 py-4 text-sm text-foreground">
                  <div className="max-w-xs truncate" title={job.lesson_path}>
                    {formatLessonPath(job.lesson_path)}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <StatusBadge status={job.status} />
                </td>
                <td className="px-6 py-4">
                  {job.status === "processing" ? (
                    <div className="w-48">
                      <ProgressBar progress={job.progress} />
                    </div>
                  ) : job.status === "completed" ? (
                    <span className="text-sm text-muted-foreground">Complete</span>
                  ) : (
                    <span className="text-sm text-muted-foreground">—</span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground">
                  {new Date(job.created_at).toLocaleString()}
                </td>
                <td className="px-6 py-4">
                  {job.status === "failed" && (
                    <button
                      onClick={() => handleRetryJob(job.job_id)}
                      className="flex items-center gap-1.5 rounded bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
                    >
                      <RefreshCw className="h-3 w-3" />
                      Retry
                    </button>
                  )}
                  {job.video_id && (
                    <a
                      href={`/shorts?video=${job.video_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-sm text-primary hover:underline"
                    >
                      View
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {jobs.length === 0 && !loading && (
          <div className="py-12 text-center text-muted-foreground">
            No jobs found
          </div>
        )}
      </div>

      {/* Pagination */}
      {jobs.length === pageSize && (
        <div className="flex justify-center">
          <button
            onClick={() => setPage((p) => p + 1)}
            className="rounded-lg border border-border bg-card px-6 py-2 text-foreground hover:bg-muted"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}

/**
 * Compact version for embedding in other pages
 */
export function GenerationDashboardMini() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const apiClient = getShortsApiClient();

  useEffect(() => {
    const loadStats = async () => {
      const result = await apiClient.listJobs({ pageSize: 1000 });
      const allJobs = result.jobs;
      const completed = allJobs.filter((j) => j.status === "completed");
      const failed = allJobs.filter((j) => j.status === "failed");

      setStats({
        totalJobs: allJobs.length,
        queued: allJobs.filter((j) => j.status === "queued").length,
        processing: allJobs.filter((j) => j.status === "processing").length,
        completed: completed.length,
        failed: failed.length,
        successRate: allJobs.length > 0
          ? (completed.length / allJobs.length) * 100
          : 0,
        totalCostUsd: completed.length * 0.006,
        avgCostPerVideo: 0.006,
      });
    };
    loadStats();
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, [apiClient]);

  if (!stats) {
    return <div className="text-sm text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4 rounded-lg border border-border bg-card p-4">
      <div>
        <div className="text-xs text-muted-foreground">Active Jobs</div>
        <div className="text-lg font-semibold text-foreground">
          {stats.queued + stats.processing}
        </div>
      </div>
      <div className="h-8 w-px bg-border" />
      <div>
        <div className="text-xs text-muted-foreground">Success Rate</div>
        <div
          className={`text-lg font-semibold ${
            stats.successRate >= 80
              ? "text-success"
              : stats.successRate >= 60
              ? "text-warning"
              : "text-destructive"
          }`}
        >
          {stats.successRate.toFixed(0)}%
        </div>
      </div>
      <div className="h-8 w-px bg-border" />
      <div>
        <div className="text-xs text-muted-foreground">Total Cost</div>
        <div className="text-lg font-semibold text-foreground">
          ${stats.totalCostUsd.toFixed(2)}
        </div>
      </div>
    </div>
  );
}
