import React from "react";
import type { DeliverySection } from "@/lib/learner-profile-types";

const OUTPUT_FORMAT_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "prose", label: "Prose" },
  { value: "structured-with-headers", label: "Structured with Headers" },
  { value: "mixed", label: "Mixed" },
];

const TARGET_LENGTH_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "short", label: "Short" },
  { value: "medium", label: "Medium" },
  { value: "long", label: "Long" },
  { value: "match-source", label: "Match Source" },
];

const CODE_VERBOSITY_OPTIONS = [
  { value: "", label: "Select..." },
  { value: "minimal", label: "Minimal" },
  { value: "annotated", label: "Annotated" },
  { value: "fully-explained", label: "Fully Explained" },
];

export function DeliveryEdit({
  data,
  onChange,
}: {
  data: unknown;
  onChange: (data: unknown) => void;
}) {
  const delivery = data as DeliverySection;

  const update = (field: keyof DeliverySection, value: unknown) => {
    onChange({ ...delivery, [field]: value });
  };

  return (
    <div className="space-y-4">
      <div className="space-y-1.5">
        <label htmlFor="output-format" className="text-sm font-medium">
          Output Format
        </label>
        <select
          id="output-format"
          value={delivery?.output_format || ""}
          onChange={(e) => update("output_format", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {OUTPUT_FORMAT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="target-length" className="text-sm font-medium">
          Target Length
        </label>
        <select
          id="target-length"
          value={delivery?.target_length || ""}
          onChange={(e) => update("target_length", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {TARGET_LENGTH_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="code-verbosity" className="text-sm font-medium">
          Code Verbosity
        </label>
        <select
          id="code-verbosity"
          value={delivery?.code_verbosity || ""}
          onChange={(e) => update("code_verbosity", e.target.value || null)}
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          {CODE_VERBOSITY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
