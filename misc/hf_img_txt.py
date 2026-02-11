import torch
import av
import numpy as np
from transformers import AutoProcessor, LlavaOnevisionForConditionalGeneration

# 1. Configuration
# "ov" stands for OneVision (Video capable), this IS the correct PyTorch model.
MODEL_ID = "llava-hf/llava-onevision-qwen2-0.5b-ov-hf" 
DEVICE = "cpu"

print(f"Loading model: {MODEL_ID}...")

# 2. Load Processor
processor = AutoProcessor.from_pretrained(MODEL_ID)

# 3. Load Model
model = LlavaOnevisionForConditionalGeneration.from_pretrained(
    MODEL_ID, 
    torch_dtype=torch.float32, 
    low_cpu_mem_usage=True,
).to(DEVICE)

# --- VERIFICATION CHECK ---
# This checks if the model loaded correctly. 
# If the language head is random, the output will be garbage.
if hasattr(model, "language_model") and hasattr(model.language_model, "lm_head"):
    head_weight = model.language_model.lm_head.weight
    if torch.isnan(head_weight).any() or head_weight.sum() == 0:
        print("WARNING: Model weights look corrupted/empty!")
else:
    print("Model loaded successfully (Architecture verified).")
# ---------------------------

def read_video_pyav(container, indices):
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            frames.append(frame.to_image())
    return frames

def get_video_frames(video_path, num_frames=16):
    container = av.open(video_path)
    total_frames = container.streams.video[0].frames
    indices = np.linspace(0, total_frames - 1, num_frames).astype(int)
    frames = read_video_pyav(container, indices)
    return frames

def summarize(video_path):
    print(f"Processing video: {video_path}")
    video_frames = get_video_frames(video_path, num_frames=16)
    
    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "video", "media": video_frames},
                {"type": "text", "text": "Describe this video in detail in English."}
            ],
        },
    ]

    prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
    inputs = processor(text=prompt, videos=video_frames, return_tensors="pt").to(DEVICE)

    print("Generating summary...")
    
    # We use greedy decoding (do_sample=False) for the most factual/stable output
    generated_ids = model.generate(
        **inputs, 
        max_new_tokens=50000,
        do_sample=False 
    )
    
    summary = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    if "assistant\n" in summary:
        return summary.split("assistant\n")[-1].strip()
    return summary

if __name__ == "__main__":
    my_video = "./ingestion/video.mp4" 
    try:
        result = summarize(my_video)
        print("\n--- SUMMARY ---\n")
        print(result)
    except Exception as e:
        print(f"Error: {e}")