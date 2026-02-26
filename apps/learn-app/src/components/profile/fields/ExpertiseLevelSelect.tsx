import React from "react";

const EXPERTISE_LEVELS = [
  { value: "none", label: "None — No experience" },
  { value: "beginner", label: "Beginner — Just starting" },
  { value: "intermediate", label: "Intermediate — Can work independently" },
  { value: "advanced", label: "Advanced — Deep experience" },
  { value: "expert", label: "Expert — Can teach others" },
] as const;

interface ExpertiseLevelSelectProps {
  value: string;
  onChange: (value: string) => void;
  label: string;
  id?: string;
}

export function ExpertiseLevelSelect({ value, onChange, label, id }: ExpertiseLevelSelectProps) {
  const selectId = id || `expertise-${label.toLowerCase().replace(/\s+/g, '-')}`;
  return (
    <div className="space-y-1.5">
      <label htmlFor={selectId} className="text-sm font-medium">{label}</label>
      <select
        id={selectId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
      >
        {EXPERTISE_LEVELS.map((level) => (
          <option key={level.value} value={level.value}>{level.label}</option>
        ))}
      </select>
    </div>
  );
}
