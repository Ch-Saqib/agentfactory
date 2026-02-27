"""Inference engine for deriving communication/delivery preferences from expertise.

Rules from spec Section 4 — Inference Rules table.
User-set values ALWAYS override inferences.
Inference only runs when at least one expertise field has user or phm source.
"""

import logging

from ..schemas.profile import ExpertiseSection

logger = logging.getLogger(__name__)

# Source priority (higher number = higher priority)
SOURCE_PRIORITY: dict[str, int] = {
    "default": 1,
    "inferred": 2,
    "phm": 3,
    "user": 4,
}

# Mapping from max expertise level to inferred fields
INFERENCE_TABLE: dict[str, dict[str, str | bool]] = {
    "none": {
        "language_complexity": "plain",
        "tone": "conversational",
        "verbosity": "detailed",
        "code_verbosity": "fully-explained",
        "include_code_samples": False,
    },
    "beginner": {
        "language_complexity": "plain",
        "tone": "conversational",
        "verbosity": "detailed",
        "code_verbosity": "fully-explained",
        "include_code_samples": True,
    },
    "intermediate": {
        "language_complexity": "professional",
        "tone": "professional",
        "verbosity": "moderate",
        "code_verbosity": "annotated",
        "include_code_samples": True,
    },
    "advanced": {
        "language_complexity": "technical",
        "tone": "peer-to-peer",
        "verbosity": "concise",
        "code_verbosity": "minimal",
        "include_code_samples": True,
    },
    "expert": {
        "language_complexity": "expert",
        "tone": "peer-to-peer",
        "verbosity": "concise",
        "code_verbosity": "minimal",
        "include_code_samples": True,
    },
}

EXPERTISE_LEVEL_ORDER = ["none", "beginner", "intermediate", "advanced", "expert"]


def _get_max_expertise_level(expertise: ExpertiseSection) -> str:
    """Get the maximum expertise level across all areas."""
    levels = [
        expertise.programming.level,
        expertise.ai_fluency.level,
        expertise.business.level,
    ]

    # Include primary domain level if domains exist
    for domain in expertise.domain:
        if domain.is_primary:
            levels.append(domain.level)
            break
    else:
        # No domain entries — treat as "none"
        levels.append("none")

    # Find maximum by index in order
    max_idx = 0
    for level in levels:
        idx = EXPERTISE_LEVEL_ORDER.index(level) if level in EXPERTISE_LEVEL_ORDER else 0
        max_idx = max(max_idx, idx)

    return EXPERTISE_LEVEL_ORDER[max_idx]


def _can_override(current_source: str, new_source: str) -> bool:
    """Check if new_source can override current_source."""
    return SOURCE_PRIORITY.get(new_source, 0) >= SOURCE_PRIORITY.get(current_source, 0)


def should_run_inference(field_sources: dict[str, str]) -> bool:
    """Check if inference should run.

    Requires at least one expertise field with user or phm source.
    """
    expertise_fields = [
        "expertise.programming.level",
        "expertise.ai_fluency.level",
        "expertise.business.level",
        "expertise.domain",
    ]
    for field in expertise_fields:
        source = field_sources.get(field, "default")
        if source in ("user", "phm"):
            return True
    return False


def run_inference(
    expertise: ExpertiseSection,
    field_sources: dict[str, str],
) -> tuple[dict[str, str | bool], dict[str, str]]:
    """Run inference rules and return (inferred_values, updated_field_sources).

    Returns only the fields that were actually changed.
    Does NOT modify field_sources in-place.
    """
    if not should_run_inference(field_sources):
        return {}, {}

    max_level = _get_max_expertise_level(expertise)
    inferred = dict(INFERENCE_TABLE.get(max_level, INFERENCE_TABLE["beginner"]))

    # Special case: if programming.level is "none" or "beginner" but max expertise
    # is higher (e.g., domain expert learning to code), cap language_complexity
    # at "professional" — don't use "technical" or "expert" for non-programmers.
    # Spec: "If programming.level = beginner but max expertise is advanced:
    #   language_complexity = professional (not technical)"
    # Spec: "If business.level = advanced but programming.level = none:
    #   language_complexity = professional (business vocabulary, not technical)"
    prog_level = expertise.programming.level
    if prog_level in ("none", "beginner") and max_level in ("advanced", "expert"):
        inferred["language_complexity"] = "professional"

    changed_values: dict[str, str | bool] = {}
    changed_sources: dict[str, str] = {}

    # Special case: programming.level == none forces include_code_samples = false
    programming_none = prog_level == "none"

    for field_key, inferred_value in inferred.items():
        if field_key in ("code_verbosity", "include_code_samples"):
            field_path = f"delivery.{field_key}"
        else:
            field_path = f"communication.{field_key}"

        # Special override for programming.level == none
        if programming_none and field_key == "include_code_samples":
            inferred_value = False
        elif programming_none and field_key == "code_verbosity":
            # code_verbosity is N/A when include_code_samples is false
            continue

        current_source = field_sources.get(field_path, "default")

        # Inferred can override default and inferred, but NOT user or phm
        if _can_override(current_source, "inferred"):
            changed_values[field_path] = inferred_value
            changed_sources[field_path] = "inferred"

    # Special case: code_verbosity based on programming level specifically
    if not programming_none:
        code_verb_map = {
            "none": "fully-explained",
            "beginner": "fully-explained",
            "intermediate": "annotated",
            "advanced": "minimal",
            "expert": "minimal",
        }
        code_verb = code_verb_map.get(prog_level, "annotated")
        field_path = "delivery.code_verbosity"
        current_source = field_sources.get(field_path, "default")
        if _can_override(current_source, "inferred"):
            changed_values[field_path] = code_verb
            changed_sources[field_path] = "inferred"

    logger.debug(
        "Inference: max_level=%s, programming=%s, changed=%d fields",
        max_level,
        expertise.programming.level,
        len(changed_values),
    )

    return changed_values, changed_sources
