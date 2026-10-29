import whisper
from pathlib import Path
import sys

def transcribe(modeltype="base"):
    model = whisper.load_model(modeltype)   # accepted values: tiny, base, small, medium, large, turbo
    for filepath in Path("./files_to_transcribe"):  # accepted file types in README
        result = model.transcribe(filepath)
        with open("transcriptions.txt", "a", encoding="utf-8") as file: # add result to end of file
            file.write(f"{filepath} result:" + result["text"] + "\n")
            # Format: "filepath result: blah meeting stuff blah \n"

transcribe(sys.argv[1])