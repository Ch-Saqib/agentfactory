---
name: generate-flashcards
description: "Generates a .flashcards.yaml spaced-repetition deck from a markdown lesson. Triggers when users ask to create flashcards from a specific document or lesson."
---

# Generate Flashcards

This skill extracts knowledge from a markdown lesson file and formats it into a `.flashcards.yaml` file for the build-time injection pipeline.

## ⚠️ Important Core Principle
Flashcards produced by this skill **MUST NOT** be trivial word-associations. They must be constructed strictly adhering to the rigorous cognitive science methodologies defining valid retrieval practice.

**Before generating any cards, you must completely read and understand the pedagogical intelligence moat defined in [Learning Sciences](references/learning_sciences.md).** Do not attempt to generate output without applying these rules.

## Execution Steps

1. **Read the Lesson:** Read the complete content of the user-specified markdown file using the `view_file` tool.
2. **Consult Methodology:** Read `references/learning_sciences.md` to ensure your extraction logic is primed for the Minimum Information Principle and Elaborative Interrogation.
3. **Format the Flashcard YAML:** Extract knowledge and format it precisely to the schema shown below. The `deck.id` should match the markdown file's basename (without `.md`), and `cards.id` should follow `${deck.id}-001`, `${deck.id}-002`, etc.
4. **Output Generation:** Write the new `[lesson-filename].flashcards.yaml` file into the *exact same directory* as the target markdown file.

## Expected YAML Schema

```yaml
deck:
  id: "lesson-id"
  title: "Lesson Title"
  description: "Brief description of the deck's coverage."
  tags: ["relevant", "tags"]
  version: 1

cards:
  - id: "lesson-id-001"
    front: "In the Agent Factory stack, what is the role of the **Factory** layer?"
    back: "It transforms Intent into Outcomes."
    tags: ["architecture"]
    difficulty: "basic" # basic | intermediate | advanced
    why: "Why is it described as an architecture rather than a single software application?" # CRITICAL for deeper synthesis
```
