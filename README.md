# ʻŌlelo

**ʻŌlelo** (Hawaiian: *language, speech, expression*) is a custom large language model developed by the AIEA Lab to support research, teaching, and experimentation in explainable and neurosymbolic AI.

The goal of ʻŌlelo is not just to generate a custom LLM for the AIEA lab  to **support structured reasoning, transparency, and responsible use of language models** in large-group, academic settings.

---

## 🌺 About the Name

In ʻŌlelo Hawaiʻi, **ʻōlelo** refers to language, speech, and meaningful expression.  
The name reflects our view of language models as systems that *express knowledge*, rather than opaque black boxes that merely predict tokens.

---

## 🎯 Project Goals

ʻŌlelo is designed to:
- Listen to meetings and produce meeting notes
- Be a custom tutor and helper for the lab (discord bot)
- Create workflows (automatically create Notion meeting notes, etc.)

Eventually, the project will:
- Support **research workflows** in explainable AI (XAI) and neurosymbolic methods
- Serve as a **teaching and mentoring aid** for students
- Enable **controlled experimentation** with reasoning, evaluation, and grounding
- Provide a platform for studying **what models know, don’t know, and how they explain it**

---

## High level overview

1. Wait for Zoom Webhook to fire. Zoom will send events, when a meeting is completed.
2. After an event is sent, the pipeline will capture all audio files from the specific meeting session then transcribe (Whisper) and diarize (Pyannote) them.
3. The diarizations will get matched with transcriptions based on timestamps.
4. Gemma (in-house LM) recieves the merged transcripts and diarizations and gives a brief summary of the meeting.

This project is intended primarily for **internal AIEA lab and academic use**.

## Transcribing Video/Audio Files with Whisper
Whisper is an open source transcription model created by OpenAI. 
| **Name** | **Parameters** | **English-only model** | **Multilingual model** | **Required VRAM** | **Relative Speed** |
| --- | --- | --- | --- | --- | --- |
| tiny | 39 M | tiny.en | tiny | ~1 GB | ~10x |
| base | 74 M | base.en | base | ~1 GB | ~7x |
| small | 244 M | small.en | small | ~2 GB | ~4x |
| medium | 769 M | medium.en | tiny | ~5 GB | ~10x | 
| large | 1550 M | N/A | large | ~10 GB | 1x | 
| turbo | 809 M | N/A | turbo | ~6 GB | ~8x |
#### Accepted File Types
Audio: 3GA, 8SVX, AAC, AC3, AIF, AIFF, ALAC, AMR, APE, AU, DSS, FLAC, M4A, M4B, M4P, M4R, MOGG, MP2, MP3, MPGA, OGG, OGA, OPUS, QCP, TTA, VOC, WAV, WMA \
Video: FLV, M2TS, M4V, MKV, MOV, MP4, MTS, MXF, TS, WEBM \
(Up to 5GB per file)

### TO USE:
1. Clone this git repo: 
```bash
git clone https://github.com/aiea-lab/olelo.git 
cd olelo
```
2. Install openai-whisper and its dependencies: 
```bash
pip install openai-whisper
```
3. Place files in `olelo/transcription_pipeline/files_to_transcribe`:
```bash
mkdir ./transcription_pipeline/files_to_transcribe
mv <path_to_your_files> ./transcription_pipeline/files_to_transcribe
```

5. Make sure you are inside the olelo directory and paste this script into your terminal (replace \<modeltype\> with one of the models above):
```bash
python ./transcription_pipeline/whisper_transcribe.py <model_type>
```
6. View your results in `transcription_pipeline/transcriptions.txt`
