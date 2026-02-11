import os
import json
from processing.audio_transcription.transcribe import transcribe_audio
from processing.video_frame_extraction.mp4_specialization import extract_frames
from processing.video_transcription.frame_analyzer import analyze_frames_directory

def refinement_process():

    print("----- Starting Refinement Process -----")

    print("Transcribing audio...")
    transcription = transcribe_audio()

    os.makedirs('artifacts', exist_ok=True)
    
    with open('artifacts/transcription.txt','w') as f:
        f.write(transcription)
    print("Audio Transcription saved to artifacts/transcription.txt")
    
    
    print("Extracting video frames on significant changes...")
    video_path = 'ingestion/video.mp4'
    output_folder = 'artifacts/video_frames'

    extract_frames(
        video_path=video_path,
        output_folder=output_folder,
        hist_threshold=0.28,       # ← tune this first (start 0.22–0.35)
        ssim_threshold=0.89,       # ← tune second (0.86–0.92)
        min_frame_interval=8       # adjust based on fps (8–15 common)
    )
    # extract_frames(video_path, output_folder, sensitivity_threshold=15)
    print(f"Video frames extracted to {output_folder}")

    print("Transcribing Video Frames...")
    FRAMES_DIR = "./artifacts/video_frames"
    OUTPUT_JSON = "./artifacts/refined_frames.json"

    # You can override settings here
    results = analyze_frames_directory(
        frames_dir=FRAMES_DIR,
        output_json_path=OUTPUT_JSON,
        conf_threshold=0.50,
        caption_max_tokens=45,
        caption_num_beams=3      # lower = faster, but slightly worse captions
    )

    # Optional: print first few results
    if results:
        print("\nSample results (first 2):")
        for item in results[:2]:
            print(json.dumps(item, indent=2))
    print(f"Frame analysis results saved to {OUTPUT_JSON}")
    print("--- Refinement process completed. ---")