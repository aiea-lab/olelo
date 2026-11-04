# Speaker counting

count_speakers.py has a function, count_speakers(audio_path), that sends an audio file to AssemblyAI and returns the number of speakers it finds.

It reads the API key from the ASSEMBLYAI_API_KEY environment variable. Don't put the key in the code.

I tested it on the headset-mix audio of 10 AMI meetings from the Nautilus PVC. Every AMI meeting has 4 speakers. It got 8 of 10 right. IS1001d came back as 3 speakers and TS3010a as 5. The other 8 meetings came back as 4.
