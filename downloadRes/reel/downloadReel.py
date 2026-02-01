# import os
from downloadRes.reel.metadata import extract_metadata
from downloadRes.reel.video import downloadVideo
from downloadRes.reel.audio import downloadAudio

downloadedReelName = "resources/reel.mp4"
def DownloadReel(url):
    extracted_video_url = extract_metadata(url)
    downloadVideo(extracted_video_url, downloadedReelName)
    downloadAudio(downloadedReelName)