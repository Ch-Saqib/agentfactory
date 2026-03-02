import React, { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Lock, Unlock, Check } from "lucide-react";
import type { RoadmapNodeResponse } from "@/lib/progress-types";
import { cn } from "@/lib/utils";

interface CustomNodeData extends RoadmapNodeResponse {
  onClick?: (nodeId: string) => void;
}

function RoadmapNodeComponent({ data, selected }: NodeProps<CustomNodeData>) {
  const { title, node_type, icon, unlocked, locked, description } = data;

  const handleClick = () => {
    if (data.onClick && unlocked) {
      data.onClick(data.id);
    }
  };

  const getNodeStyles = () => {
    if (locked) {
      return {
        bg: "bg-muted/50",
        border: "border-border",
        text: "text-muted-foreground",
        icon: "text-muted-foreground",
      };
    }
    if (unlocked) {
      return {
        bg: "bg-primary/10",
        border: "border-primary/50",
        text: "text-foreground",
        icon: "text-primary",
      };
    }
    return {
      bg: "bg-card",
      border: "border-border",
      text: "text-foreground",
      icon: "text-muted-foreground",
    };
  };

  const styles = getNodeStyles();

  return (
    <div
      onClick={handleClick}
      className={cn(
        "relative px-4 py-3 rounded-lg border-2 min-w-[140px] max-w-[180px]",
        "transition-all duration-200 cursor-pointer",
        styles.bg,
        styles.border,
        selected && "ring-2 ring-ring ring-offset-2",
        unlocked && "hover:shadow-lg",
        locked && "cursor-not-allowed opacity-60"
      )}
    >
      {/* Input handle (left) */}
      {node_type !== "part" && (
        <Handle
          type="target"
          position={Position.Left}
          className={cn(
            "!w-3 !h-3 !border-2",
            unlocked
              ? "!bg-primary !border-primary"
              : "!bg-muted !border-border"
          )}
        />
      )}

      {/* Output handle (right) */}
      {node_type === "part" && (
        <Handle
          type="source"
          position={Position.Right}
          className={cn(
            "!w-3 !h-3 !border-2",
            unlocked
              ? "!bg-primary !border-primary"
              : "!bg-muted !border-border"
          )}
        />
      )}

      {/* Icon and title */}
      <div className="flex items-center gap-2 mb-1">
        {icon && (
          <span className={cn("text-lg", styles.icon)}>{icon}</span>
        )}
        <div className="flex-1 min-w-0">
          <div
            className={cn(
              "text-sm font-semibold truncate",
              styles.text
            )}
          >
            {title}
          </div>
        </div>

        {/* Status indicator */}
        <div className="flex-shrink-0">
          {locked ? (
            <Lock className="h-3 w-3 text-muted-foreground" />
          ) : unlocked ? (
            <Check className="h-3 w-3 text-primary" />
          ) : (
            <Unlock className="h-3 w-3 text-muted-foreground" />
          )}
        </div>
      </div>

      {/* Description (if available) */}
      {description && !locked && (
        <div className="text-xs text-muted-foreground truncate">
          {description}
        </div>
      )}

      {/* Node type badge */}
      <div className="mt-2">
        <span
          className={cn(
            "text-[10px] uppercase tracking-wider font-medium",
            styles.text
          )}
        >
          {node_type}
        </span>
      </div>
    </div>
  );
}

export const RoadmapNode = memo(RoadmapNodeComponent);
