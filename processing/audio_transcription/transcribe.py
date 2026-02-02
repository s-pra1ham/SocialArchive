import whisper
import os

def transcribe_audio():
    # Verify file exists
    file_path = "ingestion/audio.mp3"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found. Check the path.")

    # Load model
    model = whisper.load_model("base")

    # Transcribe with hallucination-reducing settings
    result = model.transcribe(
        file_path,
        language="en",  # Set if known, otherwise remove for auto-detect
        condition_on_previous_text=False,  # Reduces hallucinations
        no_speech_threshold=0.6,
        logprob_threshold=-1.0,
        fp16=False
    )
    return result["text"]

if __name__ == "__main__":
    try:
        print(transcribe_audio())
    except Exception as e:
        print(f"Error: {e}")   