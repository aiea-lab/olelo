import whisper
from pathlib import Path
import sys
from moviepy import VideoFileClip

def convert_to_wav(videopath):
    videofile = VideoFileClip(videopath)   # [:-4] only if file extensions == 3 characters
    videofile.audio.write_audiofile(str(videopath)[:-4] + ".wav", codec="pcm_s16le", logger=None)
    Path("./files_to_transcribe/" + str(videopath)).unlink(missing_ok=True)
    videofile.close()
    return videofile.filename

def transcribe(modeltype="base"):
    model = whisper.load_model(modeltype)   # accepted values: tiny, base, small, medium, large, turbo
    for filepath in (Path("./files_to_transcribe")).iterdir():  # accepted file types in README

        # Uncomment this line to convert everything to wav:
        # filepath = Path(convert_to_wav("./files_to_transcribe/" + filepath.name))

        result = model.transcribe("./files_to_transcribe/" + filepath.name)
        with open("transcriptions.txt", "a", encoding="utf-8") as file: # adds result to end of file
            file.write(f"{modeltype}: {filepath.name} result:" + result["text"] + "\n")
            # Format: "modeltype filename result: blah meeting stuff blah \n"
            print(f"Wrote {filepath.name}.")
            

transcribe(sys.argv[1])