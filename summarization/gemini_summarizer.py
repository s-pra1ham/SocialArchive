import os
import json
import time
from .gemini_config import configure_gemini, get_gemini_model

# NOTE: If running this file directly as __main__, you might need to fix imports
# strictly for the test block at the bottom.

class ReelSummarizer:
    def __init__(self, api_key=None, model_name="gemini-1.5-flash"):
        """
        Initialize the summarizer.
        :param api_key: Optional. If None, looks for env variable.
        :param model_name: 'gemini-1.5-flash' (faster) or 'gemini-1.5-pro' (smarter).
        """
        configure_gemini(api_key)
        self.model = get_gemini_model(model_name)

    def _read_file_content(self, path):
        """Helper to safely read file content."""
        if not os.path.exists(path):
            print(f"⚠️ Warning: File not found at {path}")
            return "Data not available."
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    return json.load(f) # Return dict/list
                return f.read() # Return string
        except Exception as e:
            return f"Error reading file: {e}"

    def _next_reel_filename(self, storage_dir="./storage", prefix="reel", ext=".txt"):
        """Return next available filename like 'reel1.txt', 'reel2.txt', ..."""
        try:
            os.makedirs(storage_dir, exist_ok=True)
            i = 1
            while True:
                candidate = os.path.join(storage_dir, f"{prefix}{i}{ext}")
                if not os.path.exists(candidate):
                    return candidate
                i += 1
        except Exception:
            # Fallback to a timestamped file if anything unexpected happens
            ts = int(time.time())
            return os.path.join(storage_dir, f"{prefix}_{ts}{ext}")

    def generate_summary(self, transcription_path, frames_path, metadata_path):
        """
        Reads the three data files and generates a detailed summary using Gemini.
        """
        # 1. Load Data
        print(f"📂 Loading data from {frames_path}...")
        transcript = self._read_file_content(transcription_path)
        frames_data = self._read_file_content(frames_path)
        metadata = self._read_file_content(metadata_path)

        # 2. Construct Prompt
        # Gemini handles large contexts well, so we can dump the JSONs directly.
        prompt = f"""
        You are an expert video analyst AI. I have processed an Instagram Reel into three data streams.
        Synthesize these into a highly detailed narrative summary.

        --- START DATA ---
        
        1. METADATA (Context):
        {json.dumps(metadata, indent=2)}

        2. AUDIO TRANSCRIPTION (Spoken Content):
        {transcript}

        3. VISUAL ANALYSIS (Frame-by-Frame Description):
        {json.dumps(frames_data, indent=2)}
        
        --- END DATA ---

        ### INSTRUCTIONS:
        1. **Correlate**: Match what is seen in the visual analysis with what is said in the transcription.
        2. **Narrate**: Don't just list facts. Write a summary that describes the flow of the video.
        3. **Detail**: Include specific visual details (colors, objects, text on screen) mentioned in the visual data.
        4. **Context**: Use the metadata to explain the 'why' or the 'vibe' of the video.

        Output the summary in clear, professional markdown.
        """

        # 3. Generate Content
        try:
            print("✨ Sending data to Gemini...")
            start_time = time.time()
            
            response = self.model.generate_content(prompt)
            
            elapsed = time.time() - start_time
            print(f"✅ Summary generated in {elapsed:.2f} seconds.")
            
            out_path = self._next_reel_filename()
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Summary saved to {out_path}")
            return response.text

        except Exception as e:
            return f"❌ Gemini API Error: {str(e)}"

# --- Main block for testing ---
if __name__ == "__main__":
    # 1. Dummy Data Creation for Testing
    print("--- 🧪 STARTING TEST MODE ---")
    

    # 2. Initialize Logic
    # We use a try/except block here to handle the import when running as a script vs module
    try:
        # If running as script, we need to hack the import or just rely on the class above
        # For this test, we assume the class is defined above.
        
        # YOU MUST SET YOUR API KEY HERE OR IN ENV VARS FOR TEST TO WORK
        # os.environ["GEMINI_API_KEY"] = "AIzaSy..." 
        
        summarizer = ReelSummarizer(model_name="gemini-2.5-flash")
        
        summary = summarizer.generate_summary(
            "./artifacts/transcription.txt",
            "./artifacts/refined_frames.json",
            "./ingestion/metadata.json"
        )
        
        print("\n--- 📝 GENERATED SUMMARY ---")
        print(summary)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("Tip: Did you set your GEMINI_API_KEY?")
