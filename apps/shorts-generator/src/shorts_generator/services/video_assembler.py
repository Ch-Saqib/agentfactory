"""Video Assembly Service using FFmpeg.

This service composes the final video from:
- Scene images
- Audio narration
- Captions/text overlays
- Transitions between scenes

Video Spec:
- Format: MP4 (H.264 codec)
- Resolution: 1080x1920 (9:16 vertical)
- Frame rate: 30fps
- Max file size: 50MB
"""

import asyncio
import hashlib
import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from shorts_generator.services.audio_generator import GeneratedAudio
from shorts_generator.services.script_generator import GeneratedScript
from shorts_generator.services.storage import storage_service

logger = logging.getLogger(__name__)

# Video specifications
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 aspect ratio
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
VIDEO_BITRATE = "2M"  # 2 Mbps for good quality
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"
MAX_FILE_SIZE_MB = 50

# Caption styling — premium centered captions via ASS subtitles
CAPTION_FONT_SIZE = 68
CAPTION_MAX_CHARS = 72
CAPTION_MAX_LINES = 2
CAPTION_LINE_CHARS = 24  # tighter wrap → faster read → less "slow text" feel
CAPTION_FADE_IN_SECONDS = 0.22
CAPTION_FADE_OUT_SECONDS = 0.18
CAPTION_SLIDE_SECONDS = 0.22
CAPTION_SLIDE_PX = 80
CAPTION_MAX_ENTRIES = 18
CAPTION_ANIMATION_VARIANTS = 6  # up from 3 for more variety

# Karaoke word grouping — tighter = words don't linger
KARAOKE_MAX_WORDS_PER_GROUP = 5  # was 7
KARAOKE_MAX_GROUP_DURATION = 2.0  # was 2.8s
KARAOKE_MAX_GROUP_CHARS = 48  # CAPTION_LINE_CHARS × CAPTION_MAX_LINES

# Word-popup mode — 1-3 words at a time, each replacing the previous
POPUP_MAX_WORDS = 3
POPUP_MAX_CHARS = 25
POPUP_FONT_SIZE = 80  # larger since only a few words visible at once
POPUP_ANIMATION_VARIANTS = 3
POPUP_SCALE_DURATION_MS = 150  # pop-in duration
POPUP_FADE_OUT_MS = 100  # quick fade-out for snappy transitions


@dataclass
class AssembledVideo:
    """Represents an assembled video.

    Attributes:
        file_path: Path to the video file
        url: CDN URL for the video
        duration_seconds: Video duration in seconds
        file_size_mb: File size in MB
        width: Video width in pixels
        height: Video height in pixels
        thumbnail_url: URL to the thumbnail image
    """

    file_path: str
    url: str
    duration_seconds: float
    file_size_mb: float
    width: int
    height: int
    thumbnail_url: str


