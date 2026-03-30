"""Tests for profile CRUD operations at the service layer."""

import pytest

from learner_profile_api.core.exceptions import (
    ConsentRequired,
    ProfileExists,
    ProfileNotFound,
)
from learner_profile_api.schemas.profile import ExpertiseSection, ProfileCreate, ProfileUpdate
from learner_profile_api.services.profile_service import (
    create_profile,
    gdpr_erase_profile,
    get_profile,
    soft_delete_profile,
    update_profile,
    update_section,
)


class TestCreateProfile:
    async def test_create_profile_with_consent(self, db_session):
        data = ProfileCreate(consent_given=True, name="Test User")
        profile, is_restored = await create_profile(db_session, "user-1", data)

        assert profile.learner_id == "user-1"
        assert profile.name == "Test User"
        assert profile.consent_given is True
        assert profile.consent_date is not None
        assert profile.profile_version == "1.1"
        assert is_restored is False

    async def test_create_profile_without_consent_raises(self, db_session):
        data = ProfileCreate(consent_given=False)
        with pytest.raises(ConsentRequired):
            await create_profile(db_session, "user-2", data)

    async def test_duplicate_profile_raises(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-3", data)

        with pytest.raises(ProfileExists):
            await create_profile(db_session, "user-3", data)

    async def test_profile_defaults_applied(self, db_session):
        data = ProfileCreate(consent_given=True)
        profile, _ = await create_profile(db_session, "user-4", data)

        # Verify default expertise
        assert profile.expertise.get("programming", {}).get("level") == "beginner"
        assert profile.expertise.get("ai_fluency", {}).get("level") == "beginner"
        assert profile.expertise.get("business", {}).get("level") == "beginner"
        assert profile.expertise.get("domain") == []

        # Verify default goals
        assert profile.goals.get("primary_learning_goal") is None
        assert profile.goals.get("urgency") is None

    async def test_learner_id_is_set_from_arg(self, db_session):
        data = ProfileCreate(consent_given=True)
        profile, _ = await create_profile(db_session, "auth0|abc123", data)

        assert profile.learner_id == "auth0|abc123"

    async def test_restore_after_soft_delete(self, db_session):
        data = ProfileCreate(consent_given=True, name="Restorable")
        profile, _ = await create_profile(db_session, "user-restore", data)

        await soft_delete_profile(db_session, "user-restore")

        # Restore
        restored, is_restored = await create_profile(
            db_session, "user-restore", ProfileCreate(consent_given=True)
        )
        assert is_restored is True
        assert restored.name == "Restorable"  # Data preserved
        assert restored.deleted_at is None


class TestGetProfile:
    async def test_get_existing_profile(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-get", data)

        profile = await get_profile(db_session, "user-get")
        assert profile.learner_id == "user-get"

    async def test_get_nonexistent_raises(self, db_session):
        with pytest.raises(ProfileNotFound):
            await get_profile(db_session, "nonexistent")

    async def test_get_soft_deleted_raises(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-deleted", data)
        await soft_delete_profile(db_session, "user-deleted")

        with pytest.raises(ProfileNotFound):
            await get_profile(db_session, "user-deleted")


class TestUpdateProfile:
    async def test_update_only_provided_fields(self, db_session):
        data = ProfileCreate(consent_given=True, name="Original")
        await create_profile(db_session, "user-update", data)

        update = ProfileUpdate(name="Updated")
        profile = await update_profile(db_session, "user-update", update)

        assert profile.name == "Updated"

    async def test_merge_section_preserves_untouched(self, db_session):
        """PATCH with partial expertise should not wipe other expertise fields."""
        create_data = ProfileCreate(
            consent_given=True,
            expertise=ExpertiseSection(
                programming={"level": "beginner"},
                ai_fluency={"level": "intermediate"},
            ),
        )
        await create_profile(db_session, "user-merge", create_data)

        # Update only programming level
        update = ProfileUpdate(
            expertise=ExpertiseSection(programming={"level": "advanced"})
        )
        profile = await update_profile(db_session, "user-merge", update)

        # programming should be updated
        assert profile.expertise["programming"]["level"] == "advanced"
        # ai_fluency should be preserved (not wiped to default)
        assert profile.expertise["ai_fluency"]["level"] == "intermediate"

    async def test_field_sources_marked_user(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-sources", data)

        update = ProfileUpdate(
            expertise=ExpertiseSection(programming={"level": "advanced"})
        )
        profile = await update_profile(db_session, "user-sources", update)

        assert profile.field_sources.get("expertise.programming.level") == "user"


class TestSectionUpdate:
    async def test_update_expertise_section(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-section", data)

        section_data = ExpertiseSection(programming={"level": "expert"})
        profile = await update_section(db_session, "user-section", "expertise", section_data)

        assert profile.expertise["programming"]["level"] == "expert"

    async def test_unknown_section_raises(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-unknown-sec", data)

        with pytest.raises(ProfileNotFound):
            await update_section(
                db_session, "user-unknown-sec", "invalid_section", ExpertiseSection()
            )


class TestSoftDelete:
    async def test_soft_delete_sets_deleted_at(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-soft", data)

        await soft_delete_profile(db_session, "user-soft")

        with pytest.raises(ProfileNotFound):
            await get_profile(db_session, "user-soft")

    async def test_soft_delete_nonexistent_raises(self, db_session):
        with pytest.raises(ProfileNotFound):
            await soft_delete_profile(db_session, "nonexistent-del")


class TestGDPRErase:
    async def test_gdpr_erase_deletes_row(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-gdpr", data)

        await gdpr_erase_profile(db_session, "user-gdpr")

        with pytest.raises(ProfileNotFound):
            await get_profile(db_session, "user-gdpr")

    async def test_gdpr_erase_anonymizes_audit(self, db_session):
        from sqlmodel import select

        from learner_profile_api.models.profile import ProfileAuditLog

        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-gdpr-audit", data)
        await gdpr_erase_profile(db_session, "user-gdpr-audit")

        # Audit logs should be anonymized
        stmt = select(ProfileAuditLog).where(
            ProfileAuditLog.action == "gdpr_erased"
        )
        result = await db_session.execute(stmt)
        logs = result.scalars().all()

        assert len(logs) > 0
        for log in logs:
            assert log.learner_id != "user-gdpr-audit"  # Anonymized
            assert log.action == "gdpr_erased"
            assert log.previous_values == {}
            assert log.changed_sections == []

    async def test_gdpr_erase_soft_deleted_profile(self, db_session):
        """GDPR erase must work on soft-deleted profiles (spec §5)."""
        data = ProfileCreate(consent_given=True)
        profile, _ = await create_profile(db_session, "user-gdpr-soft", data)
        await soft_delete_profile(db_session, "user-gdpr-soft")
        # Must NOT raise ProfileNotFound
        await gdpr_erase_profile(db_session, "user-gdpr-soft")
        # Verify truly gone
        with pytest.raises(ProfileNotFound):
            await get_profile(db_session, "user-gdpr-soft")

    async def test_gdpr_erase_nonexistent_raises(self, db_session):
        with pytest.raises(ProfileNotFound):
            await gdpr_erase_profile(db_session, "nonexistent-gdpr")


class TestCommunicationDeliveryDefaults:
    """Verify Appendix B defaults are applied at profile creation."""

    async def test_communication_defaults_applied(self, db_session):
        data = ProfileCreate(consent_given=True)
        profile, _ = await create_profile(db_session, "user-defaults-comm", data)

        assert profile.communication["language_complexity"] == "professional"
        assert profile.communication["preferred_structure"] == "examples-first"
        assert profile.communication["verbosity"] == "moderate"
        assert profile.communication["tone"] == "professional"
        assert profile.communication["wants_summaries"] is True
        assert profile.communication["wants_check_in_questions"] is True

    async def test_delivery_defaults_applied(self, db_session):
        data = ProfileCreate(consent_given=True)
        profile, _ = await create_profile(db_session, "user-defaults-deliv", data)

        # Default programming = beginner, so include_code_samples = True
        assert profile.delivery["output_format"] == "structured-with-headers"
        assert profile.delivery["target_length"] == "match-source"
        assert profile.delivery["include_code_samples"] is True
        assert profile.delivery["code_verbosity"] == "fully-explained"
        assert profile.delivery["include_visual_descriptions"] is False
        assert profile.delivery["language"] == "English"

    async def test_delivery_code_samples_false_when_programming_none(self, db_session):
        data = ProfileCreate(
            consent_given=True,
            expertise=ExpertiseSection(
                programming={"level": "none"},
            ),
        )
        profile, _ = await create_profile(db_session, "user-no-code", data)

        assert profile.delivery["include_code_samples"] is False
        assert profile.delivery["code_verbosity"] is None

    async def test_user_set_communication_not_overwritten_by_defaults(self, db_session):
        """If user explicitly sets a communication field, defaults don't override."""
        data = ProfileCreate(
            consent_given=True,
            communication={"tone": "formal"},
        )
        profile, _ = await create_profile(db_session, "user-custom-comm", data)

        # User-set tone preserved
        assert profile.communication["tone"] == "formal"
        # Other fields get defaults
        assert profile.communication["language_complexity"] == "professional"
        # field_sources should track user-set tone
        assert profile.field_sources.get("communication.tone") == "user"


class TestDomainAutoPrimary:
    """Verify first domain entry auto-marked primary if none has is_primary=true."""

    async def test_domain_auto_primary_on_create(self, db_session):
        data = ProfileCreate(
            consent_given=True,
            expertise=ExpertiseSection(
                domain=[
                    {"level": "intermediate", "domain_name": "Finance"},
                    {"level": "beginner", "domain_name": "Healthcare"},
                ],
            ),
        )
        profile, _ = await create_profile(db_session, "user-auto-primary", data)

        # First entry should be auto-marked primary
        assert profile.expertise["domain"][0]["is_primary"] is True

    async def test_explicit_primary_not_overridden(self, db_session):
        data = ProfileCreate(
            consent_given=True,
            expertise=ExpertiseSection(
                domain=[
                    {"level": "intermediate", "domain_name": "Finance", "is_primary": False},
                    {"level": "beginner", "domain_name": "Healthcare", "is_primary": True},
                ],
            ),
        )
        profile, _ = await create_profile(db_session, "user-explicit-primary", data)

        # Second entry should stay primary (explicit)
        assert profile.expertise["domain"][0]["is_primary"] is False
        assert profile.expertise["domain"][1]["is_primary"] is True

    async def test_domain_auto_primary_on_update(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-auto-update", data)

        update = ProfileUpdate(
            expertise=ExpertiseSection(
                domain=[{"level": "advanced", "domain_name": "AI"}],
            ),
        )
        profile = await update_profile(db_session, "user-auto-update", update)

        assert profile.expertise["domain"][0]["is_primary"] is True


class TestTopicDeduplication:
    """Verify case-normalized deduplication of mastered topics."""

    async def test_duplicate_topics_deduplicated_on_update(self, db_session):
        data = ProfileCreate(consent_given=True)
        await create_profile(db_session, "user-dedup", data)

        update = ProfileUpdate(
            expertise=ExpertiseSection(
                subject_specific={
                    "topics_already_mastered": [
                        {"topic": "Python", "treatment": "reference"},
                        {"topic": "python", "treatment": "reference"},
                        {"topic": "PYTHON", "treatment": "skip"},
                    ],
                },
            ),
        )
        profile = await update_profile(db_session, "user-dedup", update)

        mastered = profile.expertise["subject_specific"]["topics_already_mastered"]
        assert len(mastered) == 1
        # "skip" should win over "reference" when deduplicating
        assert mastered[0]["treatment"] == "skip"
