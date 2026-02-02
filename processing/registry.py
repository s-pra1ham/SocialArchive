import os
from processing.audio_transcription.transcribe import transcribe_audio

def refinement_process():
    transcription = transcribe_audio()

    os.makedirs('artifacts', exist_ok=True)
    
    with open('artifacts/transcription.txt','w') as f:
        f.write(transcription)
    print("Audio Transcription saved to artifacts/transcription.txt")
    # print(f"Transcription Result:\n{transcription}")
    print("--- Refinement process completed. ---")