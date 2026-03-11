from __future__ import annotations

import argparse
import json
import re
import tempfile
import textwrap
import urllib.parse
import urllib.request
import wave
from contextlib import ExitStack
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

try:
    import numpy as np
except ImportError:
    np = None

try:
    import soundcard as sc
except ImportError:
    sc = None

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

DEFAULT_OUTPUT_DIR = Path("outputs")


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass
class MeetingSummary:
    title: str
    generated_at: str
    meeting_type: str
    executive_summary: str
    discussed_points: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    open_items: list[str] = field(default_factory=list)
    risks_or_blockers: list[str] = field(default_factory=list)
    conclusions: list[str] = field(default_factory=list)
    technical_notes: list[str] = field(default_factory=list)
    functional_notes: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


class LocalMeetingAssistant:
    def __init__(self, whisper_model_path: str | None, llm_model_path: str | None, compute_type: str, device: str, language: str | None) -> None:
        self.whisper_model_path = whisper_model_path
        self.llm_model_path = llm_model_path
        self.compute_type = compute_type
        self.device = device
        self.language = language
        self._whisper_model: WhisperModel | None = None
        self._llm: Llama | None = None

    def transcribe(self, media_path: Path) -> list[TranscriptSegment]:
        segments, _info = self._get_whisper_model().transcribe(
            str(media_path),
            beam_size=5,
            vad_filter=True,
            language=self.language,
            condition_on_previous_text=True,
        )
        return [TranscriptSegment(start=s.start, end=s.end, text=s.text.strip()) for s in segments if s.text.strip()]

    def summarize(self, transcript_text: str, title: str) -> MeetingSummary:
        generated_at = datetime.now().isoformat(timespec="seconds")
        heuristic = self._heuristic_summary(transcript_text, title, generated_at)
        if not self.llm_model_path:
            return heuristic
        if Llama is None:
            raise RuntimeError("Missing dependency: llama-cpp-python. Install requirements or omit --llm-model.")
        prompt = self._build_summary_prompt(title, transcript_text)
        response = self._get_llm().create_chat_completion(
            messages=[
                {"role": "system", "content": "You create high-quality meeting notes from a transcript. Return only valid JSON matching the requested schema."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        parsed = self._parse_summary_json(response["choices"][0]["message"]["content"], title, generated_at)
        return parsed or heuristic

    def _get_whisper_model(self) -> WhisperModel:
        if WhisperModel is None:
            raise RuntimeError("Missing dependency: faster-whisper. Install requirements before transcribing.")
        if not self.whisper_model_path:
            raise RuntimeError("A local Whisper model path is required for offline transcription.")
        if self._whisper_model is None:
            self._whisper_model = WhisperModel(self.whisper_model_path, device=self.device, compute_type=self.compute_type)
        return self._whisper_model

    def _get_llm(self) -> Llama:
        if self._llm is None:
            if Llama is None:
                raise RuntimeError("Missing dependency: llama-cpp-python. Install requirements or omit --llm-model.")
            if not self.llm_model_path:
                raise RuntimeError("A local GGUF model path is required for summarization.")
            self._llm = Llama(model_path=self.llm_model_path, n_ctx=8192, n_gpu_layers=-1 if self.device == "cuda" else 0, verbose=False)
        return self._llm

    def _build_summary_prompt(self, title: str, transcript_text: str) -> str:
        schema = {
            "meeting_type": "functional|technical|mixed|status|planning|review",
            "executive_summary": "string",
            "discussed_points": ["string"],
            "decisions": ["string"],
            "action_items": ["string"],
            "open_items": ["string"],
            "risks_or_blockers": ["string"],
            "conclusions": ["string"],
            "technical_notes": ["string"],
            "functional_notes": ["string"],
            "next_steps": ["string"],
        }
        return textwrap.dedent(f'''
        Create structured high-level meeting notes for "{title}".

        Requirements:
        - Capture the main outcomes from functional and technical discussion.
        - Extract decisions, action items, open items, blockers, and next steps.
        - Keep entries concise and specific.
        - If something is unclear, place it in open_items instead of inventing details.
        - Return only JSON using this schema:
        {json.dumps(schema, indent=2)}

        Transcript:
        {transcript_text}
        ''').strip()

    def _parse_summary_json(self, raw: str, title: str, generated_at: str) -> MeetingSummary | None:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return MeetingSummary(
            title=title,
            generated_at=generated_at,
            meeting_type=str(payload.get("meeting_type", "mixed")),
            executive_summary=str(payload.get("executive_summary", "")).strip(),
            discussed_points=_clean_list(payload.get("discussed_points")),
            decisions=_clean_list(payload.get("decisions")),
            action_items=_clean_list(payload.get("action_items")),
            open_items=_clean_list(payload.get("open_items")),
            risks_or_blockers=_clean_list(payload.get("risks_or_blockers")),
            conclusions=_clean_list(payload.get("conclusions")),
            technical_notes=_clean_list(payload.get("technical_notes")),
            functional_notes=_clean_list(payload.get("functional_notes")),
            next_steps=_clean_list(payload.get("next_steps")),
        )

    def _heuristic_summary(self, transcript_text: str, title: str, generated_at: str) -> MeetingSummary:
        lines = [line.strip() for line in transcript_text.splitlines() if line.strip()]
        sentences = split_sentences(transcript_text)
        decisions = find_sentences(sentences, [r"\bdecid", r"\bagreed?\b", r"\bfinali", r"\bapproved?\b", r"\bconfirm"])
        action_items = find_sentences(sentences, [r"\baction\b", r"\bwill\b", r"\bneed to\b", r"\bowner\b", r"\bfollow up\b"])
        open_items = find_sentences(sentences, [r"\bopen\b", r"\bquestion\b", r"\bunknown\b", r"\bpending\b", r"\bto be confirmed\b"])
        blockers = find_sentences(sentences, [r"\bblock", r"\brisk\b", r"\bissue\b", r"\bdependency\b", r"\bconcern\b"])
        technical = find_sentences(sentences, [r"\bapi\b", r"\bintegration\b", r"\bdatabase\b", r"\bservice\b", r"\bdeploy"])
        functional = find_sentences(sentences, [r"\buser\b", r"\bbusiness\b", r"\bprocess\b", r"\bworkflow\b", r"\brequirement\b"])
        discussed = unique_preserving_order(sentences[:10] + technical[:5] + functional[:5])[:12]
        conclusions = unique_preserving_order(decisions[:4] + [s for s in sentences if "conclusion" in s.lower()][:3])[:6]
        next_steps = unique_preserving_order(action_items[:6] + open_items[:3])[:8]
        summary_seed = " ".join(lines[:12])[:1200]
        executive_summary = re.sub(r"\s+", " ", summary_seed or "Transcript captured successfully. Review extracted sections below.").strip()
        meeting_type = "mixed"
        if technical and not functional:
            meeting_type = "technical"
        elif functional and not technical:
            meeting_type = "functional"
        return MeetingSummary(
            title=title,
            generated_at=generated_at,
            meeting_type=meeting_type,
            executive_summary=executive_summary,
            discussed_points=unique_preserving_order(discussed),
            decisions=unique_preserving_order(decisions)[:10],
            action_items=unique_preserving_order(action_items)[:10],
            open_items=unique_preserving_order(open_items)[:10],
            risks_or_blockers=unique_preserving_order(blockers)[:10],
            conclusions=unique_preserving_order(conclusions),
            technical_notes=unique_preserving_order(technical)[:10],
            functional_notes=unique_preserving_order(functional)[:10],
            next_steps=unique_preserving_order(next_steps),
        )


class MediaSourceResolver:
    def __init__(self) -> None:
        self._temp_files: list[Path] = []

    def resolve(self, source: str) -> Path:
        parsed = urllib.parse.urlparse(source)
        if parsed.scheme in {"http", "https"}:
            return self._download_url(self._resolve_remote_media_url(source))
        if parsed.scheme == "file":
            return Path(urllib.request.url2pathname(parsed.path))
        return Path(source)

    def cleanup(self) -> None:
        for path in self._temp_files:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    def _download_url(self, url: str) -> Path:
        suffix = Path(urllib.parse.urlparse(url).path).suffix or ".media"
        with urllib.request.urlopen(url) as response:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(response.read())
                temp_path = Path(tmp.name)
        self._temp_files.append(temp_path)
        return temp_path

    def _resolve_remote_media_url(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        if parsed.netloc.lower() == "screenrec.com" and parsed.path.startswith("/share/"):
            return self._extract_screenrec_media_url(url)
        return url

    def _extract_screenrec_media_url(self, share_url: str) -> str:
        request = urllib.request.Request(share_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request) as response:
            html = response.read().decode("utf-8", errors="ignore")
        match = re.search(r"customUrl:\s*'([^']+)'", html)
        if not match:
            raise RuntimeError("Could not extract a media URL from the ScreenRec share page.")
        return match.group(1)


class LiveAudioCapture:
    def __init__(self, sample_rate: int) -> None:
        self.sample_rate = sample_rate

    def list_sources(self) -> dict[str, list[dict[str, str]]]:
        if sc is None:
            raise RuntimeError("Missing dependency: soundcard.")
        default_microphone = sc.default_microphone()
        default_speaker = sc.default_speaker()
        return {
            "microphones": [
                {"id": m.id, "name": m.name, "default": str(default_microphone is not None and m.id == default_microphone.id)}
                for m in sc.all_microphones()
            ],
            "speakers": [
                {"id": s.id, "name": s.name, "default": str(default_speaker is not None and s.id == default_speaker.id)}
                for s in sc.all_speakers()
            ],
        }

    def record(self, output_path: Path, microphone_id: str | None, speaker_id: str | None, include_mic: bool, include_speaker: bool, seconds: int | None) -> None:
        frames = [audio for _offset, audio in self.stream_chunks(microphone_id, speaker_id, include_mic, include_speaker, max(seconds or 45, 1), seconds)]
        if not frames:
            raise RuntimeError("No live audio was captured.")
        self.write_wav(output_path, _float_audio_to_pcm(np.concatenate(frames, axis=0)))

    def stream_chunks(self, microphone_id: str | None, speaker_id: str | None, include_mic: bool, include_speaker: bool, chunk_seconds: int, seconds: int | None) -> Iterator[tuple[int, Any]]:
        if sc is None or np is None:
            raise RuntimeError("Missing dependencies: soundcard and numpy.")
        if not include_mic and not include_speaker:
            raise RuntimeError("At least one live source must be enabled.")
        block_frames = 1024
        chunk_frames_target = max(chunk_seconds * self.sample_rate, block_frames)
        total_target_frames = None if seconds is None else int(seconds * self.sample_rate)
        total_captured_frames = 0
        microphone = self._resolve_microphone(microphone_id) if include_mic else None
        speaker_loopback = self._resolve_speaker_loopback(speaker_id) if include_speaker else None
        with ExitStack() as stack:
            mic_recorder = stack.enter_context(microphone.recorder(samplerate=self.sample_rate)) if microphone is not None else None
            speaker_recorder = stack.enter_context(speaker_loopback.recorder(samplerate=self.sample_rate)) if speaker_loopback is not None else None
            print("Live capture started. Press Ctrl+C to stop.")
            try:
                while True:
                    chunk_frames: list[Any] = []
                    chunk_start = total_captured_frames
                    chunk_captured = 0
                    while chunk_captured < chunk_frames_target:
                        block_parts: list[Any] = []
                        if mic_recorder is not None:
                            block_parts.append(_to_mono(mic_recorder.record(numframes=block_frames)))
                        if speaker_recorder is not None:
                            block_parts.append(_to_mono(speaker_recorder.record(numframes=block_frames)))
                        if not block_parts:
                            continue
                        max_length = max(len(part) for part in block_parts)
                        aligned = [_pad_audio(part, max_length) for part in block_parts]
                        mixed = np.mean(np.stack(aligned, axis=0), axis=0)
                        chunk_frames.append(mixed)
                        chunk_captured += len(mixed)
                        total_captured_frames += len(mixed)
                        if total_target_frames is not None and total_captured_frames >= total_target_frames:
                            break
                    if chunk_frames:
                        yield chunk_start, np.concatenate(chunk_frames, axis=0)
                    if total_target_frames is not None and total_captured_frames >= total_target_frames:
                        break
            except KeyboardInterrupt:
                print("Live capture stopped.")

    def _resolve_microphone(self, microphone_id: str | None) -> Any:
        if microphone_id:
            microphone = sc.get_microphone(microphone_id, include_loopback=False)
            if microphone is None:
                raise RuntimeError(f"Microphone not found: {microphone_id}")
            return microphone
        microphone = sc.default_microphone()
        if microphone is None:
            raise RuntimeError("No default microphone is available.")
        return microphone

    def _resolve_speaker_loopback(self, speaker_id: str | None) -> Any:
        if speaker_id:
            loopback = sc.get_microphone(speaker_id, include_loopback=True)
            if loopback is None:
                raise RuntimeError(f"Speaker loopback not found: {speaker_id}")
            return loopback
        default_speaker = sc.default_speaker()
        if default_speaker is None:
            raise RuntimeError("No default speaker is available.")
        loopback = sc.get_microphone(default_speaker.id, include_loopback=True) or sc.get_microphone(default_speaker.name, include_loopback=True)
        if loopback is None:
            raise RuntimeError("Default speaker loopback could not be opened.")
        return loopback

    def write_wav(self, output_path: Path, audio: Any) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio.tobytes())


def _to_mono(audio: Any) -> Any:
    if np is None:
        raise RuntimeError("Missing dependency: numpy.")
    data = np.asarray(audio, dtype=np.float32)
    return data if data.ndim == 1 else data.mean(axis=1)


def _pad_audio(audio: Any, target_length: int) -> Any:
    if np is None:
        raise RuntimeError("Missing dependency: numpy.")
    if len(audio) >= target_length:
        return audio[:target_length]
    return np.concatenate([audio, np.zeros(target_length - len(audio), dtype=np.float32)], axis=0)


def _float_audio_to_pcm(audio: Any) -> Any:
    if np is None:
        raise RuntimeError("Missing dependency: numpy.")
    return (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)


def _clean_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return unique_preserving_order([str(item).strip() for item in value if str(item).strip()])


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    cleaned = [re.sub(r"\s+", " ", part).strip(" -\t") for part in parts]
    return [part for part in cleaned if len(part) > 20]


def find_sentences(sentences: list[str], patterns: list[str]) -> list[str]:
    compiled = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    return [sentence for sentence in sentences if any(pattern.search(sentence) for pattern in compiled)]


def unique_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        lowered = item.lower()
        if item and lowered not in seen:
            seen.add(lowered)
            unique.append(item)
    return unique


def segments_to_text(segments: list[TranscriptSegment]) -> str:
    return "\n".join(f"[{format_ts(segment.start)} - {format_ts(segment.end)}] {segment.text}" for segment in segments)


def format_ts(seconds: float) -> str:
    total = int(seconds)
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def render_markdown(summary: MeetingSummary) -> str:
    sections = [
        ("Executive Summary", [summary.executive_summary]),
        ("Discussed Points", summary.discussed_points),
        ("Decisions", summary.decisions),
        ("Action Items", summary.action_items),
        ("Open Items", summary.open_items),
        ("Risks / Blockers", summary.risks_or_blockers),
        ("Conclusions", summary.conclusions),
        ("Technical Notes", summary.technical_notes),
        ("Functional Notes", summary.functional_notes),
        ("Next Steps", summary.next_steps),
    ]
    lines = [f"# {summary.title}", "", f"- Generated At: {summary.generated_at}", f"- Meeting Type: {summary.meeting_type}", ""]
    for heading, items in sections:
        lines.append(f"## {heading}")
        lines.extend(f"- {item}" for item in (items or ["None captured"]))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_mom(summary: MeetingSummary) -> str:
    lines = [
        "# Meeting Minutes", "", "## Meeting", "", f"- Title: {summary.title}", f"- Generated At: {summary.generated_at}", f"- Meeting Type: {summary.meeting_type}", "", "## Executive Summary", "", f"- {summary.executive_summary or 'None captured'}", "", "## Discussed Points", ""
    ]
    lines.extend(f"- {item}" for item in (summary.discussed_points or ["None captured"]))
    for heading, items in [
        ("Decisions", summary.decisions),
        ("Action Items", summary.action_items),
        ("Open Questions", summary.open_items),
        ("Risks And Blockers", summary.risks_or_blockers),
        ("Technical Notes", summary.technical_notes),
        ("Functional Notes", summary.functional_notes),
        ("Next Steps", summary.next_steps),
    ]:
        lines.extend(["", f"## {heading}", ""])
        lines.extend(f"- {item}" for item in (items or ["None captured"]))
    return "\n".join(lines).strip() + "\n"


def export_outputs(output_dir: Path, base_name: str, transcript_segments: list[TranscriptSegment], summary: MeetingSummary) -> tuple[Path, Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / f"{base_name}_transcript.txt"
    summary_path = output_dir / f"{base_name}_summary.md"
    summary_json_path = output_dir / f"{base_name}_summary.json"
    mom_path = output_dir / f"{base_name}_mom.md"
    transcript_path.write_text(segments_to_text(transcript_segments), encoding="utf-8")
    summary_path.write_text(render_markdown(summary), encoding="utf-8")
    summary_json_path.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
    mom_path.write_text(render_mom(summary), encoding="utf-8")
    return transcript_path, summary_path, summary_json_path, mom_path


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip()).strip("_").lower() or "meeting"


def process_media_source(source_path: Path, args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    assistant = LocalMeetingAssistant(args.whisper_model, args.llm_model, args.compute_type, args.device, args.language)
    transcript_segments = assistant.transcribe(source_path)
    summary = assistant.summarize(segments_to_text(transcript_segments), args.title)
    return export_outputs(Path(args.output_dir), f"{slugify(args.title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}", transcript_segments, summary)


def run_live_notes(args: argparse.Namespace) -> tuple[Path, Path, Path, Path]:
    if np is None:
        raise RuntimeError("Missing dependency: numpy.")
    output_dir = Path(args.output_dir)
    base_name = f"{slugify(args.title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    chunk_dir = output_dir / f"{base_name}_chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)
    assistant = LocalMeetingAssistant(args.whisper_model, args.llm_model, args.compute_type, args.device, args.language)
    capture = LiveAudioCapture(sample_rate=args.sample_rate)
    transcript_segments: list[TranscriptSegment] = []
    latest_summary = MeetingSummary(title=args.title, generated_at=datetime.now().isoformat(timespec="seconds"), meeting_type="mixed", executive_summary="Live listening started. Waiting for transcript before generating notes.")
    latest_paths = export_outputs(output_dir, base_name, transcript_segments, latest_summary)
    for index, (offset_frames, audio_chunk) in enumerate(capture.stream_chunks(args.microphone_id, args.speaker_id, not args.no_mic, not args.no_speaker, args.chunk_seconds, args.seconds), start=1):
        chunk_path = chunk_dir / f"chunk_{index:04d}.wav"
        capture.write_wav(chunk_path, _float_audio_to_pcm(audio_chunk))
        chunk_segments = assistant.transcribe(chunk_path)
        offset_seconds = offset_frames / args.sample_rate
        transcript_segments.extend([TranscriptSegment(start=s.start + offset_seconds, end=s.end + offset_seconds, text=s.text) for s in chunk_segments])
        if transcript_segments and index % args.summary_every_chunks == 0:
            latest_summary = assistant.summarize(segments_to_text(transcript_segments), args.title)
            latest_paths = export_outputs(output_dir, base_name, transcript_segments, latest_summary)
            print(f"Updated live notes after chunk {index}: {latest_paths[1].name}, {latest_paths[3].name}")
    if transcript_segments:
        latest_summary = assistant.summarize(segments_to_text(transcript_segments), args.title)
        latest_paths = export_outputs(output_dir, base_name, transcript_segments, latest_summary)
    return latest_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local meeting assistant for Teams-style calls using local media capture, local Whisper transcription, and an optional local GGUF summarization model.")
    parser.add_argument("--title", default="Teams Meeting Notes", help="Title for the exported notes.")
    parser.add_argument("--whisper-model", help="Path to a local Whisper model directory.")
    parser.add_argument("--llm-model", help="Path to a local GGUF LLM model for summarization.")
    parser.add_argument("--language", help="Force transcription language, for example en.")
    parser.add_argument("--compute-type", default="int8", help="Whisper compute type, for example int8 or float16.")
    parser.add_argument("--device", default="cpu", help="Transcription device: cpu or cuda.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for transcripts and summaries.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sources_parser = subparsers.add_parser("sources", help="List available live microphone and speaker sources.")
    sources_parser.add_argument("--sample-rate", type=int, default=16000)

    capture_parser = subparsers.add_parser("capture", help="Capture live audio from system speaker, microphone, or both.")
    capture_parser.add_argument("--audio-out", default="outputs/live_meeting.wav", help="Recorded WAV output path.")
    capture_parser.add_argument("--speaker-id", help="Speaker id from the sources command.")
    capture_parser.add_argument("--microphone-id", help="Microphone id from the sources command.")
    capture_parser.add_argument("--sample-rate", type=int, default=16000)
    capture_parser.add_argument("--seconds", type=int, help="Optional duration for capture. Otherwise use Ctrl+C.")
    capture_parser.add_argument("--no-speaker", action="store_true", help="Disable system speaker capture.")
    capture_parser.add_argument("--no-mic", action="store_true", help="Disable microphone capture.")

    process_parser = subparsers.add_parser("process", help="Process a local audio/video file or a direct media URL and generate notes.")
    process_parser.add_argument("--source", required=True, help="Local media path, file:// path, or direct media URL.")

    run_parser = subparsers.add_parser("run", help="Capture live speaker/microphone audio and summarize after the call ends.")
    run_parser.add_argument("--audio-out", default="outputs/live_meeting.wav", help="Recorded WAV output path.")
    run_parser.add_argument("--speaker-id", help="Speaker id from the sources command.")
    run_parser.add_argument("--microphone-id", help="Microphone id from the sources command.")
    run_parser.add_argument("--sample-rate", type=int, default=16000)
    run_parser.add_argument("--seconds", type=int, help="Optional duration for capture. Otherwise use Ctrl+C.")
    run_parser.add_argument("--no-speaker", action="store_true", help="Disable system speaker capture.")
    run_parser.add_argument("--no-mic", action="store_true", help="Disable microphone capture.")

    live_parser = subparsers.add_parser("live", help="Listen live, update transcript continuously, and refresh notes and MoM while the meeting is running.")
    live_parser.add_argument("--speaker-id", help="Speaker id from the sources command.")
    live_parser.add_argument("--microphone-id", help="Microphone id from the sources command.")
    live_parser.add_argument("--sample-rate", type=int, default=16000)
    live_parser.add_argument("--seconds", type=int, help="Optional duration for the live session.")
    live_parser.add_argument("--chunk-seconds", type=int, default=45, help="Chunk size for rolling transcription.")
    live_parser.add_argument("--summary-every-chunks", type=int, default=2, help="Refresh summary and MoM after this many chunks.")
    live_parser.add_argument("--no-speaker", action="store_true", help="Disable system speaker capture.")
    live_parser.add_argument("--no-mic", action="store_true", help="Disable microphone capture.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "sources":
        print(json.dumps(LiveAudioCapture(sample_rate=args.sample_rate).list_sources(), indent=2, ensure_ascii=True))
        return 0
    if args.command == "capture":
        LiveAudioCapture(sample_rate=args.sample_rate).record(Path(args.audio_out), args.microphone_id, args.speaker_id, not args.no_mic, not args.no_speaker, args.seconds)
        print(f"Live capture saved to {args.audio_out}")
        return 0
    if args.command == "run":
        LiveAudioCapture(sample_rate=args.sample_rate).record(Path(args.audio_out), args.microphone_id, args.speaker_id, not args.no_mic, not args.no_speaker, args.seconds)
        transcript_path, summary_path, summary_json_path, mom_path = process_media_source(Path(args.audio_out), args)
        print(f"Transcript saved to {transcript_path}")
        print(f"Summary saved to {summary_path}")
        print(f"Summary JSON saved to {summary_json_path}")
        print(f"MoM saved to {mom_path}")
        return 0
    if args.command == "live":
        transcript_path, summary_path, summary_json_path, mom_path = run_live_notes(args)
        print(f"Transcript saved to {transcript_path}")
        print(f"Summary saved to {summary_path}")
        print(f"Summary JSON saved to {summary_json_path}")
        print(f"MoM saved to {mom_path}")
        return 0
    resolver = MediaSourceResolver()
    try:
        source_path = resolver.resolve(args.source)
        if not source_path.exists():
            raise FileNotFoundError(f"Media source not found: {source_path}")
        transcript_path, summary_path, summary_json_path, mom_path = process_media_source(source_path, args)
    finally:
        resolver.cleanup()
    print(f"Transcript saved to {transcript_path}")
    print(f"Summary saved to {summary_path}")
    print(f"Summary JSON saved to {summary_json_path}")
    print(f"MoM saved to {mom_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
