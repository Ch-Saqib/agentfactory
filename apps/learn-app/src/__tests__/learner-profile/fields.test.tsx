import { describe, it, expect, vi } from "vitest";
import React from "react";
import { render, screen, within, fireEvent } from "@testing-library/react";
import { ExpertiseLevelSelect } from "@/components/profile/fields/ExpertiseLevelSelect";
import { UrgencyRadio } from "@/components/profile/fields/UrgencyRadio";
import { AccessibilityToggles } from "@/components/profile/fields/AccessibilityToggles";
import type { AccessibilitySection } from "@/lib/learner-profile-types";

// ---------- ExpertiseLevelSelect ----------
describe("ExpertiseLevelSelect", () => {
  it("renders with label and 5 options", () => {
    render(
      <ExpertiseLevelSelect value="beginner" onChange={vi.fn()} label="Programming" />
    );
    expect(screen.getByLabelText("Programming")).toBeInTheDocument();

    const select = screen.getByLabelText("Programming") as HTMLSelectElement;
    const options = within(select).getAllByRole("option");
    expect(options).toHaveLength(5);
    expect(options.map((o) => o.textContent)).toEqual([
      "None — No experience",
      "Beginner — Just starting",
      "Intermediate — Can work independently",
      "Advanced — Deep experience",
      "Expert — Can teach others",
    ]);
  });

  it("displays the current value", () => {
    render(
      <ExpertiseLevelSelect value="advanced" onChange={vi.fn()} label="AI/ML" />
    );
    const select = screen.getByLabelText("AI/ML") as HTMLSelectElement;
    expect(select.value).toBe("advanced");
  });

  it("calls onChange when a different option is selected", () => {
    const onChange = vi.fn();
    render(
      <ExpertiseLevelSelect value="beginner" onChange={onChange} label="Programming" />
    );

    fireEvent.change(screen.getByLabelText("Programming"), {
      target: { value: "expert" },
    });
    expect(onChange).toHaveBeenCalledWith("expert");
  });

  it("has accessible label linked to select via id/htmlFor", () => {
    render(
      <ExpertiseLevelSelect value="none" onChange={vi.fn()} label="Domain Knowledge" />
    );
    const label = screen.getByText("Domain Knowledge");
    const select = screen.getByLabelText("Domain Knowledge");
    expect(label.tagName).toBe("LABEL");
    expect(label).toHaveAttribute("for", select.id);
  });

  it("uses custom id when provided", () => {
    render(
      <ExpertiseLevelSelect
        value="none"
        onChange={vi.fn()}
        label="Custom"
        id="my-custom-id"
      />
    );
    const select = screen.getByLabelText("Custom");
    expect(select.id).toBe("my-custom-id");
  });
});

// ---------- UrgencyRadio ----------
describe("UrgencyRadio", () => {
  it("renders 3 radio options", () => {
    render(<UrgencyRadio value={null} onChange={vi.fn()} />);
    const radios = screen.getAllByRole("radio");
    expect(radios).toHaveLength(3);
  });

  it("calls onChange when a radio is clicked", () => {
    const onChange = vi.fn();
    render(<UrgencyRadio value={null} onChange={onChange} />);

    fireEvent.click(screen.getByDisplayValue("high"));
    expect(onChange).toHaveBeenCalledWith("high");
  });

  it("checks the radio matching the current value", () => {
    render(<UrgencyRadio value="medium" onChange={vi.fn()} />);
    const mediumRadio = screen.getByDisplayValue("medium") as HTMLInputElement;
    expect(mediumRadio.checked).toBe(true);

    const lowRadio = screen.getByDisplayValue("low") as HTMLInputElement;
    expect(lowRadio.checked).toBe(false);
  });

  it("has proper fieldset/legend structure", () => {
    const { container } = render(<UrgencyRadio value={null} onChange={vi.fn()} />);
    const fieldset = container.querySelector("fieldset");
    expect(fieldset).toBeInTheDocument();
    const legend = container.querySelector("legend");
    expect(legend).toBeInTheDocument();
    expect(legend!.textContent).toBe("Learning Urgency");
  });

  it("shows descriptions for each option", () => {
    render(<UrgencyRadio value={null} onChange={vi.fn()} />);
    expect(screen.getByText("Learning at my own pace")).toBeInTheDocument();
    expect(screen.getByText("Want to make steady progress")).toBeInTheDocument();
    expect(screen.getByText("Need to learn quickly")).toBeInTheDocument();
  });

  it("handles null value (nothing checked)", () => {
    render(<UrgencyRadio value={null} onChange={vi.fn()} />);
    const radios = screen.getAllByRole("radio") as HTMLInputElement[];
    expect(radios.every((r) => !r.checked)).toBe(true);
  });
});

