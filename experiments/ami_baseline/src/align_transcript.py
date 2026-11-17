#!/usr/bin/env python3
"""Align Faster-Whisper transcript segments with pyannote speaker turns."""

import json
from collections import defaultdict
from pathlib import Path

MEETING = "EN2003a"

TRANSCRIPT_PATH = Path(
    f"/data/ami-results/transcripts/{MEETING}.json"
)
DIARIZATION_PATH = Path(
    f"/data/ami-results/diarization/{MEETING}.json"
)
OUTPUT_DIR = Path("/data/ami-results/aligned")


def main():
    if not TRANSCRIPT_PATH.exists():
        raise FileNotFoundError(f"Transcript not found: {TRANSCRIPT_PATH}")
    if not DIARIZATION_PATH.exists():
        raise FileNotFoundError(f"Diarization not found: {DIARIZATION_PATH}")

    with TRANSCRIPT_PATH.open() as f:
        transcript = json.load(f)

    with DIARIZATION_PATH.open() as f:
        diarization = json.load(f)

    diar_segments = diarization["segments"]
    aligned_segments = []

    for trans_seg in transcript["segments"]:
        start = float(trans_seg["start"])
        end = float(trans_seg["end"])
        duration = end - start

        if duration <= 0:
            continue

        speaker_overlap = defaultdict(float)

        for diar_seg in diar_segments:
            overlap_start = max(start, float(diar_seg["start"]))
            overlap_end = min(end, float(diar_seg["end"]))
            overlap = max(0.0, overlap_end - overlap_start)

            if overlap > 0:
                speaker_overlap[diar_seg["speaker"]] += overlap

        ranked = sorted(
            speaker_overlap.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        if ranked:
            primary_speaker = ranked[0][0]
            max_overlap = ranked[0][1]

            # Keep secondary speakers only when their overlap is meaningful.
            selected_speakers = [
                speaker
                for speaker, overlap in ranked
                if overlap >= 0.25 and overlap >= 0.15 * max_overlap
            ]
        else:
            primary_speaker = None
            selected_speakers = []

        aligned_segments.append(
            {
                "start": start,
                "end": end,
                "duration": round(duration, 3),
                "text": trans_seg["text"].strip(),
                "speaker": primary_speaker,
                "speakers": selected_speakers,
                "speaker_overlap_seconds": {
                    speaker: round(overlap, 3)
                    for speaker, overlap in ranked
                },
            }
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = {
        "meeting_id": MEETING,
        "transcription_model": transcript.get("model"),
        "diarization_model": diarization.get("model"),
        "num_speakers": diarization.get("num_speakers"),
        "num_transcript_segments": len(aligned_segments),
        "segments": aligned_segments,
    }

    json_output = OUTPUT_DIR / f"{MEETING}_aligned.json"
    txt_output = OUTPUT_DIR / f"{MEETING}_aligned.txt"

    with json_output.open("w") as f:
        json.dump(result, f, indent=2)

    with txt_output.open("w") as f:
        for seg in aligned_segments:
            speakers = seg["speakers"]
            speaker_label = " + ".join(speakers) if speakers else "UNKNOWN"
            f.write(
                f"[{seg['start']:07.2f} - {seg['end']:07.2f}] "
                f"{speaker_label}: {seg['text']}\n"
            )

    print("Alignment completed.")
    print(f"Transcript segments: {len(aligned_segments)}")
    print(f"JSON output: {json_output}")
    print(f"TXT output: {txt_output}")
    print("\nFirst 5 aligned segments:")

    for seg in aligned_segments[:5]:
        print(
            f"[{seg['start']:.2f}-{seg['end']:.2f}] "
            f"{seg['speakers']}: {seg['text'][:100]}"
        )


if __name__ == "__main__":
    main()
