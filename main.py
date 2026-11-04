from openai import OpenAI
import os

client = OpenAI()

#input audio file, any audio file can be used
audio_path = input('Enter the path to your audio file: ').strip()


#check if file exists
if not os.path.isfile(audio_path):
    print("Error: File '{audio_path}' not found.")
    exit(1)


#opening audio file
with open(audio_path, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        language="en"
    )


#getting text
text = transcription.text

output_file = "transcription.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(text)

print(f'Transcription saved to {output_file}')