// ---------- AccessibilityToggles ----------
describe("AccessibilityToggles", () => {
  const defaultValue: AccessibilitySection = {
    screen_reader: false,
    dyslexia_friendly: false,
    color_blind_safe: false,
    cognitive_load_preference: "standard",
    notes: null,
  };

  it("renders 3 toggle switches with labels", () => {
    render(<AccessibilityToggles value={defaultValue} onChange={vi.fn()} />);
    const switches = screen.getAllByRole("switch");
    expect(switches).toHaveLength(3);

    expect(screen.getByText("Screen Reader")).toBeInTheDocument();
    expect(screen.getByText("Dyslexia-Friendly")).toBeInTheDocument();
    expect(screen.getByText("Color Blind Safe")).toBeInTheDocument();
  });

  it("renders descriptions for each toggle", () => {
    render(<AccessibilityToggles value={defaultValue} onChange={vi.fn()} />);
    expect(screen.getByText("Optimize content for screen reader users")).toBeInTheDocument();
    expect(screen.getByText("Use dyslexia-friendly formatting")).toBeInTheDocument();
    expect(screen.getByText("Avoid relying on color alone for information")).toBeInTheDocument();
  });

  it("calls onChange with updated object when a toggle is clicked", () => {
    const onChange = vi.fn();
    render(<AccessibilityToggles value={defaultValue} onChange={onChange} />);

    const switches = screen.getAllByRole("switch");
    // Click the "Screen Reader" toggle (first switch)
    fireEvent.click(switches[0]);

    expect(onChange).toHaveBeenCalledWith({
      ...defaultValue,
      screen_reader: true,
    });
  });

  it("toggles off when already on", () => {
    const onChange = vi.fn();
    const enabledValue: AccessibilitySection = {
      ...defaultValue,
      dyslexia_friendly: true,
    };
    render(<AccessibilityToggles value={enabledValue} onChange={onChange} />);

    const switches = screen.getAllByRole("switch");
    // Click the "Dyslexia-Friendly" toggle (second switch)
    fireEvent.click(switches[1]);

    expect(onChange).toHaveBeenCalledWith({
      ...enabledValue,
      dyslexia_friendly: false,
    });
  });

  it("toggle buttons have role=switch and aria-checked", () => {
    const mixedValue: AccessibilitySection = {
      ...defaultValue,
      screen_reader: true,
      color_blind_safe: true,
    };
    render(<AccessibilityToggles value={mixedValue} onChange={vi.fn()} />);

    const switches = screen.getAllByRole("switch");
    expect(switches[0]).toHaveAttribute("aria-checked", "true");
    expect(switches[1]).toHaveAttribute("aria-checked", "false");
    expect(switches[2]).toHaveAttribute("aria-checked", "true");
  });

  it("has fieldset/legend structure", () => {
    const { container } = render(
      <AccessibilityToggles value={defaultValue} onChange={vi.fn()} />
    );
    const fieldset = container.querySelector("fieldset");
    expect(fieldset).toBeInTheDocument();
    const legend = container.querySelector("legend");
    expect(legend).toHaveTextContent("Accessibility Options");
  });

  it("preserves other fields in the AccessibilitySection when toggling", () => {
    const onChange = vi.fn();
    const valueWithNotes: AccessibilitySection = {
      ...defaultValue,
      cognitive_load_preference: "reduced",
      notes: "Some accessibility notes",
    };
    render(<AccessibilityToggles value={valueWithNotes} onChange={onChange} />);

    const switches = screen.getAllByRole("switch");
    fireEvent.click(switches[2]); // color_blind_safe

    expect(onChange).toHaveBeenCalledWith({
      ...valueWithNotes,
      color_blind_safe: true,
    });
  });
});
