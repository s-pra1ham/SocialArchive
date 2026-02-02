from downloadRes.download import download
from processing.registry import refinement_process

if __name__ == "__main__":
    # url = "https://www.instagram.com/reel/DUInVzxkqiq/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ=="
    url = input("Enter the Instagram Post or Reel URL: ").strip()
    download(url)
    refinement_process()