# frame_analyzer.py
"""
Module for analyzing extracted video frames:
- Object detection (YOLO)
- Image captioning (BLIP)
- OCR (EasyOCR)
"""

import os
import json
import cv2
from PIL import Image
import torch
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration
import easyocr


def load_models(
    yolo_model_name="yolov10n.pt",
    blip_model_name="Salesforce/blip-image-captioning-base",
    ocr_languages=['en']
):
    """
    Load all required models once at startup.
    Returns tuple: (yolo_model, blip_processor, blip_model, ocr_reader)
    """
    print("Loading models... (this may take a minute the first time)")

    # YOLO object detection
    yolo = YOLO(yolo_model_name)

    # BLIP image captioning
    processor = BlipProcessor.from_pretrained(blip_model_name)
    model = BlipForConditionalGeneration.from_pretrained(blip_model_name)
    model.to("cpu")  # or "cuda" if available later
    model.eval()

    # EasyOCR
    ocr = easyocr.Reader(ocr_languages, gpu=False)  # gpu=False → force CPU

    print("All models loaded.")
    return yolo, processor, model, ocr


def analyze_single_frame(
    frame_path,
    yolo_model,
    blip_processor,
    blip_model,
    ocr_reader,
    conf_threshold=0.50,
    caption_max_tokens=40,
    caption_num_beams=4
):
    """
    Analyze one frame: detection + caption + OCR
    Returns dict with timestamp (derived), objects, caption, ocr_text
    """
    # Load image
    image_bgr = cv2.imread(frame_path)
    if image_bgr is None:
        raise ValueError(f"Could not load image: {frame_path}")

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)

    # Derive timestamp from filename (assumes format frame_123.jpg → seconds)
    try:
        seconds = int(os.path.splitext(os.path.basename(frame_path))[0].split('_')[1])
        timestamp = f"{seconds // 60:02d}:{seconds % 60:02d}"
    except (IndexError, ValueError):
        timestamp = "??:??"  # fallback

    # 1. Object Detection (YOLO)
    results = yolo_model(frame_path, verbose=False)
    objects = []
    for result in results:
        for box in result.boxes:
            conf = float(box.conf)
            if conf >= conf_threshold:
                class_name = result.names[int(box.cls)]
                objects.append(f"{class_name} ({conf:.2f})")

    # 2. Image Captioning (BLIP)
    inputs = blip_processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        generated_ids = blip_model.generate(
            **inputs,
            max_new_tokens=caption_max_tokens,
            num_beams=caption_num_beams,
            do_sample=False
        )
    caption = blip_processor.decode(generated_ids[0], skip_special_tokens=True)

    # 3. OCR
    ocr_results = ocr_reader.readtext(image_bgr, detail=0, paragraph=False)
    ocr_text = " ".join([t for t in ocr_results if t.strip()])

    return {
        "frame_file": os.path.basename(frame_path),
        "timestamp": timestamp,
        "objects": ", ".join(objects) if objects else "None detected",
        "caption": caption.strip(),
        "ocr_text": ocr_text.strip() if ocr_text.strip() else "No text detected"
    }


def analyze_frames_directory(
    frames_dir,
    output_json_path,
    conf_threshold=0.50,
    caption_max_tokens=40,
    caption_num_beams=4
):
    """
    Main function: analyze all .jpg / .png frames in a directory
    Saves results to JSON file
    Returns list of frame analysis dicts
    """
    yolo, processor, model, ocr = load_models()

    if not os.path.isdir(frames_dir):
        raise NotADirectoryError(f"Directory not found: {frames_dir}")

    frame_files = [
        f for f in os.listdir(frames_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    if not frame_files:
        print("No image files found in directory.")
        return []

    refined_data = []

    print(f"Found {len(frame_files)} frames. Starting analysis...\n")

    for i, fname in enumerate(frame_files, 1):
        frame_path = os.path.join(frames_dir, fname)
        print(f"[{i}/{len(frame_files)}] Processing {fname} ...")

        try:
            result = analyze_single_frame(
                frame_path,
                yolo,
                processor,
                model,
                ocr,
                conf_threshold=conf_threshold,
                caption_max_tokens=caption_max_tokens,
                caption_num_beams=caption_num_beams
            )
            refined_data.append(result)
            print(f"  → {result['timestamp']} | {result['caption'][:60]}...")
        except Exception as e:
            print(f"  → Error on {fname}: {e}")

    # Save results
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(refined_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Results saved to: {output_json_path}")
    print(f"Processed {len(refined_data)} / {len(frame_files)} frames successfully.")

    return refined_data


# ────────────────────────────────────────────────
if __name__ == "__main__":
    # For standalone testing / quick runs

    FRAMES_DIR = "./artifacts/video_frames"
    OUTPUT_JSON = "./artifacts/refined_frames.json"

    # You can override settings here
    results = analyze_frames_directory(
        frames_dir=FRAMES_DIR,
        output_json_path=OUTPUT_JSON,
        conf_threshold=0.50,
        caption_max_tokens=45,
        caption_num_beams=3      # lower = faster, but slightly worse captions
    )

    # Optional: print first few results
    if results:
        print("\nSample results (first 2):")
        for item in results[:2]:
            print(json.dumps(item, indent=2))