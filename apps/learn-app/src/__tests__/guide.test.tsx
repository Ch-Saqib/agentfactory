import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import GuidePage from "@/pages/guide";

describe("GuidePage", () => {
  it("renders without crashing", () => {
    render(<GuidePage />);
    expect(screen.getByText("Your Learning Toolkit")).toBeDefined();
  });

  it("has a flashcards section with correct id", () => {
    const { container } = render(<GuidePage />);
    const section = container.querySelector("#flashcards");
    expect(section).not.toBeNull();
  });
});
