# AMI Audio Transcription on Nautilus

This guide explains how to transcribe AMI Mix-Headset audio recordings using Faster-Whisper on Nautilus Kubernetes.

## 1. Prerequisites

* Nautilus access and a configured `kubectl` context.
* AMI dataset downloaded to the PVC.
* A running transcription pod (`olelo-transcription`).
* Transcription script: `experiments/ami_baseline/src/transcribe_ami.py`.

**Namespace:** `gilpin-lab`
**PVC:** `pkandhas-ami-data`
**PVC mount path:** `/data`

## 2. Check the Transcription Pod

Check whether the transcription pod is running:

```bash
kubectl get pod olelo-transcription -n gilpin-lab
```

The pod uses Python 3.11 and has Faster-Whisper and FFmpeg installed. It mounts the AMI PVC at `/data`.

If the pod is not running, create it using:

```bash
kubectl apply -f experiments/ami_baseline/scripts/ami-transcription-pod.yaml
```

## 3. Copy the Transcription Script

Copy the existing transcription script from the local repository into the pod:

```bash
kubectl cp experiments/ami_baseline/src/transcribe_ami.py \
  gilpin-lab/olelo-transcription:/tmp/transcribe_ami.py
```

Verify the copy:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- \
  ls -lh /tmp/transcribe_ami.py
```

## 4. Run Transcription

Run the script by specifying the audio file path and transcription settings.

Example using `EN2003a`:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- \
  python /tmp/transcribe_ami.py \
  --audio /data/ami-official/amicorpus/EN2003a/audio/EN2003a.Mix-Headset.wav \
  --output-dir /data/ami-results/transcripts \
  --model small \
  --device cpu \
  --compute-type int8 \
  --language en
```

### Transcription Parameters

| Parameter    | Value   | Description                                 |
| ------------ | ------- | ------------------------------------------- |
| Model        | `small` | Faster-Whisper model                        |
| Device       | `cpu`   | Runs on CPU                                 |
| Compute type | `int8`  | Reduces memory usage                        |
| Language     | `en`    | English audio                               |
| VAD filter   | Enabled | Filters out non-speech regions              |
| Beam size    | 5       | Decoding parameter configured in the script |

**Note:** Transcription can take several minutes depending on recording duration and CPU availability. The terminal may not display output immediately because Python output can be buffered.

## 5. Check Transcription Progress

Check whether the transcription process is running:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- ps aux
```

Check the output directory:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- \
  ls -lh /data/ami-results/transcripts/
```

The script writes the output files after processing the recording.

## 6. Check the Generated Files

Each recording produces two files:

* `.txt` – Plain-text transcript.
* `.json` – Timestamped transcript segments and metadata.

For example:

```text
/data/ami-results/transcripts/
├── EN2002a.txt
├── EN2002a.json
├── EN2003a.txt
└── EN2003a.json
```

Inspect the generated transcript:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- \
  head -c 2000 /data/ami-results/transcripts/EN2003a.txt
```

## 7. Transcribe Other Recordings

To transcribe another recording, reuse the same command and change the meeting ID and audio path.

For example, for `EN2004a`:

```bash
kubectl exec -n gilpin-lab olelo-transcription -- \
  python /tmp/transcribe_ami.py \
  --audio /data/ami-official/amicorpus/EN2004a/audio/EN2004a.Mix-Headset.wav \
  --output-dir /data/ami-results/transcripts \
  --model small \
  --device cpu \
  --compute-type int8 \
  --language en
```

Run recordings individually and check that their output files are generated successfully.

## Output Location

All transcription results are saved to:

```text
/data/ami-results/transcripts/
```
