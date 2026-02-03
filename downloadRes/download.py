import re
import os

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
    print(f"----- Downloadeing {content_type} Ingestion -----")
    if content_type == "Post":
        print("Logic not implemented for Post downloads yet.")
        # from downloadRes.post.downloadPosts import extract_metadata
        # extract_metadata(url)
    elif content_type == "Reel":
        from downloadRes.reel.downloadReel import DownloadReel as download_reel_ingestion
        download_reel_ingestion(url)
    else:
        print("Unsupported content type or invalid URL.")
    print("---")