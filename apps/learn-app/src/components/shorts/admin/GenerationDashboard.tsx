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
    queued: "bg-yellow-500/20 text-yellow-400",
    processing: "bg-blue-500/20 text-blue-400",
    completed: "bg-green-500/20 text-green-400",
    failed: "bg-red-500/20 text-red-400",
  };

  const labels = {
    queued: "Queued",
    processing: "Processing",
    completed: "Completed",
    failed: "Failed",
  };

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-medium ${styles[status]}`}
    >
      {labels[status]}
    </span>
  );
}

/**
 * Progress bar component
 */
function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="relative h-2 w-full overflow-hidden rounded-full bg-gray-800">
      <div
        className="absolute h-full bg-blue-500 transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
      <span className="absolute inset-0 flex items-center justify-center text-xs text-white">
        {progress}%
      </span>
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
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-700 border-t-blue-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-white">
            Shorts Generation Dashboard
          </h1>
          <p className="text-gray-400">
            Monitor and manage automated short video generation
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-500 bg-red-500/10 p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Statistics Cards */}
        {stats && (
          <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Total Jobs */}
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
              <div className="mb-2 text-sm text-gray-400">Total Jobs</div>
              <div className="text-3xl font-bold text-white">{stats.totalJobs}</div>
            </div>

            {/* Processing */}
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
              <div className="mb-2 text-sm text-gray-400">Processing</div>
              <div className="flex items-center gap-3">
                <div className="h-3 w-3 animate-pulse rounded-full bg-blue-500" />
                <div className="text-3xl font-bold text-white">
                  {stats.processing}
                </div>
              </div>
            </div>

            {/* Success Rate */}
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
              <div className="mb-2 text-sm text-gray-400">Success Rate</div>
              <div
                className={`text-3xl font-bold ${
                  stats.successRate >= 80
                    ? "text-green-400"
                    : stats.successRate >= 60
                    ? "text-yellow-400"
                    : "text-red-400"
                }`}
              >
                {stats.successRate.toFixed(1)}%
              </div>
            </div>

            {/* Total Cost */}
            <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
              <div className="mb-2 text-sm text-gray-400">Total Cost</div>
              <div className="text-3xl font-bold text-white">
                ${stats.totalCostUsd.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">
                ${stats.avgCostPerVideo.toFixed(4)}/video
              </div>
            </div>
          </div>
        )}

        {/* Storage Statistics */}
        {storageStats && (
          <div className="mb-8 rounded-lg border border-gray-800 bg-gray-900 p-6">
            <h2 className="mb-4 text-xl font-semibold text-white">
              Storage Statistics
            </h2>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <div className="text-sm text-gray-400">Videos</div>
                <div className="text-lg font-semibold text-white">
                  {storageStats.videos.count}
                </div>
                <div className="text-xs text-gray-500">
                  {formatBytes(storageStats.videos.total_bytes)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Thumbnails</div>
                <div className="text-lg font-semibold text-white">
                  {storageStats.thumbnails.count}
                </div>
                <div className="text-xs text-gray-500">
                  {formatBytes(storageStats.thumbnails.total_bytes)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Captions</div>
                <div className="text-lg font-semibold text-white">
                  {storageStats.captions.count}
                </div>
                <div className="text-xs text-gray-500">
                  {formatBytes(storageStats.captions.total_bytes)}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-400">Total Storage</div>
                <div className="text-lg font-semibold text-white">
                  {storageStats.total.total_gb.toFixed(2)} GB
                </div>
                <div className="text-xs text-gray-500">
                  ${storageStats.total.estimated_monthly_cost_usd.toFixed(2)}/mo
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Status Filter Tabs */}
        <div className="mb-6 flex flex-wrap gap-2 border-b border-gray-800">
          {(["all", "queued", "processing", "completed", "failed"] as const).map(
            (status) => (
              <button
                key={status}
                onClick={() => {
                  setSelectedStatus(status);
                  setPage(1);
                }}
                className={`px-4 py-2 font-medium capitalize transition-colors ${
                  selectedStatus === status
                    ? "border-b-2 border-blue-500 text-white"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {status === "all" ? "All Jobs" : status}
                {stats && status !== "all" && (
                  <span className="ml-2 rounded-full bg-gray-800 px-2 py-0.5 text-xs">
                    {getStatusCount(status)}
                  </span>
                )}
              </button>
            )
          )}
        </div>

        {/* Jobs Table */}
        <div className="overflow-hidden rounded-lg border border-gray-800">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Job ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Lesson
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Progress
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-400">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {jobs.map((job) => (
                <tr key={job.job_id} className="bg-gray-950">
                  <td className="px-6 py-4 text-sm text-gray-300">
                    <code className="rounded bg-gray-900 px-2 py-1">
                      {job.job_id.slice(0, 8)}
                    </code>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
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
                      <span className="text-sm text-gray-400">Complete</span>
                    ) : (
                      <span className="text-sm text-gray-500">—</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {new Date(job.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4">
                    {job.status === "failed" && (
                      <button
                        onClick={() => handleRetryJob(job.job_id)}
                        className="rounded bg-blue-500 px-3 py-1 text-sm font-medium text-white hover:bg-blue-600"
                      >
                        Retry
                      </button>
                    )}
                    {job.video_id && (
                      <a
                        href={`/shorts?video=${job.video_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-sm text-blue-400 hover:text-blue-300"
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
            <div className="py-12 text-center text-gray-500">
              No jobs found
            </div>
          )}
        </div>

        {/* Pagination */}
        {jobs.length === pageSize && (
          <div className="mt-4 flex justify-center">
            <button
              onClick={() => setPage((p) => p + 1)}
              className="rounded-lg border border-gray-800 bg-gray-900 px-6 py-2 text-white hover:bg-gray-800"
            >
              Load More
            </button>
          </div>
        )}
      </div>
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
    return <div className="text-sm text-gray-500">Loading...</div>;
  }

  return (
    <div className="flex items-center gap-4 rounded-lg border border-gray-800 bg-gray-900 p-4">
      <div>
        <div className="text-xs text-gray-400">Active Jobs</div>
        <div className="text-lg font-semibold text-white">
          {stats.queued + stats.processing}
        </div>
      </div>
      <div className="h-8 w-px bg-gray-800" />
      <div>
        <div className="text-xs text-gray-400">Success Rate</div>
        <div
          className={`text-lg font-semibold ${
            stats.successRate >= 80
              ? "text-green-400"
              : stats.successRate >= 60
              ? "text-yellow-400"
              : "text-red-400"
          }`}
        >
          {stats.successRate.toFixed(0)}%
        </div>
      </div>
      <div className="h-8 w-px bg-gray-800" />
      <div>
        <div className="text-xs text-gray-400">Total Cost</div>
        <div className="text-lg font-semibold text-white">
          ${stats.totalCostUsd.toFixed(2)}
        </div>
      </div>
    </div>
  );
}
