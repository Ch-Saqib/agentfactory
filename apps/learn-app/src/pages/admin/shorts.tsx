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
 */

import { GenerationDashboard, GenerationDashboardMini, AnalyticsDashboard, CostMonitorWidget } from "../../components/shorts/admin";
import { useState } from "react";

export default function AdminShortsPage() {
  const [activeTab, setActiveTab] = useState<"generation" | "analytics" | "cost">("generation");

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto max-w-7xl px-4 py-4">
          <h1 className="text-2xl font-bold text-white">
            Shorts Admin Dashboard
          </h1>
          <p className="text-gray-400">
            Monitor and manage automated short video generation
          </p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-800 bg-gray-900">
        <div className="mx-auto max-w-7xl px-4">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab("generation")}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                activeTab === "generation"
                  ? "border-blue-500 text-white"
                  : "border-transparent text-gray-400 hover:text-white"
              }`}
            >
              Generation
            </button>
            <button
              onClick={() => setActiveTab("analytics")}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                activeTab === "analytics"
                  ? "border-blue-500 text-white"
                  : "border-transparent text-gray-400 hover:text-white"
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab("cost")}
              className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                activeTab === "cost"
                  ? "border-blue-500 text-white"
                  : "border-transparent text-gray-400 hover:text-white"
              }`}
            >
              Cost Monitor
            </button>
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
          <div className="rounded-lg border border-gray-800 bg-gray-900 p-6">
            <h2 className="mb-4 text-xl font-semibold text-white">
              Cost Monitoring Details
            </h2>
            <p className="text-gray-400">
              Detailed cost metrics are displayed in the widget above.
              For more detailed analysis, check the API endpoints:
            </p>
            <ul className="mt-4 space-y-2 text-sm text-gray-400">
              <li className="flex items-center gap-2">
                <code className="rounded bg-gray-950 px-2 py-1">
                  GET /api/v1/cost/daily
                </code>
                <span>- Daily cost breakdown</span>
              </li>
              <li className="flex items-center gap-2">
                <code className="rounded bg-gray-950 px-2 py-1">
                  GET /api/v1/cost/monthly
                </code>
                <span>- Monthly cost with projections</span>
              </li>
              <li className="flex items-center gap-2">
                <code className="rounded bg-gray-950 px-2 py-1">
                  GET /api/v1/cost/job/{job_id}
                </code>
                <span>- Per-job cost breakdown</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
