import React from "react";
import type {
  GoalsSection,
  ExpertiseSection,
  ProfessionalContextSection,
  AccessibilitySection,
} from "@/lib/learner-profile-types";

interface ReviewStepProps {
  goals: GoalsSection;
  expertise: ExpertiseSection;
  professional: ProfessionalContextSection;
  accessibility: AccessibilitySection;
}

function SectionSummary({
  title,
  items,
}: {
  title: string;
  items: { label: string; value: string | null }[];
}) {
  const filledItems = items.filter((item) => item.value);
  return (
    <div className="rounded-md border border-input p-4 space-y-2">
      <h3 className="text-sm font-semibold">{title}</h3>
      {filledItems.length === 0 ? (
        <p className="text-sm text-muted-foreground italic">Skipped</p>
      ) : (
        <dl className="space-y-1">
          {filledItems.map((item) => (
            <div key={item.label} className="flex gap-2 text-sm">
              <dt className="font-medium text-muted-foreground min-w-[120px]">
                {item.label}:
              </dt>
              <dd>{item.value}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  );
}

export function ReviewStep({
  goals,
  expertise,
  professional,
  accessibility,
}: ReviewStepProps) {
  const totalFields = 8;
  let filledFields = 0;
  if (goals.primary_learning_goal) filledFields++;
  if (goals.urgency) filledFields++;
  if (expertise.programming.level !== "none") filledFields++;
  if (expertise.ai_ml.level !== "none") filledFields++;
  if (expertise.business.level !== "none") filledFields++;
  if (professional.current_role) filledFields++;
  if (professional.industry) filledFields++;
  if (
    accessibility.screen_reader ||
    accessibility.dyslexia_friendly ||
    accessibility.color_blind_safe ||
    accessibility.cognitive_load_preference !== "standard"
  )
    filledFields++;

  const completenessPercent = Math.round((filledFields / totalFields) * 100);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold">Review Your Profile</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Here is a summary of what you have entered. You can always update
          these later in your profile settings.
        </p>
      </div>

      <div className="rounded-md border border-input p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Profile Completeness</span>
          <span className="text-sm font-semibold" data-testid="completeness-percent">
            {completenessPercent}%
          </span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full transition-all"
            style={{ width: `${completenessPercent}%` }}
            role="progressbar"
            aria-valuenow={completenessPercent}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        </div>
      </div>

      <SectionSummary
        title="Goals & Motivation"
        items={[
          { label: "Goal", value: goals.primary_learning_goal },
          { label: "Urgency", value: goals.urgency },
        ]}
      />
      <SectionSummary
        title="Expertise & Skills"
        items={[
          { label: "Programming", value: expertise.programming.level },
          { label: "AI/ML", value: expertise.ai_ml.level },
          { label: "Business", value: expertise.business.level },
          {
            label: "Domain",
            value: expertise.domain[0]?.domain_name || null,
          },
        ]}
      />
      <SectionSummary
        title="Professional Context"
        items={[
          { label: "Role", value: professional.current_role },
          { label: "Industry", value: professional.industry },
          { label: "Org Type", value: professional.organization_type },
        ]}
      />
      <SectionSummary
        title="Accessibility"
        items={[
          {
            label: "Screen Reader",
            value: accessibility.screen_reader ? "Enabled" : null,
          },
          {
            label: "Dyslexia-Friendly",
            value: accessibility.dyslexia_friendly ? "Enabled" : null,
          },
          {
            label: "Color Blind Safe",
            value: accessibility.color_blind_safe ? "Enabled" : null,
          },
          {
            label: "Cognitive Load",
            value:
              accessibility.cognitive_load_preference !== "standard"
                ? accessibility.cognitive_load_preference
                : null,
          },
          { label: "Notes", value: accessibility.notes },
        ]}
      />
    </div>
  );
}
