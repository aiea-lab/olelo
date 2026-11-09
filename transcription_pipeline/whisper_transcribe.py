import whisper
from pathlib import Path
import sys
import os
from moviepy import VideoFileClip

def convert_to_wav(videopath):
    videofile = VideoFileClip(videopath)
    videofile.audio.write_audiofile(str(videopath).with_suffix("") + ".wav", codec="pcm_s16le", logger=None)
    Path("./files_to_transcribe/" + str(videopath)).unlink(missing_ok=True)
    videofile.close()
    return videofile.filename

def transcribe(modeltype, dirpath):
    model = whisper.load_model(modeltype)   # accepted values: tiny, base, small, medium, large, turbo
    for file in os.scandir(dirpath):
        if file.is_file():
            # Uncomment next line to convert all files to wav:
            # filepath = Path(convert_to_wav("./files_to_transcribe/" + filepath.name))
            try: 
                result = model.transcribe(file.path)
                # adds result to end of file
                with open(f"../rawtext_transcriptions/{file.name} transcription.txt", "a", encoding="utf-8") as file:
                    file.write(f"{modeltype}: {file.name} result:" + result["text"] + "\n")
                    # Format: "modeltype filename result: blah meeting stuff blah \n"
                    print(f"Wrote to {file.name}.")
            except: print(f"File {file.name} is not compatible.")  

        elif file.is_dir(): transcribe(modeltype, file)  

modeltype = sys.argv[1] if len(sys.argv) > 1 else "small"
dirpath = "./files_to_transcribe"
transcribe(modeltype, dirpath)