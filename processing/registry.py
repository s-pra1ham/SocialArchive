import os
from processing.audio_transcription.transcribe import transcribe_audio
from processing.video_frame_extraction.mp4_specialization import extract_frames

def refinement_process():

    print("----- Starting Refinement Process -----")

    print("Transcribing audio...")
    transcription = transcribe_audio()

    os.makedirs('artifacts', exist_ok=True)
    
    with open('artifacts/transcription.txt','w') as f:
        f.write(transcription)
    print("Audio Transcription saved to artifacts/transcription.txt")
    
    
    print("=Extracting video frames on significant changes...")
    video_path = 'ingestion/video.mp4'
    output_folder = 'artifacts/video_frames'
    extract_frames(video_path, output_folder, threshold=15000)
    print(f"Video frames extracted to {output_folder}")
    print("--- Refinement process completed. ---")