import os
import json
import ollama
from ollama_manager import initialize_ollama 
# NOTE: If running this file directly as __main__, remove the '.' before ollama_manager import
# or run as a module: python -m your_package.reel_summarizer

class ReelSummarizer:
    def __init__(self, model_name="gpt-oss:120b-cloud  "):
        self.model_name = initialize_ollama(model_name)

    def _read_text(self, path):
        if not os.path.exists(path):
            return "No transcription available."
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_json(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"error": "File corrupted"}

    def generate_detailed_summary(self, transcription_path, frames_path, metadata_path):
        """
        Ingests processed reel data and generates a detailed summary using Ollama.
        """
        # 1. Load Data
        transcript = self._read_text(transcription_path)
        frames_data = self._read_json(frames_path)
        metadata = self._read_json(metadata_path)

        # 2. Construct the Prompt
        # We explicitly label the data sources to help the model distinguish 
        # between what was 'heard' (audio) and what was 'seen' (frames).
        prompt = f"""
        You are an expert video content analyst. I have decoded an Instagram Reel into three raw data streams. 
        Your task is to synthesize these streams into a single, highly detailed summary of the video.

        ### DATA STREAMS:
        
        1. METADATA (Context, Caption, Hashtags):
        {json.dumps(metadata, indent=2)}

        2. AUDIO TRANSCRIPTION (Spoken words):
        {transcript}

        3. VISUAL ANALYSIS (Frame-by-frame details):
        {json.dumps(frames_data, indent=2)}

        ### INSTRUCTIONS:
        - Analyze the correlation between the visual events and the spoken audio.
        - Capture the "vibe" and intent of the video based on the metadata.
        - Provide a comprehensive summary that describes exactly what happens in the video, what is said, and the overall message.
        - Do not leave out small details found in the visual analysis.
        
        ### OUTPUT:
        Provide the response in a structured, very detailed narrative format.
        """

        # 3. Call Ollama
        try:
            print("🧠 Generating summary... (this depends on your GPU/CPU speed)")
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            
            return response['message']['content']

        except Exception as e:
            return f"Error during generation: {str(e)}"

# --- Main block for testing ---
if __name__ == "__main__":
    # Mock data generation for testing purposes
    # In production, you would point these to your actual file paths
    
    # 1. Create dummy files
    with open("dummy_transcription.txt", "w") as f:
        f.write("Hey guys, today I'm showing you how to build a custom keyboard. First, lube the switches.")
    
    with open("dummy_frames.json", "w") as f:
        json.dump([
            {"timestamp": "00:01", "description": "Person holding a mechanical switch"},
            {"timestamp": "00:05", "description": "Close up of applying lube with a brush"},
            {"timestamp": "00:10", "description": "Assembling the keycaps onto the board"}
        ], f)
        
    with open("dummy_metadata.json", "w") as f:
        json.dump({
            "caption": "Thocky goodness! #mechanicalkeyboard #tech",
            "author": "TechUser123"
        }, f)

    # 2. Initialize and Run
    # Note: We change the import for local testing if files are in the same dir
    try:
        from ollama_manager import initialize_ollama
    except ImportError:
        pass # Assuming the class handles import or file structure is different

    summarizer = ReelSummarizer(model_name="gpt-oss:120b-cloud  ")
    
    print("\n--- TEST RUN START ---")
    summary = summarizer.generate_detailed_summary(
        "./artifacts/transction.txt", 
        "./artifacts/refined_frames.json", 
        "./ingestion/metadata.json"
    )
    
    print("\n--- FINAL SUMMARY ---")
    print(summary)

    # Cleanup dummy files
    import os
    os.remove("dummy_transcription.txt")
    os.remove("dummy_frames.json")
    os.remove("dummy_metadata.json")