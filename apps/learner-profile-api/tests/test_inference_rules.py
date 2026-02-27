"""Tests for the inference engine that derives communication/delivery prefs from expertise.

Pure unit tests — no DB, no client, no fixtures needed beyond schema constructors.
"""


from learner_profile_api.schemas.profile import (
    AiFluencyExpertise,
    BusinessExpertise,
    DomainExpertise,
    ExpertiseSection,
    ProgrammingExpertise,
)
from learner_profile_api.services.inference import run_inference, should_run_inference


def _make_expertise(
    *,
    programming: str = "beginner",
    ai_fluency: str = "beginner",
    business: str = "beginner",
    domain_level: str | None = None,
    domain_primary: bool = True,
) -> ExpertiseSection:
    """Helper to build an ExpertiseSection with the given levels."""
    domain = []
    if domain_level is not None:
        domain = [
            DomainExpertise(
                level=domain_level,
                domain_name="Test Domain",
                is_primary=domain_primary,
            )
        ]
    return ExpertiseSection(
        programming=ProgrammingExpertise(level=programming),
        ai_fluency=AiFluencyExpertise(level=ai_fluency),
        business=BusinessExpertise(level=business),
        domain=domain,
    )


# ---------------------------------------------------------------------------
# should_run_inference
# ---------------------------------------------------------------------------


class TestShouldRunInference:
    def test_inference_not_run_without_real_data(self):
        """All sources default -> inference should NOT run."""
        field_sources = {
            "expertise.programming.level": "default",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }
        assert should_run_inference(field_sources) is False

    def test_inference_not_run_with_empty_sources(self):
        """Empty dict (no keys at all) -> inference should NOT run."""
        assert should_run_inference({}) is False

    def test_inference_runs_with_user_source(self):
        """At least one expertise field sourced from 'user' -> should run."""
        field_sources = {
            "expertise.programming.level": "user",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }
        assert should_run_inference(field_sources) is True

    def test_inference_runs_with_phm_source(self):
        """At least one expertise field sourced from 'phm' -> should run."""
        field_sources = {
            "expertise.programming.level": "default",
            "expertise.ai_fluency.level": "phm",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }
        assert should_run_inference(field_sources) is True

    def test_inference_runs_with_domain_user_source(self):
        """Domain field sourced from 'user' -> should run."""
        field_sources = {
            "expertise.programming.level": "default",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "user",
        }
        assert should_run_inference(field_sources) is True

    def test_inferred_source_does_not_trigger(self):
        """'inferred' source on expertise fields should NOT trigger inference."""
        field_sources = {
            "expertise.programming.level": "inferred",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }
        assert should_run_inference(field_sources) is False


# ---------------------------------------------------------------------------
# run_inference — level-based mapping
# ---------------------------------------------------------------------------


