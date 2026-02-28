# Learner Profile System — Progress Log

## 2026-02-28

- Created canonical `profile-field-definitions.ts` — single source of truth for all UI field options (dropdowns, radios, toggles, chip-selects).
- Refactored 9 components to import from canonical file, eliminating option drift between onboarding and edit pages.
- Fixed value drift: `academic`→`education`, `nonprofit`→`non_profit`, added missing `small_business` org type.
- Created GitHub #787 (backend `field_definitions.py` + `?enrich=true` endpoint) and #788 (CI sync check).
- Updated spec: added decisions D-36, D-37; added §9.9 (Field Definitions Architecture); updated §9.8 priority table.
- Removed root `specs/learner-profile/` (redirect stubs only — anchored spec is canonical).
- Verification: `npx tsc --noEmit` — zero new type errors.

## 2026-02-27

- Promoted Learner Profile spec to an anchored spec package under `specs/anchored/learner-profile/`.
- Updated spec to v1.3 and aligned it with the current implementation (AI fluency naming + onboarding polish + subject-specific enrichment).
- Implemented premium onboarding/profile UX fixes (redirect-once, baseUrl-safe navigation, exit confirmation, scroll reset, subject-specific enrichment collection).
- Verification:
  - learn-app: `pnpm vitest run`
  - learner-profile-api: `uv run pytest tests/`
