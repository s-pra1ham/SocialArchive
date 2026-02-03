import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# 1. Load a pre-trained multi-modal model (e.g., Salesforce's BLIP)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

# 2. Load the image
img_url = 'artifacts/video_frames/frame_10.jpg'  # Example frame path
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

# 3. Process the image and generate a caption
# unconditional caption generation
inputs = processor(raw_image, return_tensors="pt")
out = model.generate(**inputs)
summary = processor.decode(out[0], skip_special_tokens=True)

print(f"Detailed Summary: {summary}")
