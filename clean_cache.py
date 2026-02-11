def clear_existing_data():
    import shutil
    import os

    # Define paths to clear
    paths_to_clear = [
        'ingestion/audio.mp3',
        'ingestion/metadata.json',
        'ingestion/video.mp4',
        'artifacts/video_frames',
        'artifacts/transcription.txt',
        'artifacts/refined_frames.json'
    ]

    for path in paths_to_clear:
        if os.path.isfile(path):
            os.remove(path)
            print(f"Removed file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"Removed directory and its contents: {path}")