import os
from downloadRes.reel.downloadReel import DownloadReel as download_reel_resources

cols = os.get_terminal_size().columns
url = "https://www.instagram.com/reel/DRH9-20DB8H/?utm_source=ig_web_copy_link&igsh=NTc4MTIwNjQ2YQ=="

print("\n" + "="*cols)
print(" " * ((cols - len("Downloading Reel Resources")) // 2) + "Downloading Reel Resources")
print("="*cols + "\n")
download_reel_resources(url)
print("="*cols + "\n")