# frame_analyzer.py
"""
Module for analyzing extracted video frames on CPU (optimized for Intel i7 + Iris Xe)
- Object detection (YOLO nano)
- Image captioning (BLIP base)
- OCR (EasyOCR)
"""

import os
import json
import cv2
from PIL import Image
import torch
from concurrent.futures import ProcessPoolExecutor, as_completed
from ultralytics import YOLO
from transformers import BlipProcessor, BlipForConditionalGeneration
import easyocr


def load_models(
    yolo_model_name="yolov10n.pt",                    # nano = fastest
    blip_model_name="Salesforce/blip-image-captioning-base",
    ocr_languages=['en']
):
    print("Loading models (CPU optimized)...")

    yolo = YOLO(yolo_model_name)

    processor = BlipProcessor.from_pretrained(blip_model_name)
    model = BlipForConditionalGeneration.from_pretrained(blip_model_name)
    model.eval()

    # Try to use reduced precision for speed (Iris Xe / CPU friendly)
    try:
        model = model.to(torch.bfloat16)
        print("Using bfloat16 precision")
    except:
        try:
            model = model.to(torch.float16)
            print("Using float16 precision")
        except:
            print("Using full float32 precision")

    ocr = easyocr.Reader(ocr_languages, gpu=False)

    print("Models loaded.")
    return yolo, processor, model, ocr


def analyze_single_frame(args):
    frame_path, conf_threshold, caption_max_tokens, caption_num_beams = args

    image_bgr = cv2.imread(frame_path)
    if image_bgr is None:
        return {"frame_file": os.path.basename(frame_path), "error": "Image load failed"}

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)

    # Timestamp from filename (frame_XXX.jpg → seconds)
    try:
        seconds = int(os.path.splitext(os.path.basename(frame_path))[0].split('_')[1])
        timestamp = f"{seconds // 60:02d}:{seconds % 60:02d}"
    except:
        timestamp = "??:??"

    # YOLO - reload lightweight model per process (avoids pickling issues)
    yolo = YOLO("yolov10n.pt")
    results = yolo(frame_path, verbose=False)
    objects = []
    for result in results:
        for box in result.boxes:
            conf = float(box.conf)
            if conf >= conf_threshold:
                class_name = result.names[int(box.cls)]
                objects.append(f"{class_name} ({conf:.2f})")

    # BLIP - reload per process
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    model.eval()
    try:
        model = model.to(torch.bfloat16 if torch.bfloat16 in model.parameters().__next__().dtype else torch.float32)
    except:
        pass

    inputs = processor(images=pil_image, return_tensors="pt")
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=caption_max_tokens,
            num_beams=caption_num_beams,
            do_sample=False
        )
    caption = processor.decode(generated_ids[0], skip_special_tokens=True).strip()

    # OCR
    ocr = easyocr.Reader(['en'], gpu=False)
    ocr_results = ocr.readtext(image_bgr, detail=0, paragraph=False)
    ocr_text = " ".join([t for t in ocr_results if t.strip()])

    return {
        "frame_file": os.path.basename(frame_path),
        "timestamp": timestamp,
        "objects": ", ".join(objects) if objects else "None detected",
        "caption": caption,
        "ocr_text": ocr_text if ocr_text.strip() else "No text detected"
    }


def analyze_frames_directory(
    frames_dir,
    output_json_path,
    conf_threshold=0.50,
    caption_max_tokens=35,       # lower = faster
    caption_num_beams=3,         # lower = faster, acceptable quality
    num_workers=6                # good for i7-1185G7 (4 cores / 8 threads)
):
    if not os.path.isdir(frames_dir):
        raise NotADirectoryError(f"Directory not found: {frames_dir}")

    frame_files = [f for f in os.listdir(frames_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not frame_files:
        print("No image files found.")
        return []

    frame_paths = [os.path.join(frames_dir, f) for f in frame_files]

    print(f"Found {len(frame_paths)} frames. Using {num_workers} parallel workers (CPU).")

    refined_data = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(
                analyze_single_frame,
                (path, conf_threshold, caption_max_tokens, caption_num_beams)
            )
            for path in frame_paths
        ]

        for future in as_completed(futures):
            try:
                result = future.result()
                refined_data.append(result)
                print(f"Processed {result['frame_file']}  →  {result['caption'][:50]}...")
            except Exception as e:
                print(f"Error processing frame: {e}")

    refined_data.sort(key=lambda x: x.get('timestamp', '00:00'))

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(refined_data, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Results saved to: {output_json_path}")
    print(f"Successfully processed {len(refined_data)} / {len(frame_paths)} frames.")

    return refined_data


if __name__ == "__main__":
    FRAMES_DIR = "./artifacts/video_frames"
    OUTPUT_JSON = "./artifacts/refined_frames.json"

    results = analyze_frames_directory(
        frames_dir=FRAMES_DIR,
        output_json_path=OUTPUT_JSON,
        caption_max_tokens=35,
        caption_num_beams=3,
        num_workers=6
    )