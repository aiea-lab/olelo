import whisper
from pathlib import Path
import sys
from moviepy import VideoFileClip

def convert_to_wav(videopath):
    videofile = VideoFileClip(videopath)
    videopath = videopath.replace("./files_to_transcribe/", "")[:-4]    # [:-4] if file extensions == 3 characters
    videofile.audio.write_audiofile(str(videopath) + ".wav", codec="pcm_s16le", logger=None)
    videofile.close()
    return str(videopath) + ".wav"

def transcribe(modeltype="base"):
    model = whisper.load_model(modeltype)   # accepted values: tiny, base, small, medium, large, turbo
    for filepath in (Path("./files_to_transcribe")).iterdir():  # accepted file types in README
        filepath = Path(convert_to_wav("./files_to_transcribe/" + filepath.name))
        result = model.transcribe(filepath.name)
        with open("transcriptions.txt", "a", encoding="utf-8") as file: # adds result to end of file
            file.write(f"{modeltype}: {filepath.name} result:" + result["text"] + "\n")
            print(f"Wrote {filepath.name}.")
            # Format: "modeltype filename result: blah meeting stuff blah \n"

transcribe(sys.argv[1])