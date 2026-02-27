import React from "react";
import type { DeliverySection } from "@/lib/learner-profile-types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
        <Select
          value={delivery?.output_format || "none"}
          onValueChange={(val) => update("output_format", val === "none" ? null : val)}
        >
          <SelectTrigger id="output-format" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {OUTPUT_FORMAT_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="target-length" className="text-sm font-medium">
          Target Length
        </label>
        <Select
          value={delivery?.target_length || "none"}
          onValueChange={(val) => update("target_length", val === "none" ? null : val)}
        >
          <SelectTrigger id="target-length" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {TARGET_LENGTH_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="space-y-1.5">
        <label htmlFor="code-verbosity" className="text-sm font-medium">
          Code Verbosity
        </label>
        <Select
          value={delivery?.code_verbosity || "none"}
          onValueChange={(val) => update("code_verbosity", val === "none" ? null : val)}
        >
          <SelectTrigger id="code-verbosity" className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none" className="italic text-muted-foreground">Select...</SelectItem>
            {CODE_VERBOSITY_OPTIONS.filter(opt => opt.value !== "").map((opt) => (
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
