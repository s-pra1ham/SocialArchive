import instaloader
import json
import re

def extract_metadata(url):
    def extract_shortcode(url):
        pattern = r'instagram\.com/(?:[^/]+/)?(?:reel|p)/([^/?]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    L = instaloader.Instaloader()
    shortcode = extract_shortcode(url)  # From URL
    post = instaloader.Post.from_shortcode(L.context, shortcode)

    # Save metadata to JSON
    metadata = {
        "caption": post.caption,
        "likes": post.likes,
        "views": post.video_view_count if post.is_video else None,
        "date": str(post.date_utc),
        "shortcode": shortcode,
        "video_url": post.video_url
    }

    with open(f"resources/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return post.video_url   