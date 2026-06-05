import os
import torch
from prompts import generate_chunk_prompt, generate_final_prompt
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, AutoFeatureExtractor
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
from pydub import AudioSegment
from tempfile import TemporaryDirectory
from transformers import AutoProcessor, AutoModelForImageTextToText



_pyannote_pipeline = None
_whisper_pipeline = None
_gemma_processor = None
_gemma_model = None


## Pyannote

def init_pyannote():
    global _pyannote_pipeline
    _pyannote_pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-community-1",
    token=os.getenv("HF_API_KEY"))

    _pyannote_pipeline.to(torch.device("cuda"))

def get_pyannote_model():
    global _pyannote_pipeline
    if _pyannote_pipeline is None:
        init_pyannote()
    return _pyannote_pipeline



## Whisper API

def init_whisper():
    global _whisper_pipeline
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-large-v3-turbo"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)
    processor = AutoProcessor.from_pretrained(model_id)
    _whisper_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True
    )

def get_whisper_model():
    global _whisper_pipeline
    if _whisper_pipeline is None:
        init_whisper()
    return _whisper_pipeline

## gemma
def init_gemma():
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    _gemma_processor = AutoProcessor.from_pretrained("google/gemma-3-12b-it", token = os.getenv('HF_API_KEY'))
    _model = AutoModelForImageTextToText.from_pretrained("google/gemma-3-12b-it", token = os.getenv('HF_API_KEY'))
    _model.to(device)

def query_gemma(query):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
            ]
        },
    ]
    inputs = _gemma_processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(_gemma_model.device)

    outputs = _gemma_model.generate(**inputs, max_new_tokens=8192)
    summary = _gemma_processor.decode(outputs[0][inputs["input_ids"].shape[-1]:])

    return summary


def diar_transcribe(audio_file: str):

    global _pyannote_pipeline
    if _pyannote_pipeline is None:
        init_pyannote()

    global _whisper_pipeline
    if _whisper_pipeline is None:
        init_whisper()

    with TemporaryDirectory() as tmp:
        wav_aud_file = os.path.join(tmp, "wav_audio_file.wav")
        audio = AudioSegment.from_file(audio_file, format="m4a")
        audio.export(wav_aud_file, format="wav") 

        with ProgressHook() as hook:
            diarizations = _pyannote_pipeline(wav_aud_file, hook = hook)

        transcriptions = _whisper_pipeline(wav_aud_file)

    return diarizations, transcriptions

def calc_overlap(d_time_start, d_time_end, t_time_start, t_time_end):
    overlap = max(0.0, min(d_time_end, t_time_end) - max(d_time_start, t_time_start))
    duration = max(t_time_end - t_time_start, 1e-8)
    return overlap / duration

def merge_trans_diar(diarizations, transcriptions):
    for t in transcriptions["chunks"]:
        t_time_start = t["timestamp"][0]
        t_time_end = t["timestamp"][1]
        best_overlap_score = 0.0
        for s, speaker in diarizations.speaker_diarization:
            d_time_start = s.start
            d_time_end = s.end
            curr_score = calc_overlap(d_time_start, d_time_end, t_time_start, t_time_end)
            if curr_score > best_overlap_score:
                print(t['text'])
                print(d_time_start, d_time_end, t_time_start, t_time_end)
                print(speaker)
                t["speaker"] = speaker
                best_overlap_score = curr_score


    unmerged = transcriptions["chunks"]
    merged = []

    last = len(unmerged)
    i = 0
    j = 1
    while(i < last and j < last):
        #print(unmerged[i])
        #print(unmerged[j])
        if unmerged[i].get("speaker") == unmerged[j].get("speaker") and i != j:
            j += 1
        elif j - i > 1:
            start_time = unmerged[i]["timestamp"][0]
            speaker_str = ""
            speaker = unmerged[i]["speaker"]
            while (i < j - 1):
                # merge everything starting at j until i
                speaker_str += unmerged[i]["text"] + " "
                i += 1
                print(speaker_str)
                print("added with ", unmerged[i]["text"])
            end_time = unmerged[i]["timestamp"][0]
            turn = {'timestamp': (start_time, end_time), 'text': speaker_str, 'speaker': speaker}
            merged.append(turn)
        else:
            # this is when all the speakers between i and j are different
            merged.append(unmerged[i])
            j += 1
            i += 1
    merged.append(unmerged[last - 1])
    return merged


def summarize_chunk(transcript):
    structure = generate_chunk_prompt(transcript=transcript)
    summary = query_gemma(structure)
    print(summary)
    return summary


def generate_final_summary(chunks):
    structure = generate_final_prompt(chunks=chunks)
    summary = query_gemma(structure)
    print(summary)
    return summary







