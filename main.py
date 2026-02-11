from downloadRes.download import download
from processing.registry import refinement_process
from clean_cache import clear_existing_data

if __name__ == "__main__":
    # url = "https://www.instagram.com/reel/DUInVzxkqiq/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ=="
    url = input("Enter the Instagram Post or Reel URL: ").strip()

    clear_existing_data()
    download(url)
    refinement_process()