class TestInferenceLevelMapping:
    """Test that each max-expertise level produces the correct inferred values."""

    def _field_sources_with_user_programming(self) -> dict[str, str]:
        """Field sources that trigger inference via programming.level = user."""
        return {
            "expertise.programming.level": "user",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }

    def test_none_inference_no_code_samples(self):
        """Max level 'none' -> include_code_samples = false, no code_verbosity."""
        expertise = _make_expertise(
            programming="none", ai_fluency="none", business="none",
        )
        field_sources = {
            "expertise.programming.level": "user",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "default",
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "plain"
        assert changed_values["communication.tone"] == "conversational"
        assert changed_values["communication.verbosity"] == "detailed"
        assert changed_values["delivery.include_code_samples"] is False
        # code_verbosity skipped when programming == none
        assert "delivery.code_verbosity" not in changed_values

    def test_beginner_inference(self):
        """Max level 'beginner' -> plain, conversational, detailed, code samples on."""
        expertise = _make_expertise(
            programming="beginner", ai_fluency="none", business="none",
        )
        field_sources = self._field_sources_with_user_programming()
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "plain"
        assert changed_values["communication.tone"] == "conversational"
        assert changed_values["communication.verbosity"] == "detailed"
        assert changed_values["delivery.include_code_samples"] is True
        assert changed_values["delivery.code_verbosity"] == "fully-explained"

    def test_intermediate_inference(self):
        """Max level 'intermediate' -> professional, professional, moderate."""
        expertise = _make_expertise(
            programming="intermediate", ai_fluency="none", business="none",
        )
        field_sources = self._field_sources_with_user_programming()
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "professional"
        assert changed_values["communication.tone"] == "professional"
        assert changed_values["communication.verbosity"] == "moderate"
        assert changed_values["delivery.include_code_samples"] is True

    def test_advanced_inference(self):
        """Max level 'advanced' -> technical, peer-to-peer, concise."""
        expertise = _make_expertise(
            programming="advanced", ai_fluency="none", business="none",
        )
        field_sources = self._field_sources_with_user_programming()
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "technical"
        assert changed_values["communication.tone"] == "peer-to-peer"
        assert changed_values["communication.verbosity"] == "concise"
        assert changed_values["delivery.include_code_samples"] is True

    def test_expert_inference(self):
        """Max level 'expert' -> expert, peer-to-peer, concise."""
        expertise = _make_expertise(
            programming="expert", ai_fluency="none", business="none",
        )
        field_sources = self._field_sources_with_user_programming()
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "expert"
        assert changed_values["communication.tone"] == "peer-to-peer"
        assert changed_values["communication.verbosity"] == "concise"
        assert changed_values["delivery.include_code_samples"] is True


# ---------------------------------------------------------------------------
# run_inference — special cases
# ---------------------------------------------------------------------------


class TestInferenceSpecialCases:
    def test_programming_none_overrides_code_samples(self):
        """programming.level = none forces include_code_samples = false
        even when domain expertise pushes max level higher."""
        expertise = _make_expertise(
            programming="none",
            ai_fluency="none",
            business="none",
            domain_level="advanced",
        )
        field_sources = {
            "expertise.programming.level": "default",
            "expertise.ai_fluency.level": "default",
            "expertise.business.level": "default",
            "expertise.domain": "user",
        }
        changed_values, _ = run_inference(expertise, field_sources)

        # Max level is 'advanced' (from domain), but programming=none caps
        # language_complexity at 'professional' per spec special case
        assert changed_values["communication.language_complexity"] == "professional"
        assert changed_values["communication.tone"] == "peer-to-peer"
        assert changed_values["communication.verbosity"] == "concise"

        # But programming == none -> no code samples, no code_verbosity
        assert changed_values["delivery.include_code_samples"] is False
        assert "delivery.code_verbosity" not in changed_values

    def test_code_verbosity_by_programming_level_beginner(self):
        """programming = beginner -> code_verbosity = fully-explained."""
        expertise = _make_expertise(programming="beginner")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)
        assert changed_values["delivery.code_verbosity"] == "fully-explained"

    def test_code_verbosity_by_programming_level_intermediate(self):
        """programming = intermediate -> code_verbosity = annotated."""
        expertise = _make_expertise(programming="intermediate")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)
        assert changed_values["delivery.code_verbosity"] == "annotated"

    def test_code_verbosity_by_programming_level_advanced(self):
        """programming = advanced -> code_verbosity = minimal."""
        expertise = _make_expertise(programming="advanced")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)
        assert changed_values["delivery.code_verbosity"] == "minimal"

    def test_code_verbosity_by_programming_level_expert(self):
        """programming = expert -> code_verbosity = minimal."""
        expertise = _make_expertise(programming="expert")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)
        assert changed_values["delivery.code_verbosity"] == "minimal"

    def test_max_level_uses_highest_across_all_areas(self):
        """Max level should reflect the highest level across all expertise areas."""
        expertise = _make_expertise(
            programming="beginner",
            ai_fluency="intermediate",
            business="none",
            domain_level="expert",
        )
        field_sources = {"expertise.domain": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        # Max level is 'expert' from domain, but programming=beginner caps
        # language_complexity at 'professional' per spec special case
        assert changed_values["communication.language_complexity"] == "professional"
        assert changed_values["communication.tone"] == "peer-to-peer"
        assert changed_values["communication.verbosity"] == "concise"


# ---------------------------------------------------------------------------
# run_inference — field source protection (user/phm not overwritten)
# ---------------------------------------------------------------------------


class TestInferenceSourceProtection:
    def test_user_set_not_overwritten(self):
        """A field with source='user' should NOT be overwritten by inference."""
        expertise = _make_expertise(programming="advanced")
        field_sources = {
            "expertise.programming.level": "user",
            "communication.language_complexity": "user",  # user already set this
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        # language_complexity should NOT appear in changed values
        assert "communication.language_complexity" not in changed_values
        assert "communication.language_complexity" not in changed_sources

        # Other fields that were default should still be inferred
        assert "communication.tone" in changed_values
        assert "communication.verbosity" in changed_values

    def test_phm_set_not_overwritten(self):
        """A field with source='phm' should NOT be overwritten by inference."""
        expertise = _make_expertise(programming="intermediate")
        field_sources = {
            "expertise.programming.level": "user",
            "communication.tone": "phm",  # phm already set this
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        # tone should NOT appear in changed values
        assert "communication.tone" not in changed_values
        assert "communication.tone" not in changed_sources

        # Other default fields should still be inferred
        assert "communication.language_complexity" in changed_values

    def test_inferred_can_override_previous_inferred(self):
        """A field with source='inferred' CAN be updated by new inference."""
        expertise = _make_expertise(programming="expert")
        field_sources = {
            "expertise.programming.level": "user",
            "communication.language_complexity": "inferred",  # previously inferred
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        # Should be updated since inferred >= inferred
        assert changed_values["communication.language_complexity"] == "expert"
        assert changed_sources["communication.language_complexity"] == "inferred"

    def test_inferred_can_override_default(self):
        """A field with source='default' CAN be overridden by inference."""
        expertise = _make_expertise(programming="beginner")
        field_sources = {
            "expertise.programming.level": "user",
            "communication.verbosity": "default",
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        assert changed_values["communication.verbosity"] == "detailed"
        assert changed_sources["communication.verbosity"] == "inferred"


# ---------------------------------------------------------------------------
# run_inference — changed_sources output
# ---------------------------------------------------------------------------


class TestInferenceChangedSources:
    def test_inferred_field_sources_updated(self):
        """After inference, changed_sources should have 'inferred' for all affected fields."""
        expertise = _make_expertise(programming="intermediate")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, changed_sources = run_inference(expertise, field_sources)

        # Every changed field should have source = "inferred"
        for field_path in changed_values:
            assert changed_sources[field_path] == "inferred", (
                f"Expected 'inferred' source for {field_path}, "
                f"got '{changed_sources.get(field_path)}'"
            )

    def test_changed_values_and_sources_have_same_keys(self):
        """changed_values and changed_sources must have identical key sets."""
        expertise = _make_expertise(programming="advanced", ai_fluency="beginner")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, changed_sources = run_inference(expertise, field_sources)

        assert set(changed_values.keys()) == set(changed_sources.keys())

    def test_no_changes_when_inference_not_triggered(self):
        """When should_run_inference is False, run_inference returns empty dicts."""
        expertise = _make_expertise(programming="advanced")
        field_sources = {
            "expertise.programming.level": "default",
            "expertise.ai_fluency.level": "default",
        }
        changed_values, changed_sources = run_inference(expertise, field_sources)

        assert changed_values == {}
        assert changed_sources == {}

    def test_does_not_mutate_input_field_sources(self):
        """run_inference must NOT modify the input field_sources dict."""
        expertise = _make_expertise(programming="expert")
        field_sources = {
            "expertise.programming.level": "user",
            "communication.language_complexity": "default",
        }
        original_sources = field_sources.copy()
        run_inference(expertise, field_sources)

        assert field_sources == original_sources


# ---------------------------------------------------------------------------
# run_inference — spec special cases for language_complexity capping
# ---------------------------------------------------------------------------


class TestInferenceLanguageComplexityCapping:
    """Spec: if programming.level is none/beginner but max expertise is
    advanced/expert, language_complexity caps at 'professional'."""

    def test_programming_beginner_max_advanced_caps_professional(self):
        """programming=beginner, domain=advanced -> professional (not technical)."""
        expertise = _make_expertise(
            programming="beginner",
            ai_fluency="beginner",
            business="beginner",
            domain_level="advanced",
        )
        field_sources = {"expertise.domain": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "professional"

    def test_programming_none_max_expert_caps_professional(self):
        """programming=none, business=expert -> professional (not expert)."""
        expertise = _make_expertise(
            programming="none",
            ai_fluency="none",
            business="expert",
        )
        field_sources = {"expertise.business.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "professional"

    def test_programming_intermediate_no_capping(self):
        """programming=intermediate, max=advanced -> normal mapping (technical)."""
        expertise = _make_expertise(
            programming="intermediate",
            ai_fluency="advanced",
            business="none",
        )
        field_sources = {"expertise.ai_fluency.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        # No capping — programming is intermediate (not none/beginner)
        assert changed_values["communication.language_complexity"] == "technical"

    def test_business_advanced_programming_none_caps(self):
        """Spec: 'If business.level = advanced but programming.level = none:
        language_complexity = professional'."""
        expertise = _make_expertise(
            programming="none",
            ai_fluency="none",
            business="advanced",
        )
        field_sources = {"expertise.business.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "professional"

    def test_programming_advanced_no_capping(self):
        """programming=advanced -> no capping applies, normal technical."""
        expertise = _make_expertise(programming="advanced")
        field_sources = {"expertise.programming.level": "user"}
        changed_values, _ = run_inference(expertise, field_sources)

        assert changed_values["communication.language_complexity"] == "technical"
