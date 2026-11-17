import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from faster_whisper import WhisperModel

DEFAULT_AUDIO = Path(
    "/data/ami-corpus-mirror/sdm/EN2002a.Mix-Headset.wav"
)

DEFAULT_OUTPUT_DIR = Path("/data/ami-results/transcripts")
DEFAULT_MODEL_CACHE = Path("/data/model-cache/faster-whisper")


def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
    overwrite: bool = False,
) -> None:
    """Transcribe an audio file and save its text and timestamped segments."""

    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    DEFAULT_MODEL_CACHE.mkdir(parents=True, exist_ok=True)

    output_prefix = output_dir / audio_path.stem
    text_path = output_prefix.with_suffix(".txt")
    json_path = output_prefix.with_suffix(".json")

    if not overwrite and (text_path.exists() or json_path.exists()):
        raise FileExistsError(
            f"Output already exists for {audio_path.name}.\n"
            f"Text: {text_path}\n"
            f"JSON: {json_path}\n"
            "Choose another output directory or use --overwrite."
        )

    print(f"Audio: {audio_path}")
    print(f"Model: {model_name}")
    print(f"Device: {device}")
    print(f"Output directory: {output_dir}")

    # Load the pretrained Whisper model.
    model = WhisperModel(
        model_name,
        device=device,
        compute_type=compute_type,
        download_root=str(DEFAULT_MODEL_CACHE),
    )

    # Transcribe the audio.
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,
    )

    transcript_segments = []
    transcript_lines = []

    for segment in segments:
        text = segment.text.strip()

        transcript_segments.append(
            {
                "start": round(segment.start, 3),
                "end": round(segment.end, 3),
                "text": text,
            }
        )

        if text:
            transcript_lines.append(text)

        print(
            f"[{segment.start:8.2f}s - {segment.end:8.2f}s] "
            f"{text}"
        )

    # Save a readable transcript.
    full_text = " ".join(transcript_lines)

    text_path.write_text(full_text + "\n", encoding="utf-8")

    # Save timestamps and metadata
    result = {
        "audio_file": str(audio_path),
        "model": model_name,
        "language": info.language,
        "language_probability": info.language_probability,
        "duration_seconds": info.duration,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "segments": transcript_segments,
        "text": full_text,
    }

    json_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nTranscription complete!")
    print(f"Text transcript: {text_path}")
    print(f"Timestamped JSON: {json_path}")
    print(f"Segments generated: {len(transcript_segments)}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe AMI meeting audio using faster-whisper."
    )

    parser.add_argument(
        "--audio",
        type=Path,
        default=DEFAULT_AUDIO,
        help="Path to the input audio file.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for saved transcripts.",
    )

    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model size or model identifier. Default: small.",
    )

    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Inference device. Default: cpu.",
    )

    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Model computation type. Default: int8.",
    )

    parser.add_argument(
        "--language",
        default="en",
        help="Audio language code. Use 'en' for English or 'auto' for detection.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow existing transcript files to be overwritten.",
    )

    args = parser.parse_args()

    language = None if args.language.lower() == "auto" else args.language

    transcribe_audio(
        audio_path=args.audio,
        output_dir=args.output_dir,
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
        language=language,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()