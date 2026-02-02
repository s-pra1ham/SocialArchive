import re
import os

cols = os.get_terminal_size().columns

def get_instagram_content_type(url):
    # Extract the path part after instagram.com
    match = re.search(r'instagram\.com/([^/]+)/([^/]+)/', url)
    if not match:
        return "Unknown"
    
    # The second group is the content type (post or reel)
    content_type = match.group(1)
    return content_type.capitalize()  # Returns "Post" or "Reel"

def download(url):
    content_type = get_instagram_content_type(url)
    print("\n" + "="*cols)
    print(" " * ((cols - len(f"Downloading {content_type} Resources")) // 2) + f"Downloading {content_type} Resources")
    print("="*cols + "\n")
    if content_type == "Post":
        from downloadRes.post.downloadPosts import extract_metadata
        extract_metadata(url)
    elif content_type == "Reel":
        from downloadRes.reel.downloadReel import DownloadReel as download_reel_resources
        download_reel_resources(url)
    else:
        print("Unsupported content type or invalid URL.")
    print("="*cols + "\n")