class VideoAssembler:
    """Assembles videos from scenes, audio, and captions using FFmpeg."""

    def __init__(self):
        """Initialize the video assembler."""
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=60.0)
        return self._http_client

    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get the actual duration of an audio file.

        Args:
            audio_path: Path to the audio file

        Returns:
            Duration in seconds, or 0 if detection fails
        """
        try:
            # Clean up file:// prefix
            if audio_path.startswith("file://"):
                audio_path = audio_path.replace("file://", "")

            # Use ffprobe to get accurate duration
            import subprocess
            result = await asyncio.to_thread(
                subprocess.run,
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                logger.info(f"Detected audio duration: {duration}s")
                return duration
            else:
                logger.warning(f"ffprobe failed: {result.stderr}")
                return 0.0
        except Exception as e:
            logger.warning(f"Could not detect audio duration: {e}")
            return 0.0

    async def _download_image_with_retry(self, image_url: str, max_retries: int = 3) -> str:
        """Download an image to a temp file with retry logic.

        Args:
            image_url: URL of the image to download
            max_retries: Maximum number of retry attempts

        Returns:
            Local file path to the downloaded image

        Raises:
            Exception: If download fails after all retries
        """
        client = await self._get_http_client()

        for attempt in range(max_retries):
            try:
                response = await client.get(image_url, timeout=60.0)
                response.raise_for_status()

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file.flush()
                    return tmp_file.name

            except httpx.HTTPStatusError as e:
                if 500 <= e.response.status_code < 600:
                    # Retry on server errors with exponential backoff
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.warning(
                            f"Image download failed with {e.response.status_code}, "
                            f"retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Image download failed: {e}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                raise

        raise Exception(f"Failed to download image after {max_retries} attempts")

    def _parse_captions_for_overlay(self, captions: str, script: GeneratedScript) -> list[dict]:
        """Parse SRT captions into list of timed text entries.

        Args:
            captions: SRT format captions
            script: Generated script for fallback text

        Returns:
            List of {start, end, text} dictionaries
        """
        caption_list = []

        if not captions:
            # Fallback to script scenes
            current_time = 0
            for scene in [script.hook] + script.concepts + [script.example, script.cta]:
                caption_list.append({
                    "start": current_time,
                    "end": current_time + scene.duration_seconds,
                    "text": scene.text
                })
                current_time += scene.duration_seconds
            return caption_list

        # Parse SRT format
        lines = captions.strip().split("\n")
        i = 0
        while i < len(lines):
            # Skip empty lines
            if not lines[i].strip():
                i += 1
                continue

            # Check if it's a sequence number
            if lines[i].strip().isdigit():
                # Next line should be timestamp
                if i + 1 < len(lines) and "-->" in lines[i + 1]:
                    time_line = lines[i + 1]
                    # Parse timestamp: "00:00:00,000 --> 00:00:02,500"
                    parts = time_line.split("-->")
                    if len(parts) == 2:
                        start_str = parts[0].strip().replace(",", ".")
                        end_str = parts[1].strip().replace(",", ".")

                        def parse_time(ts: str) -> float:
                            # Parse "HH:MM:SS.mmm" or "MM:SS.mmm"
                            parts = ts.split(":")
                            if len(parts) == 3:
                                h, m, s = parts
                                return float(h) * 3600 + float(m) * 60 + float(s)
                            elif len(parts) == 2:
                                m, s = parts
                                return float(m) * 60 + float(s)
                            return 0

                        start_time = parse_time(start_str)
                        end_time = parse_time(end_str)

                        # Next lines are the caption text (until empty line or next number)
                        i += 2
                        text_lines = []
                        while i < len(lines) and lines[i].strip() and not lines[i].strip().isdigit():
                            text_lines.append(lines[i].strip())
                            i += 1

                        if text_lines:
                            caption_list.append({
                                "start": start_time,
                                "end": end_time,
                                "text": " ".join(text_lines)
                            })
                        continue
            i += 1

        return caption_list

    def _compress_captions(self, captions: list[dict], max_entries: int = CAPTION_MAX_ENTRIES) -> list[dict]:
        """Reduce caption count by merging adjacent entries (keeps full timeline coverage)."""
        if len(captions) <= max_entries:
            return captions

        # Work on a copy to keep caller data safe.
        caps = [
            {"start": float(c["start"]), "end": float(c["end"]), "text": str(c["text"])}
            for c in captions
            if c.get("text")
        ]
        if len(caps) <= max_entries:
            return caps

        # Merge the shortest adjacent pair repeatedly until within limit.
        # This favors keeping longer captions (more important moments) intact.
        while len(caps) > max_entries:
            best_i = 0
            best_cost = float("inf")
            for i in range(len(caps) - 1):
                a = caps[i]
                b = caps[i + 1]
                merged_dur = max(0.0, float(b["end"]) - float(a["start"]))
                merged_len = len(a["text"]) + 1 + len(b["text"])
                # Cost: prioritize merging very short durations + long text bursts.
                cost = merged_dur * 10 + (merged_len / 80)
                if cost < best_cost:
                    best_cost = cost
                    best_i = i

            a = caps[best_i]
            b = caps[best_i + 1]
            merged = {
                "start": a["start"],
                "end": b["end"],
                "text": f"{a['text']} {b['text']}".strip(),
            }
            caps[best_i : best_i + 2] = [merged]

        return caps

    def _select_caption_animation_params(self, script: GeneratedScript, audio_path: str) -> tuple[int, int]:
        """Deterministically pick animation params so each video feels different."""
        seed = f"{script.lesson_path}|{script.lesson_title}|{audio_path}".encode("utf-8", errors="ignore")
        digest = hashlib.sha256(seed).hexdigest()
        variant = int(digest[:8], 16) % CAPTION_ANIMATION_VARIANTS
        seed_int = int(digest[8:16], 16)
        return variant, seed_int

    # ── ASS helpers ────────────────────────────────────────────────

    @staticmethod
    def _ass_time(seconds: float) -> str:
        """Format seconds as ASS timestamp ``H:MM:SS.cc``."""
        seconds = max(0.0, float(seconds))
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        cs = int(round((s - int(s)) * 100))
        return f"{h:d}:{m:02d}:{int(s):02d}.{cs:02d}"

    @staticmethod
    def _ass_escape(text: str) -> str:
        """Escape text for ASS dialogue lines."""
        text = text.replace("\\", "\\\\")
        text = text.replace("{", "(").replace("}", ")")
        return text

    @staticmethod
    def _wrap_text(text: str) -> str:
        """Soft-wrap text into CAPTION_MAX_LINES using ``\\N``."""
        words = text.split()
        if not words:
            return ""
        lines: list[str] = []
        current: list[str] = []
        for w in words:
            candidate = (" ".join(current + [w])).strip()
            if current and len(candidate) > CAPTION_LINE_CHARS:
                lines.append(" ".join(current))
                current = [w]
                if len(lines) >= CAPTION_MAX_LINES:
                    break
            else:
                current.append(w)
        if len(lines) < CAPTION_MAX_LINES and current:
            lines.append(" ".join(current))
        return "\\N".join(lines[:CAPTION_MAX_LINES])

    def _dynamic_fade(self, group_duration: float) -> tuple[int, int]:
        """Return (fade_in_ms, fade_out_ms) scaled to group duration."""
        fade_in = min(int(CAPTION_FADE_IN_SECONDS * 1000), int(group_duration * 150))
        fade_out = min(int(CAPTION_FADE_OUT_SECONDS * 1000), int(group_duration * 120))
        return max(80, fade_in), max(60, fade_out)

    def _pick_animation_tag(
        self,
        anim_index: int,
        center_x: int,
        center_y: int,
        fade_in_ms: int,
        fade_out_ms: int,
    ) -> str:
        """Return an ASS override tag for one of 6 animation variants."""
        anim = anim_index % CAPTION_ANIMATION_VARIANTS
        sp = CAPTION_SLIDE_PX

        if anim == 0:
            # Slide up to center + fade
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\move({center_x},{center_y+sp},{center_x},{center_y})}}")
        elif anim == 1:
            # Slide in from left + fade
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\move({-200},{center_y},{center_x},{center_y})}}")
        elif anim == 2:
            # Pop-in with bounce overshoot (60→110→100%)
            t1 = int(fade_in_ms * 0.6)
            t2 = fade_in_ms
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\fscx60\\fscy60"
                    f"\\t(0,{t1},\\fscx110\\fscy110)"
                    f"\\t({t1},{t2},\\fscx100\\fscy100)}}")
        elif anim == 3:
            # Bounce drop from above
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\move({center_x},{center_y-sp},{center_x},{center_y})}}")
        elif anim == 4:
            # Typewriter pop — scale from 0 on X + fade
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\fscx0\\t(0,{fade_in_ms},\\fscx100)}}")
        else:
            # Color sweep — fade in + colour shift accent→white
            return (f"{{\\fad({fade_in_ms},{fade_out_ms})"
                    f"\\c&H00FFFF&\\t(0,{fade_in_ms},\\c&HFFFFFF&)}}")

    def _ass_header(self, *, karaoke: bool = False, popup: bool = False) -> list[str]:
        """Build the [Script Info] + [V4+ Styles] header for ASS files."""
        ass: list[str] = []
        ass.append("[Script Info]")
        ass.append("ScriptType: v4.00+")
        ass.append(f"PlayResX: {VIDEO_WIDTH}")
        ass.append(f"PlayResY: {VIDEO_HEIGHT}")
        if karaoke:
            ass.append("WrapStyle: 2")
        ass.append("")
        ass.append("[V4+ Styles]")
        ass.append(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        )
        if popup:
            # Word-popup: large bold white, strong outline+shadow, center-center (Alignment 5)
            ass.append(
                "Style: Default,Arial Bold,"
                f"{POPUP_FONT_SIZE},"
                "&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
                "-1,0,0,0,100,100,2,0,1,6,4,5,80,80,200,1"
            )
        elif karaoke:
            # Karaoke: Primary = highlight (electric yellow), Secondary = base white
            # BorderStyle 1 = outline+shadow (cleaner than opaque box)
            ass.append(
                "Style: Default,Arial Bold,"
                f"{CAPTION_FONT_SIZE},"
                "&H0000FFFF,&H00FFFFFF,&H00000000,&H40000000,"
                "-1,0,0,0,100,100,1,0,1,5,3,5,80,80,120,1"
            )
        else:
            # Regular: white text, dark outline, subtle shadow
            ass.append(
                "Style: Default,Arial Bold,"
                f"{CAPTION_FONT_SIZE},"
                "&H00FFFFFF,&H00FFFFFF,&H00000000,&H40000000,"
                "-1,0,0,0,100,100,1,0,1,5,3,5,80,80,120,1"
            )
        ass.append("")
        ass.append("[Events]")
        ass.append(
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        )
        return ass

    # ── ASS subtitle builders ─────────────────────────────────────

    def _build_ass_subtitles_file(self, captions: list[dict], variant: int = 0, seed_int: int = 0) -> str:
        """Build an .ass subtitle file for centered, animated captions.

        We prefer ASS over drawtext for animation because it is more reliable and expressive:
        - Center alignment and margins
        - Fade and move animations (fad/move)
        - 6 animation variants for visual variety
        """
        captions = self._compress_captions(captions, max_entries=CAPTION_MAX_ENTRIES)

        center_x = VIDEO_WIDTH // 2
        center_y = VIDEO_HEIGHT // 2

        ass = self._ass_header(karaoke=False)

        for i, cap in enumerate(captions):
            start = float(cap["start"])
            end = float(cap["end"])
            if end <= start:
                continue

            text = str(cap["text"]).strip()
            text = " ".join(text.split())
            if len(text) > CAPTION_MAX_CHARS:
                text = text[: CAPTION_MAX_CHARS - 3].rstrip() + "..."
            text = self._ass_escape(self._wrap_text(text))

            fade_in_ms, fade_out_ms = self._dynamic_fade(end - start)
            tag = self._pick_animation_tag(
                seed_int + i + variant, center_x, center_y, fade_in_ms, fade_out_ms
            )

            ass.append(
                f"Dialogue: 0,{self._ass_time(start)},{self._ass_time(end)},Default,,0,0,0,,{tag}{text}"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ass", mode="w", encoding="utf-8") as tmp:
            tmp.write("\n".join(ass))
            tmp.flush()
            return tmp.name

    def _build_ass_karaoke_file(
        self,
        word_timings: list[dict[str, Any]],
        variant: int = 0,
        seed_int: int = 0,
    ) -> str:
        """Build a karaoke-style ASS subtitle file using word boundary timings.

        Uses tighter grouping (max 5 words / 2.0s) and 6 animation variants
        with dynamic fade speed tied to actual group duration.
        """
        # Normalize and clamp timings
        tokens: list[dict[str, Any]] = []
        for wt in word_timings:
            w = str(wt.get("word") or "").strip()
            if not w:
                continue
            start = float(wt.get("start") or 0.0)
            end = float(wt.get("end") or start)
            if end <= start:
                end = start + 0.12
            tokens.append({"word": w, "start": start, "end": end})

        if not tokens:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ass", mode="w", encoding="utf-8") as tmp:
                tmp.write("")
                tmp.flush()
                return tmp.name

        # ── Group words into tight display chunks ──
        lines: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []

        for tok in tokens:
            if not current:
                current.append(tok)
                continue

            next_len = len(" ".join(x["word"] for x in (current + [tok])))
            duration = float(tok["end"]) - float(current[0]["start"])

            if (
                len(current) >= KARAOKE_MAX_WORDS_PER_GROUP
                or next_len > KARAOKE_MAX_GROUP_CHARS
                or duration > KARAOKE_MAX_GROUP_DURATION
            ):
                lines.append(current)
                current = [tok]
            else:
                current.append(tok)

        if current:
            lines.append(current)

        center_x = VIDEO_WIDTH // 2
        center_y = VIDEO_HEIGHT // 2

        ass = self._ass_header(karaoke=True)

        for i, group in enumerate(lines):
            start = float(group[0]["start"])
            end = float(group[-1]["end"])
            group_dur = end - start

            # Build karaoke text with per-word \k (centiseconds)
            parts: list[str] = []
            for g in group:
                w = self._ass_escape(g["word"])
                dur_cs = max(1, int(round((float(g["end"]) - float(g["start"])) * 100)))
                parts.append(f"{{\\k{dur_cs}}}{w}")
            text = " ".join(parts)

            # Dynamic fade timing + one of 6 animation variants
            fade_in_ms, fade_out_ms = self._dynamic_fade(group_dur)
            tag = self._pick_animation_tag(
                seed_int + i + variant, center_x, center_y, fade_in_ms, fade_out_ms
            )

            ass.append(
                f"Dialogue: 0,{self._ass_time(start)},{self._ass_time(end)},Default,,0,0,0,,{tag}{text}"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ass", mode="w", encoding="utf-8") as tmp:
            tmp.write("\n".join(ass))
            tmp.flush()
            return tmp.name

    def _build_ass_word_popup_file(
        self,
        word_timings: list[dict[str, Any]],
        variant: int = 0,
        seed_int: int = 0,
    ) -> str:
        """Build a word-by-word popup ASS subtitle file.

        Each 1-3 word chunk gets its own Dialogue event with exact start/end
        times from word boundary data.  Text pops in with a scale animation
        and disappears before the next chunk appears — sync is guaranteed by
        construction since each chunk only exists during its spoken window.
        """
        # ── Normalize word timings ──────────────────────────────────
        tokens: list[dict[str, Any]] = []
        for wt in word_timings:
            w = str(wt.get("word") or "").strip()
            if not w:
                continue
            start = float(wt.get("start") or 0.0)
            end = float(wt.get("end") or start)
            if end <= start:
                end = start + 0.15
            tokens.append({"word": w, "start": start, "end": end})

        if not tokens:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".ass", mode="w", encoding="utf-8"
            ) as tmp:
                tmp.write("")
                tmp.flush()
                return tmp.name

        # ── Group words into 1-3 word chunks ───────────────────────
        groups: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []

        for tok in tokens:
            if not current:
                current.append(tok)
                continue

            candidate_text = " ".join(x["word"] for x in (current + [tok]))
            if (
                len(current) >= POPUP_MAX_WORDS
                or len(candidate_text) > POPUP_MAX_CHARS
            ):
                groups.append(current)
                current = [tok]
            else:
                current.append(tok)

        if current:
            groups.append(current)

        # ── Pick animation variant (deterministic per video) ───────
        anim = (seed_int + variant) % POPUP_ANIMATION_VARIANTS
        pop_ms = POPUP_SCALE_DURATION_MS
        fade_out = POPUP_FADE_OUT_MS

        # ── Build ASS dialogue events ──────────────────────────────
        ass = self._ass_header(popup=True)

        for i, group in enumerate(groups):
            g_start = float(group[0]["start"])
            g_end = float(group[-1]["end"])

            # Ensure minimum visible duration (at least 200ms)
            if g_end - g_start < 0.20:
                g_end = g_start + 0.20

            text = " ".join(self._ass_escape(g["word"]) for g in group)
            text = text.upper()  # all-caps for impact, like reference video

            # Build animation override tag
            if anim == 0:
                # Scale Pop: 0 → 105% → 100%
                t1 = pop_ms
                t2 = pop_ms + 50
                tag = (
                    f"{{\\fscx0\\fscy0"
                    f"\\t(0,{t1},\\fscx105\\fscy105)"
                    f"\\t({t1},{t2},\\fscx100\\fscy100)"
                    f"\\fad(0,{fade_out})}}"
                )
            elif anim == 1:
                # Slide Up Pop: move from 60px below to center + fade out
                cx = VIDEO_WIDTH // 2
                cy = int(VIDEO_HEIGHT * 0.58)
                tag = (
                    f"{{\\move({cx},{cy + 60},{cx},{cy},0,{pop_ms})"
                    f"\\fad(0,{fade_out})}}"
                )
            else:
                # Bounce Pop: 0 → 115% → 100%
                t1 = int(pop_ms * 0.65)
                t2 = pop_ms
                tag = (
                    f"{{\\fscx0\\fscy0"
                    f"\\t(0,{t1},\\fscx115\\fscy115)"
                    f"\\t({t1},{t2},\\fscx100\\fscy100)"
                    f"\\fad(0,{fade_out})}}"
                )

            ass.append(
                f"Dialogue: 0,{self._ass_time(g_start)},{self._ass_time(g_end)},"
                f"Default,,0,0,0,,{tag}{text}"
            )

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".ass", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write("\n".join(ass))
            tmp.flush()
            return tmp.name

    def _build_caption_filter(self, captions: list[dict], total_duration: float, variant: int = 0) -> str:
        """Build FFmpeg drawtext filter for dynamic caption overlay.

        Creates multiple drawtext filters that enable/disable at specific times,
        allowing captions to change throughout the video.

        Args:
            captions: List of {start, end, text} dictionaries
            total_duration: Total video duration

        Returns:
            FFmpeg filter string with chained drawtext filters
        """
        if not captions:
            return ""

        def _wrap_caption_text(text: str) -> str:
            """Soft-wrap caption to max lines, returning FFmpeg-safe newlines."""
            words = text.split()
            if not words:
                return ""

            lines: list[str] = []
            current: list[str] = []
            for w in words:
                candidate = (" ".join(current + [w])).strip()
                if current and len(candidate) > CAPTION_LINE_CHARS:
                    lines.append(" ".join(current))
                    current = [w]
                    if len(lines) >= CAPTION_MAX_LINES:
                        break
                else:
                    current.append(w)

            if len(lines) < CAPTION_MAX_LINES and current:
                lines.append(" ".join(current))

            # Join with drawtext newline escape. FFmpeg uses \n; inside a python
            # string used in a filtergraph we need a literal backslash+n.
            return "\\n".join(lines[:CAPTION_MAX_LINES])

        # Common caption styling (centered, mobile-first readability)
        # Note: x/y are expressions evaluated by FFmpeg.
        common_params = (
            f"fontsize={CAPTION_FONT_SIZE}:"
            f"fontcolor=white:"
            f"font=DejaVuSans:"
            f"shadowcolor=black@0.85:"
            f"shadowx=3:"
            f"shadowy=3:"
            f"line_spacing=12:"
            f"box=1:"
            f"boxcolor=black@0.45:"
            f"boxborderw=26:"
            f"borderw=2:"
            f"bordercolor=white@0.10:"
        )

        # Keep filtergraph size bounded, but preserve full timeline by compressing.
        captions = self._compress_captions(captions, max_entries=CAPTION_MAX_ENTRIES)

        # Create drawtext filters with timeline-based enable/disable
        # Format: enable='between(t,start,end)'
        filter_parts = []
        for i, cap in enumerate(captions):
            # Clean and escape text
            text = cap["text"].strip()
            # Remove newlines and excess whitespace
            text = " ".join(text.split())
            # Limit length (keep it readable; prefer wrapping over truncation)
            if len(text) > CAPTION_MAX_CHARS:
                text = text[: CAPTION_MAX_CHARS - 3].rstrip() + "..."
            text = _wrap_caption_text(text)
            # Escape special characters for FFmpeg
            text = text.replace("'", "'\\''").replace(":", "\\:")

            # Time range for this caption
            start = cap["start"]
            end = cap["end"]

            # Animation: slide-up + fade-in at start, fade-out near end.
            # y animates from center+CAPTION_SLIDE_PX to center over CAPTION_SLIDE_SECONDS.
            # Using min/max to clamp progress into [0,1].
            fade_in = CAPTION_FADE_IN_SECONDS
            fade_out = CAPTION_FADE_OUT_SECONDS
            slide_dur = CAPTION_SLIDE_SECONDS
            slide_px = CAPTION_SLIDE_PX

            alpha_expr = (
                "if(lt(t,{start}),0,"
                "if(lt(t,{start_fade_end}),(t-{start})/{fade_in},"
                "if(lt(t,{end_fade_start}),1,"
                "if(lt(t,{end}),({end}-t)/{fade_out},0))))"
            ).format(
                start=start,
                start_fade_end=start + fade_in,
                end=end,
                end_fade_start=max(start, end - fade_out),
                fade_in=fade_in,
                fade_out=fade_out,
            )

            y_expr = (
                "(h-text_h)/2"
                f"+{slide_px}*(1-min(max((t-{start})/{slide_dur},0),1))"
            )

            # Variant animation: keep it readable while adding variety.
            # 0: slide-up, 1: slide-in from left, 2: slide-down.
            progress = f"min(max((t-{start})/{slide_dur},0),1)"
            if variant % CAPTION_ANIMATION_VARIANTS == 1:
                x_expr = f"-text_w+((w+text_w)/2)*{progress}"
                y_expr = "(h-text_h)/2"
            elif variant % CAPTION_ANIMATION_VARIANTS == 2:
                x_expr = "(w-text_w)/2"
                y_expr = f"(h-text_h)/2-{slide_px}*(1-{progress})"
            else:
                x_expr = "(w-text_w)/2"

            # Create enable expression
            enable_expr = f"between(t,{start},{end})"

            # Build filter string
            # Each filter is chained to the previous one
            filter_str = (
                f"drawtext=text='{text}':"
                f"{common_params}"
                f"x={x_expr}:"
                f"y={y_expr}:"
                f"alpha='{alpha_expr}':"
                f"enable='{enable_expr}'"
            )

            filter_parts.append(filter_str)

        # Chain all filters together
        # FFmpeg applies filters in sequence, so each drawtext operates on the result
        return ",".join(filter_parts)

    def _build_alternative_caption_filter(self, captions: list[dict], total_duration: float) -> str:
        """Alternative method using filtergraphs for complex timing.

        This creates separate filter inputs and uses the overlay filter with
        enable expressions for more precise control.

        Args:
            captions: List of {start, end, text} dictionaries
            total_duration: Total video duration

        Returns:
            FFmpeg complex filtergraph string
        """
        if not captions:
            return ""

        # This is a fallback if the chained drawtext approach has issues
        # For now, use the simpler chained approach
        return self._build_caption_filter(captions, total_duration)

    def _build_kinetic_typography_filter(
        self,
        script_text: str,
        word_timing: list[dict] | None = None,
        animation_type: str = "fade",
    ) -> str:
        """Build kinetic typography filter with word-by-word animation.

        Creates animated text that appears word-by-word synced with speech.
        Supports multiple animation types: fade, popin, typewriter, slide.

        Args:
            script_text: Full text spoken by AI
            word_timing: Optional list of {word, start} timings. If None,
                        calculates timing based on word count (2.5 words/sec).
            animation_type: Type of animation - "fade", "popin", "typewriter", "slide"

        Returns:
            FFmpeg filter string with animated word overlays
        """
        import math

        words = script_text.split()

        # Calculate timing if not provided
        if word_timing is None:
            words_per_second = 2.5
            current_time = 0.5
            word_timing = []
            for word in words:
                word_timing.append({
                    "word": word,
                    "start": current_time,
                })
                current_time += 1.0 / words_per_second

        # Limit words for performance
        max_words = min(len(words), 20)
        words_to_animate = words[:max_words]
        timing = word_timing[:max_words]

        filter_parts = []

        if animation_type == "fade":
            # Fade-in animation for each word
            for i, wt in enumerate(timing):
                word = wt["word"].replace("'", "'\\''")
                start = wt["start"]
                fade_duration = 0.3

                # Position in grid
                col = i % 5
                row = i // 5
                x = 100 + col * 180
                y = 500 - row * 80

                filter_str = (
                    f"drawtext=text='{word}':"
                    f"fontsize=32:"
                    f"fontcolor=7c4dff:"
                    f"font=DejaVuSansBold:x={x}:y={y}:"
                    f"shadowcolor=000000cc:shadowx=2:shadowy=2:"
                    f"alpha='if(lt(t,{start}),0,if(lt(t,{start+fade_duration}),(t-{start})/{fade_duration},1))':"
                    f"enable='between(t,{start},{start+5})'"
                )
                filter_parts.append(filter_str)

        elif animation_type == "popin":
            # Pop-in animation with scale
            for i, wt in enumerate(timing):
                word = wt["word"].replace("'", "'\\''")
                start = wt["start"]
                pop_duration = 0.2

                # Circular position
                angle = (i / len(timing)) * 2 * math.pi
                radius = 350
                x = int(540 + radius * math.cos(angle))
                y = int(960 + radius * math.sin(angle))

                filter_str = (
                    f"drawtext=text='{word}':"
                    f"fontsize=38:"
                    f"fontcolor=00ffcc:"
                    f"font=DejaVuSansBold:x={x}:y={y}:"
                    f"shadowcolor=000000cc:shadowx=3:shadowy=3:"
                    f"alpha='if(lt(t,{start}),0,if(lt(t,{start+pop_duration}),(t-{start})/{pop_duration},1))':"
                    f"enable='between(t,{start},{start+4})'"
                )
                filter_parts.append(filter_str)

        elif animation_type == "typewriter":
            # Typewriter effect - reveal word by word in same position
            for i, wt in enumerate(timing):
                word = wt["word"].replace("'", "'\\''")
                start = wt["start"]
                # Each word appears in sequence at center
                filter_str = (
                    f"drawtext=text='{word}':"
                    f"fontsize=44:"
                    f"fontcolor=ffffff:"
                    f"font=DejaVuSansBold:x=(w-text_w)/2:y=850:"
                    f"shadowcolor=000000cc:shadowx=2:shadowy=2:"
                    f"enable='between(t,{start},{start+0.8})'"
                )
                filter_parts.append(filter_str)

        elif animation_type == "slide":
            # Slide in from left
            for i, wt in enumerate(timing):
                word = wt["word"].replace("'", "'\\''")
                start = wt["start"]
                slide_duration = 0.3

                # Stack vertically
                y = 400 + i * 70

                filter_str = (
                    f"drawtext=text='{word}':"
                    f"fontsize=30:"
                    f"fontcolor=ffa500:"
                    f"font=DejaVuSans:x=w-(w-(w-text_w)/2)*if(lt(t,{start}),1,if(lt(t,{start+slide_duration}),(t-{start})/{slide_duration},0)):y={y}:"
                    f"shadowcolor=000000cc:shadowx=2:shadowy=2:"
                    f"enable='between(t,{start},{start+3})'"
                )
                filter_parts.append(filter_str)

        elif animation_type == "centered":
            # Centered phrases - ONE AT A TIME for clean, readable layout
            # Group words into phrases of 2-3 words
            phrases = []
            current_phrase = []
            for word in words:
                current_phrase.append(word)
                if len(current_phrase) >= 2 or len(" ".join(current_phrase)) > 20:
                    phrases.append(" ".join(current_phrase))
                    current_phrase = []
            if current_phrase:
                phrases.append(" ".join(current_phrase))

            # Calculate timing for phrases (spread across available time)
            if timing:
                total_time = timing[-1]["start"] + 2.0  # Estimate total duration
            else:
                total_time = len(words) / 2.5

            time_per_phrase = total_time / len(phrases)
            phrase_start = 0.5

            for phrase in phrases:
                phrase_esc = phrase.replace("'", "'\\''")
                start = phrase_start
                end = phrase_start + time_per_phrase - 0.3  # Small gap

                # Centered text with smooth fade-in/out
                # Position: dead center of screen
                filter_str = (
                    f"drawtext=text='{phrase_esc}':"
                    f"fontsize=56:"
                    f"fontcolor=00ffcc:"
                    f"font=DejaVuSansBold:"
                    f"x=(w-text_w)/2:"
                    f"y=960:"  # Dead center vertically
                    f"shadowcolor=000000dd:"
                    f"shadowx=5:"
                    f"shadowy=5:"
                    # Fade in over 0.4s, stay visible, fade out over 0.3s
                    f"alpha='if(lt(t,{start}),0,if(lt(t,{start+0.4}),(t-{start})/0.4,if(lt(t,{end-0.3}),1,({end}-t)/0.3)))':"
                    f"enable='between(t,{start},{end})'"
                )
                filter_parts.append(filter_str)
                phrase_start = phrase_start + time_per_phrase

        return ",".join(filter_parts) if filter_parts else ""

    def _estimate_bitrate(self, duration_seconds: float, max_size_mb: int = MAX_FILE_SIZE_MB) -> str:
        """Estimate video bitrate to fit within file size limit.

        Args:
            duration_seconds: Target video duration
            max_size_mb: Maximum file size in MB

        Returns:
            Bitrate string for FFmpeg (e.g., "2M")
        """
        # Formula: bitrate = (file_size * 8) / duration
        # We use 90% of target size to leave room for overhead
        target_bits = (max_size_mb * 1024 * 1024 * 0.9 * 8) / duration_seconds

        # Convert to bits per second, then to kbps/Mbps
        if target_bits > 1_000_000:
            return f"{int(target_bits / 1_000_000)}M"
        elif target_bits > 1000:
            return f"{int(target_bits / 1000)}k"
        else:
            return f"{int(target_bits)}"

    async def assemble_video(
        self,
        scene_images: list[str],
        audio: GeneratedAudio,
        script: GeneratedScript,
        captions: str,
        script_text: str | None = None,
        transition: str = "fade",
    ) -> AssembledVideo:
        """Assemble video from scenes, audio, and captions.

        Args:
            scene_images: List of image URLs (one per scene)
            audio: GeneratedAudio with narration
            script: GeneratedScript with timing info
            captions: SRT format captions (fallback when word timings not available)
            script_text: Full TTS script text (optional; improves caption accuracy)
            transition: Transition type between scenes

        Returns:
            AssembledVideo object with video metadata

        Raises:
            Exception: If video assembly fails
        """
        logger.info(f"Assembling video from {len(scene_images)} scenes")

        try:
            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                output_path = tmp_file.name

                # Get actual audio duration from the audio file
                # This is more accurate than using script.total_duration
                audio_duration = await self._get_audio_duration(audio.file_path)
                total_duration = audio_duration if audio_duration > 0 else script.total_duration

                logger.info(f"Using audio duration: {audio_duration}s, script duration: {script.total_duration}s, final: {total_duration}s")

                # Calculate appropriate bitrate
                bitrate = self._estimate_bitrate(total_duration)

                # Prepare input files
                audio_path = audio.file_path
                if audio_path.startswith("file://"):
                    audio_path = audio_path.replace("file://", "")

                # Build filter complex for combining images
                # For simplicity, we'll use the first image for the entire video duration
                # In production, you'd want to overlay different images at different times

                # Clean up image URLs
                clean_images = []
                for img_url in scene_images[:1]:  # Use first image for now
                    if img_url.startswith("file://"):
                        clean_images.append(img_url.replace("file://", ""))
                    elif img_url.startswith("data:"):
                        # Save data URL to temp file
                        import base64
                        header, data = img_url.split(",", 1)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                            img_tmp.write(base64.b64decode(data))
                            img_tmp.flush()
                            clean_images.append(img_tmp.name)
                    elif img_url.startswith("http://") or img_url.startswith("https://"):
                        # Download remote image with retry logic
                        logger.info(f"Downloading remote image: {img_url[:80]}...")
                        local_path = await self._download_image_with_retry(img_url)
                        clean_images.append(local_path)
                    else:
                        clean_images.append(img_url)

                if not clean_images:
                    raise Exception("No valid images found for video generation")

                # Use subprocess to run ffmpeg directly (more reliable than ffmpeg-python)
                import subprocess

                # Parse captions for text overlay
                caption_texts = self._parse_captions_for_overlay(captions, script)
                caption_variant, caption_seed = self._select_caption_animation_params(script, audio_path)

                # Build video filter with scale and text overlay
                # Captions are rendered centered with a subtle entrance animation.
                video_filters = [f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}"]

                # Add text overlay for captions (if available)
                ass_path: str | None = None

                # 1) Best: word-by-word popup using word boundary timings.
                if getattr(audio, "word_timings", None):
                    ass_path = self._build_ass_word_popup_file(
                        audio.word_timings or [],
                        variant=caption_variant,
                        seed_int=caption_seed,
                    )
                    logger.info("Added word-popup captions via ASS word timings")
                # 2) Fallback: scene/SRT-level ASS captions.
                elif caption_texts:
                    ass_path = self._build_ass_subtitles_file(
                        caption_texts,
                        variant=caption_variant,
                        seed_int=caption_seed,
                    )
                    logger.info(f"Added {len(caption_texts)} caption overlays via ASS subtitles")

                if ass_path:
                    # Note: This requires ffmpeg built with libass (common in most distros).
                    video_filters.append(f"subtitles='{ass_path}'")

                vf_string = ",".join(video_filters)

                # Build ffmpeg command
                # Create slideshow from images with audio
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-loop", "1",  # Loop images
                    "-i", clean_images[0],  # Input image
                    "-i", audio_path,  # Input audio
                    "-c:v", "libx264",  # Video codec
                    "-tune", "stillimage",  # Optimize for still images
                    "-pix_fmt", "yuv420p",  # Better compatibility
                    "-vf", vf_string,  # Video filters with captions
                    "-t", str(total_duration),  # Duration
                    "-c:a", "aac",  # Audio codec
                    "-b:a", "128k",  # Audio bitrate
                    "-shortest",  # End when shortest input ends
                    "-movflags", "+faststart",  # Enable web playback
                    output_path,
                ]

                logger.info(f"Running ffmpeg: {' '.join(cmd[:5])}...")

                # Run ffmpeg
                result = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    raise Exception(f"Video assembly failed: {result.stderr}")

                logger.info(f"Video assembled: {output_path}")

                # Get file size
                file_size_bytes = os.path.getsize(output_path)
                file_size_mb = file_size_bytes / (1024 * 1024)

                # Generate thumbnail from first scene image
                # We need to ensure we have a local file path for the thumbnail
                thumbnail_path = await self._generate_thumbnail_from_scene(scene_images[0] if scene_images else "")

                # Upload to R2 storage
                video_id = str(uuid4())  # Generate ID for this video

                # Upload video
                video_upload = await storage_service.upload_video(
                    file_path=output_path,
                    video_id=video_id,
                )

                # Upload thumbnail
                thumbnail_upload = await storage_service.upload_thumbnail(
                    file_path=thumbnail_path.replace("file://", ""),
                    video_id=video_id,
                )

                video = AssembledVideo(
                    file_path=output_path,
                    url=video_upload["cdn_url"],  # R2 CDN URL
                    duration_seconds=total_duration,
                    file_size_mb=file_size_mb,
                    width=VIDEO_WIDTH,
                    height=VIDEO_HEIGHT,
                    thumbnail_url=thumbnail_upload["cdn_url"],  # R2 CDN URL
                )

                logger.info(f"Video assembled: {file_size_mb:.2f}MB, {total_duration}s")

                return video

        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise

    async def _generate_thumbnail_from_scene(self, first_scene_image_url: str) -> str:
        """Generate a thumbnail from the first scene image.

        Handles local files, data URLs, and remote URLs.

        Args:
            first_scene_image_url: URL to the first scene image

        Returns:
            Local file path to the generated thumbnail

        Raises:
            Exception: If thumbnail generation fails
        """
        logger.info("Generating thumbnail from first scene")

        try:
            import subprocess

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                output_path = tmp_file.name

                # Get local image path, downloading if necessary
                if first_scene_image_url.startswith("file://"):
                    image_path = first_scene_image_url.replace("file://", "")
                elif first_scene_image_url.startswith("data:"):
                    # Save data URL to temp file
                    import base64
                    header, data = first_scene_image_url.split(",", 1)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
                        img_tmp.write(base64.b64decode(data))
                        img_tmp.flush()
                        image_path = img_tmp.name
                elif first_scene_image_url.startswith("http://") or first_scene_image_url.startswith("https://"):
                    # Download remote image
                    logger.info(f"Downloading image for thumbnail: {first_scene_image_url[:80]}...")
                    image_path = await self._download_image_with_retry(first_scene_image_url)
                else:
                    # Assume it's a local file path
                    image_path = first_scene_image_url

                logger.info(f"Generating thumbnail from: {image_path}")

                # Use ffmpeg to resize the image to thumbnail dimensions
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output file
                    "-i", image_path,  # Input image
                    "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
                    "-q:v", "2",  # Quality for JPEG (2 is high quality)
                    output_path,
                ]

                result = await asyncio.to_thread(
                    subprocess.run,
                    cmd,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"FFmpeg thumbnail error: {result.stderr}")
                    # Fallback: just copy the original image
                    import shutil
                    shutil.copy(image_path, output_path)

                logger.info(f"Thumbnail generated: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            # Ultimate fallback: create a simple gradient thumbnail
            return await self._generate_fallback_thumbnail()

    async def _generate_fallback_thumbnail(self) -> str:
        """Generate a fallback thumbnail when image processing fails.

        Returns:
            Local file path to the generated thumbnail
        """
        logger.warning("Generating fallback thumbnail")

        try:
            from PIL import Image, ImageDraw

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                output_path = tmp_file.name

            # Create a simple gradient image
            img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
            draw = ImageDraw.Draw(img)

            # Create purple/blue gradient
            for y in range(VIDEO_HEIGHT):
                ratio = y / VIDEO_HEIGHT
                r = int(80 + (40 - 80) * ratio)
                g = int(40 + (20 - 40) * ratio)
                b = int(120 + (60 - 120) * ratio)
                for x in range(VIDEO_WIDTH):
                    img.putpixel((x, y), (r, g, b))

            # Add text
            try:
                from PIL import ImageFont
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
            except Exception:
                font = ImageFont.load_default()

            text = "AI Agent Factory"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = (VIDEO_WIDTH - text_width) // 2
            text_y = VIDEO_HEIGHT // 2 - 50
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

            # Save as JPEG
            img.save(output_path, "JPEG", quality=90)
            logger.info(f"Fallback thumbnail generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Fallback thumbnail failed: {e}")
            raise

    def optimize_for_web(
        self,
        video_path: str,
        target_size_mb: int = MAX_FILE_SIZE_MB,
    ) -> str:
        """Optimize video for web delivery.

        Args:
            video_path: Path to the video file
            target_size_mb: Target file size in MB

        Returns:
            Path to optimized video file

        Raises:
            Exception: If optimization fails
        """
        logger.info(f"Optimizing video for web (target: {target_size_mb}MB)")

        try:
            import ffmpeg

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                output_path = tmp_file.name

                # Probe original video
                probe = ffmpeg.probe(video_path)
                original_duration = float(probe.format["duration"])

                # Calculate new bitrate
                bitrate = self._estimate_bitrate(original_duration, target_size_mb)

                (
                    ffmpeg
                    .input(video_path)
                    .output(
                        output_path,
                        vcodec=VIDEO_CODEC,
                        video_bitrate=bitrate,
                        acodec=AUDIO_CODEC,
                        audio_bitrate=AUDIO_BITRATE,
                        movflags="+faststart",
                        pix_fmt="yuv420p",
                    )
                    .overwrite_output()
                    .run()
                )

                return output_path

        except Exception as e:
            logger.error(f"Video optimization failed: {e}")
            raise

    def _calculate_video_size(self, duration_seconds: float, bitrate_kbps: int) -> float:
        """Estimate video file size.

        Args:
            duration_seconds: Video duration
            bitrate_kbps: Video bitrate in kbps

        Returns:
            Estimated file size in MB
        """
        # Size (bits) = bitrate * duration
        # Add 10% for container overhead
        total_bits = (bitrate_kbps * 1000) * duration_seconds * 1.1
        total_mb = total_bits / (8 * 1024 * 1024)

        return total_mb

    async def assemble_video_from_assets(
        self,
        assets: dict[str, Any],
        script: GeneratedScript,
    ) -> AssembledVideo:
        """Assemble video from pre-generated assets.

        This is a simplified version for testing that takes
        pre-generated images and audio.

        Args:
            assets: Dictionary containing scene_images, audio_path, captions
            script: GeneratedScript

        Returns:
            AssembledVideo object
        """
        scene_images = assets.get("scene_images", [])
        audio_path = assets.get("audio_path")
        captions = assets.get("captions", "")

        # For testing, we'd need to create GeneratedAudio
        from shorts_generator.services.audio_generator import GeneratedAudio as Audio

        if not audio_path:
            # Create dummy audio for testing
            audio = Audio(
                url="file:///dev/null",
                duration_seconds=script.total_duration,
                file_path="/dev/null",
                generation_method="edge_tts",
                voice_used="test",
            )
        else:
            # TODO: Load audio from path
            pass

        return await self.assemble_video(
            scene_images=scene_images,
            audio=audio,
            script=script,
            captions=captions,
        )


# Singleton instance
video_assembler = VideoAssembler()
