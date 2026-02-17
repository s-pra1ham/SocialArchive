import os
import json
import time
from .llm_config import get_llm_client

class ReelSummarizer:
    def __init__(self, provider="gemini", model_name=None):
        """
        Initialize the summarizer with a specific LLM provider.
        
        :param provider: 'gemini', 'openai', 'claude', 'ollama'
        :param model_name: Optional specific model name (e.g. 'gpt-4-turbo').
                           If None, uses defaults from config.
        """
        print(f"🔌 Initializing {provider.upper()} client...")
        self.llm = get_llm_client(provider, model_name)

    def _read_file_content(self, path):
        """Helper to safely read file content."""
        if not os.path.exists(path):
            print(f"⚠️ Warning: File not found at {path}")
            return "Data not available."
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.endswith('.json'):
                    return json.load(f)
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    def _next_reel_filename(self, storage_dir="./storage", prefix="summary", ext=".md"):
        """Return next available filename."""
        try:
            os.makedirs(storage_dir, exist_ok=True)
            i = 1
            while True:
                candidate = os.path.join(storage_dir, f"{prefix}_{i}{ext}")
                if not os.path.exists(candidate):
                    return candidate
                i += 1
        except Exception:
            ts = int(time.time())
            return os.path.join(storage_dir, f"{prefix}_{ts}{ext}")

    def generate_summary(self, transcription_path, frames_path, metadata_path):
        """
        Reads data files and generates a summary using the configured LLM.
        """
        # 1. Load Data
        print(f"📂 Loading data files...")
        transcript = self._read_file_content(transcription_path)
        frames_data = self._read_file_content(frames_path)
        metadata = self._read_file_content(metadata_path)

        # 2. Construct Prompt
        # Standardized prompt for all models
        prompt = f"""
        You are an expert Content Strategist and Video Analyst. 
        Your goal is not just to describe *what* happens, but to explain *why* this video exists and what value it provides to the viewer.

        --- INPUT DATA ---
        
        1. CONTEXT (Metadata):
        {json.dumps(metadata, indent=2) if isinstance(metadata, dict) else metadata}

        2. AUDIO (Spoken Words):
        {transcript}

        3. VISUALS (Frame Analysis):
        {json.dumps(frames_data, indent=2) if isinstance(frames_data, list) else frames_data}
        
        --- END INPUT DATA ---

        ### ANALYSIS INSTRUCTIONS:

        **STEP 1: IDENTIFY THE "HOOK" & PURPOSE**
        - Look at the metadata (captions/hashtags) and the first 5 seconds of audio/visuals.
        - Determine the primary category: Is this Educational? A Travel Vlog? Comedy? A Product Review? Motivation?
        - *Crucial*: Answer the question: "If I shared this video with a friend, what would I say it is about?" (e.g., "It's a guy climbing an active volcano in Guatemala," not "It's a video of a man walking on rocks.")

        **STEP 2: SYNTHESIZE THE NARRATIVE**
        - Do NOT list frames chronologically unless necessary for a tutorial.
        - Combine visual cues with spoken words to tell the story.
        - If the speaker says "This is dangerous," mention that the visual shows lava or a steep drop.

        **STEP 3: GENERATE OUTPUT (Markdown Format)**
        
        Produce the output strictly in this structure:

        # [Catchy Title of the Video Idea]

        ## 🎯 The Core Purpose (TL;DR)
        *A 1-2 sentence statement capturing the essence. Example: "A travel vlog documenting a high-stakes hike up Volcán de Fuego in Guatemala to see active lava eruptions."*

        ## 📝 Key Takeaways / Highlights
        - [Bullet point of major event or tip]
        - [Bullet point of major event or tip]
        - [Bullet point of major event or tip]

        ## 📽️ Narrative Summary
        *[A paragraph synthesizing the video content. Focus on the 'vibe', the location, and the main action. Mention specific visual details only if they support the main point.]*
        """

        # 3. Generate Content
        try:
            print("✨ Sending prompt to LLM...")
            start_time = time.time()
            
            # This calls the .generate() method from our wrapper in config.py
            # regardless of which provider is used.
            response_text = self.llm.generate(prompt)
            
            elapsed = time.time() - start_time
            print(f"✅ Summary generated in {elapsed:.2f} seconds.")
            
            out_path = self._next_reel_filename()
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(response_text)
            print(f"💾 Summary saved to {out_path}")
            return response_text

        except Exception as e:
            return f"❌ LLM Error: {str(e)}"

# --- Main block for testing ---
if __name__ == "__main__":
    # 1. Setup paths (Make sure these files exist or code will return "Data not available")
    TRANSCRIPT = "./artifacts/transcription.txt"
    FRAMES = "./artifacts/refined_frames.json"
    META = "./ingestion/metadata.json"

    # 2. Choose your fighter
    # Options: 'gemini', 'openai', 'claude', 'ollama'
    # Model Name: Optional (pass None to use default in config)
    
    # PROVIDER = "gemini" 
    # MODEL = "gemini-1.5-flash" 
    
    # Example for Ollama:
    PROVIDER = "ollama"
    MODEL = "gpt-oss:120b-cloud"

    try:
        summarizer = ReelSummarizer(provider=PROVIDER, model_name=MODEL)
        
        result = summarizer.generate_summary(TRANSCRIPT, FRAMES, META)
        
        print("\n--- 📝 GENERATED SUMMARY SAMPLE ---")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")