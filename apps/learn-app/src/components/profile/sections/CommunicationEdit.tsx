import React from "react";
import type { CommunicationSection } from "@/lib/learner-profile-types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
        <Select
          value={comm?.language_complexity || "none"}
          onValueChange={(val) => update("language_complexity", val === "none" ? null : val)}
        >
          <SelectTrigger id="language-complexity" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {LANGUAGE_COMPLEXITY_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="preferred-structure" className="text-sm font-medium">
          Preferred Structure
        </label>
        <Select
          value={comm?.preferred_structure || "none"}
          onValueChange={(val) => update("preferred_structure", val === "none" ? null : val)}
        >
          <SelectTrigger id="preferred-structure" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {STRUCTURE_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="verbosity" className="text-sm font-medium">
          Verbosity
        </label>
        <Select
          value={comm?.verbosity || "none"}
          onValueChange={(val) => update("verbosity", val === "none" ? null : val)}
        >
          <SelectTrigger id="verbosity" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {VERBOSITY_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="tone" className="text-sm font-medium">
          Tone
        </label>
        <Select
          value={comm?.tone || "none"}
          onValueChange={(val) => update("tone", val === "none" ? null : val)}
        >
          <SelectTrigger id="tone" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {TONE_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
