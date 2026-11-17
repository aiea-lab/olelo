import argparse
import json
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


def extract_features(audio, sample_rate, start, end):
    """Extract MFCC-based features from one speech segment."""

    start_sample = max(0, int(start * sample_rate))
    end_sample = min(len(audio), int(end * sample_rate))

    segment = audio[start_sample:end_sample]

    if len(segment) < int(0.25 * sample_rate):
        return None

    # MFCCs capture characteristics of the audio signal.
    mfcc = librosa.feature.mfcc(
        y=segment.astype(np.float32),
        sr=sample_rate,
        n_mfcc=20,
        n_fft=512,
        hop_length=160,
    )

    # Summarize each segment using mean and standard deviation.
    means = np.mean(mfcc, axis=1)
    stds = np.std(mfcc, axis=1)

    return np.concatenate([means, stds])


def main():
    parser = argparse.ArgumentParser(
        description="Simple audio-segment clustering baseline for diarization."
    )
    parser.add_argument(
        "--audio",
        default="/data/ami-corpus-mirror/sdm/EN2002a.Mix-Headset.wav",
    )
    parser.add_argument(
        "--transcript",
        default="/data/ami-results/transcripts/EN2002a.json",
    )
    parser.add_argument(
        "--output-dir",
        default="/data/ami-results/diarization",
    )
    parser.add_argument(
        "--speakers",
        type=int,
        default=4,
        help="Assumed number of speakers; default is 4.",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio)
    transcript_path = Path(args.transcript)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading audio: {audio_path}")
    audio, sample_rate = sf.read(audio_path)

    if audio.ndim == 2:
        audio = audio.mean(axis=1)

    print(f"Audio duration: {len(audio) / sample_rate / 60:.2f} minutes")

    with transcript_path.open("r", encoding="utf-8") as f:
        transcript_data = json.load(f)

    segments = transcript_data["segments"]

    features = []
    valid_segments = []

    print(f"Extracting features from {len(segments)} transcript segments...")

    for index, segment in enumerate(segments):
        feature = extract_features(
            audio,
            sample_rate,
            segment["start"],
            segment["end"],
        )

        if feature is not None and np.all(np.isfinite(feature)):
            features.append(feature)
            valid_segments.append(segment)

        if (index + 1) % 100 == 0:
            print(f"Processed {index + 1}/{len(segments)} segments")

    if len(features) < args.speakers:
        raise ValueError(
            "Not enough valid segments for the requested number of speakers."
        )

    feature_matrix = np.asarray(features)

    # Normalize feature dimensions before clustering.
    feature_matrix = StandardScaler().fit_transform(feature_matrix)

    # Cluster segments into the assumed number of speakers.
    clustering = AgglomerativeClustering(
        n_clusters=args.speakers,
        linkage="ward",
    )

    labels = clustering.fit_predict(feature_matrix)

    results = []

    for segment, label in zip(valid_segments, labels):
        results.append(
            {
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip(),
                "speaker_id": f"SPEAKER_{label:02d}",
            }
        )

    json_path = output_dir / "EN2002a_diarized.json"
    text_path = output_dir / "EN2002a_diarized.txt"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    with text_path.open("w", encoding="utf-8") as f:
        for segment in results:
            f.write(
                f"[{segment['start']:.2f}s - {segment['end']:.2f}s] "
                f"{segment['speaker_id']}: {segment['text']}\n"
            )

    print("\nDiarization baseline complete.")
    print(f"Segments assigned: {len(results)}")
    print(f"Assumed speakers: {args.speakers}")
    print(f"JSON output: {json_path}")
    print(f"Text output: {text_path}")
    print(
        "\nNote: These speaker labels are approximate clusters, "
        "not verified speaker identities."
    )


if __name__ == "__main__":
    main()

