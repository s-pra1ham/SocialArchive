from moviepy import VideoFileClip
import os

def downloadAudio(input_path):
# Define input and output paths
    input_file = input_path
    output_folder = "resources"
    os.makedirs(output_folder, exist_ok=True)

    # Extract audio and save as MP3
    video_clip = VideoFileClip(input_file)
    audio_clip = video_clip.audio
    output_file = os.path.join(output_folder, "output_audio.mp3")
    audio_clip.write_audiofile(output_file, codec='mp3', bitrate='320k')

    # Close clips to free resources
    audio_clip.close()
    video_clip.close()

    print(f"Audio successfully extracted to {output_file}")