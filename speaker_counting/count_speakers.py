import os
import time
import requests

BASE_URL = "https://api.assemblyai.com"


def count_speakers(audio_path, api_key=None):
    if api_key is None:
        api_key = os.environ["ASSEMBLYAI_API_KEY"]
    headers = {"authorization": api_key}

    with open(audio_path, "rb") as f:
        upload = requests.post(BASE_URL + "/v2/upload", headers=headers, data=f)
    upload.raise_for_status()
    audio_url = upload.json()["upload_url"]

    data = {
        "audio_url": audio_url,
        "speech_models": ["universal-3-pro", "universal-2"],
        "language_detection": True,
        "speaker_labels": True,
    }
    resp = requests.post(BASE_URL + "/v2/transcript", json=data, headers=headers)
    resp.raise_for_status()
    transcript_id = resp.json()["id"]

    while True:
        result = requests.get(BASE_URL + "/v2/transcript/" + transcript_id, headers=headers).json()
        if result["status"] == "completed":
            break
        if result["status"] == "error":
            raise RuntimeError(result["error"])
        time.sleep(5)

    speakers = {u["speaker"] for u in result["utterances"]}
    return len(speakers)


if __name__ == "__main__":
    meetings = ["IS1001d", "IS1002d", "IS1001c", "ES2010a", "ES2013a",
                "ES2005a", "ES2012d", "TS3012a", "TS3010a", "TS3007b"]
    TRUE_COUNT = 4
    for m in meetings:
        path = "/data/amicorpus/" + m + "/audio/" + m + ".Mix-Headset.wav"
        try:
            found = count_speakers(path)
            print(m, "API says", found, "| true", TRUE_COUNT, "| match:", found == TRUE_COUNT, flush=True)
        except Exception as e:
            print(m, "FAILED:", e, flush=True)
