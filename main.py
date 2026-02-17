from downloadRes.download import download
from processing.registry import refinement_process
from clean_cache import clear_existing_data
# from summarization.gemini_summarizer import ReelSummarizer
from summarization.reel_summarizer import ReelSummarizer
import time

import os
import certifi

os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()   

if __name__ == "__main__":
    start = time.perf_counter()

    # url = "https://www.instagram.com/reel/DUInVzxkqiq/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ=="
    url = input("Enter the Instagram Post or Reel URL: ").strip()

    clear_existing_data()
    download(url)
    refinement_process()

    # Summarization
    TRANSCRIPT = "./artifacts/transcription.txt"
    FRAMES = "./artifacts/refined_frames.json"
    META = "./ingestion/metadata.json"

    # Choose provider and model
    # Options: 'gemini', 'openai', 'claude', 'ollama'
    # Model Name: Optional (pass None to use default in config)
    PROVIDER = "ollama"
    MODEL = "gpt-oss:120b-cloud"

    try:
        summarizer = ReelSummarizer(provider=PROVIDER, model_name=MODEL)
        
        result = summarizer.generate_summary(TRANSCRIPT, FRAMES, META)
        
        print("\n--- 📝 GENERATED SUMMARY SAMPLE ---")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
    clear_existing_data()

    for i in range(1000000):
        pass
    end = time.perf_counter()
    print(f"Total execution time: {end - start:.2f} seconds")