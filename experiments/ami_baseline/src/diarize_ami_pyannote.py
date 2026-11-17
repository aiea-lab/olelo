#!/usr/bin/env python3
"""
Run pretrained pyannote speaker diarization on an AMI Mix-Headset recording.

Expected environment:
    pip install pyannote.audio==4.0.3

Before running:
    export HF_TOKEN="your_hugging_face_read_token"
    export HF_HOME=/data/model-cache/pyannote

Example:
    python diarize_ami_pyannote.py

Optional:
    python diarize_ami_pyannote.py \
        --meeting EN2003a \
        --num-speakers 4

Outputs:
    /data/ami-results/diarization/<meeting>.rttm
    /data/ami-results/diarization/<meeting>.json
"""

import argparse
import json
import os
from pathlib import Path

import torch
from pyannote.audio import Pipeline


DEFAULT_DATA_ROOT = Path("/data/ami-official/amicorpus")
DEFAULT_OUTPUT_ROOT = Path("/data/ami-results/diarization")
MODEL_ID = "pyannote/speaker-diarization-3.1"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Diarize an AMI Mix-Headset audio recording with pyannote."
    )
    parser.add_argument(
        "--meeting",
        default="EN2003a",
        help="AMI meeting ID (default: EN2003a).",
    )
    parser.add_argument(
        "--audio",
        type=Path,
        default=None,
        help="Optional explicit path to the input WAV file.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help=f"AMI corpus root (default: {DEFAULT_DATA_ROOT}).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output directory (default: {DEFAULT_OUTPUT_ROOT}).",
    )
    parser.add_argument(
        "--num-speakers",
        type=int,
        default=None,
        help="Optional known number of speakers, e.g. 4. Leave unset to estimate.",
    )
    parser.add_argument(
        "--min-speakers",
        type=int,
        default=None,
        help="Optional minimum speaker count (used only if --num-speakers is unset).",
    )
    parser.add_argument(
        "--max-speakers",
        type=int,
        default=None,
        help="Optional maximum speaker count (used only if --num-speakers is unset).",
    )
    return parser.parse_args()


def get_audio_path(args):
    if args.audio is not None:
        return args.audio

    return (
        args.data_root
        / args.meeting
        / "audio"
        / f"{args.meeting}.Mix-Headset.wav"
    )


def load_pipeline(token):
    print(f"Loading pretrained pipeline: {MODEL_ID}", flush=True)
    pipeline = Pipeline.from_pretrained(MODEL_ID, token=token)

    if pipeline is None:
        raise RuntimeError("pyannote did not return a pipeline. Check model access.")

    # Keep CPU thread usage modest for the current 1-CPU pod.
    torch.set_num_threads(1)

    # The current pod is CPU-only. If a CUDA device is available, use it.
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        print("Using CUDA.", flush=True)
    else:
        print("Using CPU.", flush=True)

    return pipeline


def normalize_annotation(result):
    """
    pyannote 3.1 normally returns an Annotation directly.
    This also supports newer output wrappers exposing
    `speaker_diarization`.
    """
    if hasattr(result, "itertracks"):
        return result

    annotation = getattr(result, "speaker_diarization", None)
    if annotation is not None and hasattr(annotation, "itertracks"):
        return annotation

    raise TypeError(
        "Unexpected diarization result type: "
        f"{type(result)!r}. Expected a pyannote Annotation."
    )


def save_outputs(annotation, meeting_id, output_root):
    output_root.mkdir(parents=True, exist_ok=True)

    rttm_path = output_root / f"{meeting_id}.rttm"
    json_path = output_root / f"{meeting_id}.json"

    # RTTM is a standard diarization format supported by pyannote.
    with rttm_path.open("w", encoding="utf-8") as rttm_file:
        annotation.write_rttm(rttm_file)

    segments = []
    for segment, track, speaker in annotation.itertracks(yield_label=True):
        segments.append(
            {
                "start": round(float(segment.start), 3),
                "end": round(float(segment.end), 3),
                "duration": round(float(segment.end - segment.start), 3),
                "speaker": str(speaker),
                "track": str(track),
            }
        )

    segments.sort(key=lambda item: (item["start"], item["end"]))

    speaker_ids = sorted({item["speaker"] for item in segments})
    payload = {
        "meeting_id": meeting_id,
        "model": MODEL_ID,
        "num_speakers": len(speaker_ids),
        "speakers": speaker_ids,
        "segments": segments,
    }

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(payload, json_file, indent=2)

    return rttm_path, json_path, speaker_ids, segments


def main():
    args = parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        raise EnvironmentError(
            "HF_TOKEN is not set. Export your Hugging Face read token "
            "in this shell before running the script."
        )

    audio_path = get_audio_path(args)
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Meeting: {args.meeting}", flush=True)
    print(f"Audio:   {audio_path}", flush=True)
    print(f"Size:    {audio_path.stat().st_size / (1024**2):.1f} MB", flush=True)

    pipeline = load_pipeline(token)

    inference_kwargs = {}
    if args.num_speakers is not None:
        inference_kwargs["num_speakers"] = args.num_speakers
    else:
        if args.min_speakers is not None:
            inference_kwargs["min_speakers"] = args.min_speakers
        if args.max_speakers is not None:
            inference_kwargs["max_speakers"] = args.max_speakers

    print("Running speaker diarization. This may take a while...", flush=True)
    result = pipeline(str(audio_path), **inference_kwargs)
    annotation = normalize_annotation(result)

    rttm_path, json_path, speaker_ids, segments = save_outputs(
        annotation, args.meeting, args.output_root
    )

    print("\nDiarization complete.", flush=True)
    print(f"Speakers detected ({len(speaker_ids)}): {', '.join(speaker_ids)}")
    print(f"Diarization segments: {len(segments)}")
    print(f"RTTM: {rttm_path}")
    print(f"JSON: {json_path}")

    print("\nFirst 10 diarization segments:")
    for item in segments[:10]:
        print(
            f"{item['start']:8.2f} - {item['end']:8.2f}  "
            f"{item['speaker']}"
        )


if __name__ == "__main__":
    main()