from downloadRes.download import download
from processing.registry import refinement_process
from clean_cache import clear_existing_data
from summarization.gemini_summarizer import ReelSummarizer
import time

if __name__ == "__main__":
    start = time.perf_counter()

    # url = "https://www.instagram.com/reel/DUInVzxkqiq/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ=="
    url = input("Enter the Instagram Post or Reel URL: ").strip()

    clear_existing_data()
    download(url)
    refinement_process()
    ReelSummarizer(model_name="gemini-2.5-flash").generate_summary(
        "./artifacts/transcription.txt",
        "./artifacts/refined_frames.json",
        "./ingestion/metadata.json"
    )
    clear_existing_data()

    for i in range(1000000):
        pass
    end = time.perf_counter()
    print(f"Total execution time: {end - start:.2f} seconds")