import React from "react";
import Layout from "@theme/Layout";
import AchievementRoadmap from "@/components/roadmap/AchievementRoadmap";

export default function RoadmapPage() {
  return (
    <Layout title="Achievement Roadmap">
      <div style={{ padding: "2rem", maxWidth: "1400px", margin: "0 auto" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: "bold", marginBottom: "1.5rem" }}>
          Achievement Roadmap
        </h1>
        <p style={{ color: "#666", marginBottom: "2rem" }}>
          Track your learning journey through the AI Agent Factory curriculum.
          Unlock new chapters and milestones as you earn XP.
        </p>
        <div style={{ height: "600px", border: "1px solid #e5e7eb", borderRadius: "8px", overflow: "hidden" }}>
          <AchievementRoadmap />
        </div>
      </div>
    </Layout>
  );
}
