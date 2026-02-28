"""Pure-unit tests for apply_phm_data logic in the PHM client.

No HTTP mocking needed — we test the synchronous transformation function
directly with plain dicts.
"""


from learner_profile_api.services.phm_client import apply_phm_data

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _empty_sections():
    """Return blank section dicts matching what a fresh profile has."""
    return (
        {  # expertise
            "domain": [],
            "programming": {"level": "beginner"},
            "ai_fluency": {"level": "beginner"},
            "business": {"level": "beginner"},
            "subject_specific": {
                "topics_already_mastered": [],
                "topics_partially_known": [],
                "known_misconceptions": [],
            },
        },
        {},  # professional_context
        {},  # goals
        {},  # communication
        {},  # field_sources
    )


# ---------------------------------------------------------------------------
# Expertise levels
# ---------------------------------------------------------------------------


class TestPhmExpertiseLevels:
    def test_phm_updates_expertise_levels(self):
        """PHM data with expertise levels updates the profile."""
        expertise, prof, goals, comm, sources = _empty_sections()

        phm_data = {
            "expertise_level": {
                "programming_experience": "advanced",
                "ai_fluency_familiarity": "intermediate",
            },
        }

        updated_exp, _, _, _, updated_src = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        assert updated_exp["programming"]["level"] == "advanced"
        assert updated_exp["ai_fluency"]["level"] == "intermediate"
        assert updated_src["expertise.programming.level"] == "phm"
        assert updated_src["expertise.ai_fluency.level"] == "phm"

    def test_phm_only_upgrades_expertise_in_v1(self, monkeypatch):
        """PHM tries to lower level -> no change (phm_allow_downrank=false)."""
        from learner_profile_api.services import phm_client

        monkeypatch.setattr(phm_client.settings, "phm_allow_downrank", False)

        expertise, prof, goals, comm, sources = _empty_sections()
        expertise["programming"]["level"] = "expert"

        phm_data = {
            "expertise_level": {"programming_experience": "beginner"},
        }

        updated_exp, _, _, _, _ = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        # Should stay at "expert" — PHM cannot downrank
        assert updated_exp["programming"]["level"] == "expert"


# ---------------------------------------------------------------------------
# Provenance / override rules
# ---------------------------------------------------------------------------


class TestPhmProvenance:
    def test_phm_respects_user_provenance(self):
        """field_sources has 'user' -> PHM does NOT overwrite."""
        expertise, prof, goals, comm, _ = _empty_sections()
        sources = {"expertise.programming.level": "user"}
        expertise["programming"]["level"] = "expert"

        phm_data = {
            "expertise_level": {"programming_experience": "beginner"},
        }

        updated_exp, _, _, _, updated_src = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        assert updated_exp["programming"]["level"] == "expert"
        assert updated_src["expertise.programming.level"] == "user"

    def test_phm_can_override_default(self):
        """field_sources has 'default' (or missing) -> PHM overrides."""
        expertise, prof, goals, comm, sources = _empty_sections()
        sources["expertise.programming.level"] = "default"

        phm_data = {
            "expertise_level": {"programming_experience": "intermediate"},
        }

        updated_exp, _, _, _, updated_src = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        assert updated_exp["programming"]["level"] == "intermediate"
        assert updated_src["expertise.programming.level"] == "phm"

    def test_phm_can_override_inferred(self):
        """field_sources has 'inferred' -> PHM overrides (phm > inferred)."""
        expertise, prof, goals, comm, sources = _empty_sections()
        sources["expertise.programming.level"] = "inferred"

        phm_data = {
            "expertise_level": {"programming_experience": "advanced"},
        }

        updated_exp, _, _, _, updated_src = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        assert updated_exp["programming"]["level"] == "advanced"
        assert updated_src["expertise.programming.level"] == "phm"


# ---------------------------------------------------------------------------
# Knowledge map transforms
# ---------------------------------------------------------------------------


class TestPhmKnowledgeMap:
    def test_phm_misconception_transform(self):
        """PHM string misconception -> {topic, misconception} object."""
        expertise, prof, goals, comm, sources = _empty_sections()

        phm_data = {
            "knowledge_map": {
                "known_misconceptions": ["neural networks are just if-else"],
            },
        }

        updated_exp, _, _, _, _ = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        misconceptions = updated_exp["subject_specific"]["known_misconceptions"]
        assert len(misconceptions) == 1
        assert misconceptions[0]["topic"] == "neural networks are just if-else"
        assert "misconception" in misconceptions[0]

    def test_phm_mastered_topics_additive(self):
        """Existing + new mastered topics -> merged (no duplicates)."""
        expertise, prof, goals, comm, sources = _empty_sections()
        expertise["subject_specific"]["topics_already_mastered"] = [
            {"topic": "Python basics", "treatment": "reference"},
        ]

        phm_data = {
            "knowledge_map": {
                "mastered": ["FastAPI", "Python basics"],  # Python basics already exists
            },
        }

        updated_exp, _, _, _, _ = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        mastered = updated_exp["subject_specific"]["topics_already_mastered"]
        topics = [t["topic"] for t in mastered]
        assert "Python basics" in topics
        assert "FastAPI" in topics
        # No duplicates
        assert len([t for t in topics if t.lower() == "python basics"]) == 1

    def test_phm_skip_overrides_reference(self):
        """Existing 'reference' topic + PHM 'skip' -> upgraded to 'skip'."""
        expertise, prof, goals, comm, sources = _empty_sections()
        expertise["subject_specific"]["topics_already_mastered"] = [
            {"topic": "Variables", "treatment": "reference"},
        ]

        phm_data = {
            "knowledge_map": {
                "topics_to_skip": ["Variables"],
            },
        }

        updated_exp, _, _, _, _ = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        mastered = updated_exp["subject_specific"]["topics_already_mastered"]
        variables_entry = next(t for t in mastered if t["topic"] == "Variables")
        assert variables_entry["treatment"] == "skip"

    def test_phm_misconceptions_capped_at_5(self):
        """6 misconceptions submitted -> only 5 stored."""
        expertise, prof, goals, comm, sources = _empty_sections()

        phm_data = {
            "knowledge_map": {
                "known_misconceptions": [
                    "misconception-1",
                    "misconception-2",
                    "misconception-3",
                    "misconception-4",
                    "misconception-5",
                    "misconception-6",
                ],
            },
        }

        updated_exp, _, _, _, _ = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        misconceptions = updated_exp["subject_specific"]["known_misconceptions"]
        assert len(misconceptions) == 5

    def test_phm_domain_auto_create(self):
        """Empty domain list + PHM domain expertise -> creates primary entry."""
        expertise, prof, goals, comm, sources = _empty_sections()
        assert expertise["domain"] == []

        phm_data = {
            "expertise_level": {"domain_expertise": "advanced"},
        }

        updated_exp, _, _, _, updated_src = apply_phm_data(
            phm_data, expertise, prof, goals, comm, sources,
        )

        domains = updated_exp["domain"]
        assert len(domains) == 1
        assert domains[0]["level"] == "advanced"
        assert domains[0]["is_primary"] is True
        assert updated_src["expertise.domain"] == "phm"
