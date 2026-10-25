from pathlib import Path

DATASET_DIR = Path("/data/ami-corpus-mirror")

print(f"Checking dataset at: {DATASET_DIR}")
print(f"Dataset directory exists: {DATASET_DIR.is_dir()}")

if DATASET_DIR.is_dir():
    print("\nDataset contents:")
    for item in sorted(DATASET_DIR.iterdir()):
        print(f"  {item.name}")

    audio_file = DATASET_DIR / "sdm" / "EN2002a.Mix-Headset.wav"

    print(f"\nTest audio: {audio_file}")
    print(f"Audio file exists: {audio_file.is_file()}")

    if audio_file.is_file():
        print(f"Audio file size: {audio_file.stat().st_size:,} bytes")

    annotation_file = (
        DATASET_DIR / "annotations" / "ami_public_manual_1.6.2.zip"
    )

    print(f"\nAnnotation archive exists: {annotation_file.is_file()}")

else:
    print(
        "\nDataset not found at this path"
    )