import React from "react";
import type { CommunicationSection } from "@/lib/learner-profile-types";

const LANGUAGE_COMPLEXITY_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "plain", label: "Plain" },
  { value: "professional", label: "Professional" },
  { value: "technical", label: "Technical" },
  { value: "expert", label: "Expert" },
];

const STRUCTURE_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "examples-first", label: "Examples First" },
  { value: "theory-first", label: "Theory First" },
  { value: "story-narrative", label: "Story / Narrative" },
  { value: "reference-lookup", label: "Reference / Lookup" },
  { value: "problem-first", label: "Problem First" },
];

const VERBOSITY_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "concise", label: "Concise" },
  { value: "moderate", label: "Moderate" },
  { value: "detailed", label: "Detailed" },
];

const TONE_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "formal", label: "Formal" },
  { value: "professional", label: "Professional" },
  { value: "conversational", label: "Conversational" },
  { value: "peer-to-peer", label: "Peer to Peer" },
];

export function CommunicationEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const comm = data as CommunicationSection;

  const update = (field: keyof CommunicationSection, value: unknown) => {
    onChange({ ...comm, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label htmlFor="language-complexity" className="text-sm font-medium">
          Language Complexity
        </label>
        <select
          id="language-complexity"
          value={comm?.language_complexity || ""}
          onChange={(e) =>
            update("language_complexity", e.target.value || null)
          }
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {LANGUAGE_COMPLEXITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="preferred-structure" className="text-sm font-medium">
          Preferred Structure
        </label>
        <select
          id="preferred-structure"
          value={comm?.preferred_structure || ""}
          onChange={(e) =>
            update("preferred_structure", e.target.value || null)
          }
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {STRUCTURE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="verbosity" className="text-sm font-medium">
          Verbosity
        </label>
        <select
          id="verbosity"
          value={comm?.verbosity || ""}
          onChange={(e) => update("verbosity", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {VERBOSITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="tone" className="text-sm font-medium">
          Tone
        </label>
        <select
          id="tone"
          value={comm?.tone || ""}
          onChange={(e) => update("tone", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {TONE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
