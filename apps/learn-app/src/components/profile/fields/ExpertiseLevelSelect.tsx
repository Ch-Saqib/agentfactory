import React from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import type { ExpertiseLevel } from "@/lib/learner-profile-types";
import {
  EXPERTISE_LEVELS,
  DEFAULT_EXPERTISE_LEVELS,
} from "@/lib/profile-field-definitions";

interface ExpertiseLevelSelectProps {
  value: ExpertiseLevel | "";
  onChange: (value: ExpertiseLevel) => void;
  label: string;
  id?: string;
}

export function ExpertiseLevelSelect({
  value,
  onChange,
  label,
  id,
}: ExpertiseLevelSelectProps) {
  const selectId =
    id || `expertise-${label.toLowerCase().replace(/\s+/g, "-")}`;
  const levels = EXPERTISE_LEVELS[label] || DEFAULT_EXPERTISE_LEVELS;

  return (
    <div className="space-y-2">
      <Label
        htmlFor={selectId}
        className="text-xs font-semibold tracking-wide text-muted-foreground uppercase pl-1"
      >
        {label}
      </Label>
      <Select value={value} onValueChange={onChange as (value: string) => void}>
        <SelectTrigger
          id={selectId}
          className="h-14 text-lg text-left rounded-xl border-2 border-border/50 bg-background/50 px-4 transition-colors focus:ring-primary/20"
        >
          <SelectValue placeholder="Select level…" />
        </SelectTrigger>
        <SelectContent className="z-[120] rounded-xl border border-border/50 shadow-xl overflow-hidden">
          {levels.map((level) => (
            <SelectItem
              key={level.value}
              value={level.value}
              className="text-base py-3 cursor-pointer hover:bg-accent"
            >
              <span className="font-medium">{level.label}</span>
              <span className="text-muted-foreground ml-2">— {level.hint}</span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
