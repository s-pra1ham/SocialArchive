import re

def extract_shortcode(url):
    pattern = r'instagram\.com/(?:reel|p)/([^/?]+)'
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid Instagram URL")
    return match.group(1)