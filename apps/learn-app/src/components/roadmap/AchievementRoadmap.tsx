import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useReactFlow,
  type Node,
  type Edge,
  type ReactFlowInstance,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { getRoadmap, syncRoadmap, type RoadmapResponse } from "@/lib/progress-api";
import { RoadmapNode } from "./RoadmapNode";
import { RoadmapControls } from "./RoadmapControls";
import { cn } from "@/lib/utils";
import "@/components/progress/gamification.css";

const nodeTypes = {
  roadmapNode: RoadmapNode,
};

interface AchievementRoadmapProps {
  className?: string;
  onNodeClick?: (nodeId: string) => void;
}

function RoadmapControlsWrapper({
  onNodeClick,
}: {
  onNodeClick?: (nodeId: string) => void;
}) {
  const { zoomIn, zoomOut, fitView, setViewport } = useReactFlow();

  const handleZoomIn = () => zoomIn({ duration: 300 });
  const handleZoomOut = () => zoomOut({ duration: 300 });
  const handleFitView = () => fitView({ duration: 300, padding: 0.2 });
  const handleReset = () => setViewport({ x: 0, y: 0, zoom: 1 }, { duration: 300 });

  return (
    <RoadmapControls
      onZoomIn={handleZoomIn}
      onZoomOut={handleZoomOut}
      onFitView={handleFitView}
      onReset={handleReset}
    />
  );
}

export default function AchievementRoadmap({
  className,
  onNodeClick,
}: AchievementRoadmapProps) {
  const { siteConfig } = useDocusaurusContext();
  const progressApiUrl =
    (siteConfig.customFields?.progressApiUrl as string) ||
    "http://localhost:8001";

  const [roadmap, setRoadmap] = useState<RoadmapResponse | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] =
    useState<ReactFlowInstance | null>(null);

  const loadRoadmap = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRoadmap(progressApiUrl);
      setRoadmap(data);

      // Convert to ReactFlow format
      const flowNodes: Node[] = data.nodes.map((node) => ({
        id: node.id,
        type: "roadmapNode",
        position: { x: node.position_x, y: node.position_y },
        data: {
          ...node,
          onClick: onNodeClick,
        },
        draggable: false,
      }));

      const flowEdges: Edge[] = data.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: edge.animated,
        type: "smoothstep",
        style: {
          stroke: nodeUnlockedInFlow(data.nodes, edge.target)
            ? "hsl(var(--primary))"
            : "hsl(var(--border))",
          strokeWidth: 2,
        },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      console.error("Failed to load roadmap:", err);
      setError("Failed to load roadmap");
    } finally {
      setLoading(false);
    }
  }, [progressApiUrl, onNodeClick]);

  const handleSync = async () => {
    try {
      await syncRoadmap(progressApiUrl);
      await loadRoadmap();
    } catch (err) {
      console.error("Failed to sync roadmap:", err);
    }
  };

  useEffect(() => {
    loadRoadmap();
  }, [loadRoadmap]);

  // Auto-fit view when nodes load
  useEffect(() => {
    if (reactFlowInstance && nodes.length > 0) {
      setTimeout(() => {
        reactFlowInstance.fitView({ padding: 0.2, duration: 300 });
      }, 100);
    }
  }, [reactFlowInstance, nodes.length]);

  function nodeUnlockedInFlow(nodes: RoadmapResponse["nodes"], nodeId: string): boolean {
    const node = nodes.find((n) => n.id === nodeId);
    return node?.unlocked ?? false;
  }

  if (loading) {
    return (
      <div
        className={cn(
          "flex items-center justify-center min-h-[400px] rounded-lg border border-border bg-card",
          className
        )}
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Loading roadmap...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className={cn(
          "flex items-center justify-center min-h-[400px] rounded-lg border border-border bg-card",
          className
        )}
      >
        <div className="text-center">
          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("relative", className)}>
      <div ref={reactFlowWrapper} className="w-full h-[600px] rounded-lg border border-border bg-background">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onInit={setReactFlowInstance}
          fitView
          minZoom={0.3}
          maxZoom={1.5}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
          proOptions={{ hideAttribution: true }}
        >
          <Background
            color="hsl(var(--muted))"
            gap={16}
            className="bg-background"
          />
          <MiniMap
            nodeColor={(node) => {
              const data = node.data as RoadmapResponse["nodes"][0];
              if (data.locked) return "hsl(var(--muted))";
              if (data.unlocked) return "hsl(var(--primary))";
              return "hsl(var(--border))";
            }}
            className="!bg-background !border-border"
          />
          <Controls className="!border-border !bg-card" />
          <RoadmapControlsWrapper onNodeClick={onNodeClick} />
        </ReactFlow>
      </div>

      {/* Stats footer */}
      {roadmap && (
        <div className="mt-4 flex items-center justify-between p-3 rounded-lg border border-border bg-card/50">
          <div className="flex items-center gap-4 text-sm">
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                {roadmap.unlocked_count}
              </span>{" "}
              / {roadmap.total_count} unlocked
            </span>
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">
                {roadmap.user_xp.toLocaleString()}
              </span>{" "}
              total XP
            </span>
          </div>

          <button
            onClick={handleSync}
            className="text-xs text-primary hover:underline"
          >
            Sync Progress
          </button>
        </div>
      )}
    </div>
  );
}
