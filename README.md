# SocialArchive

A Python application that downloads Instagram Reels/Posts, extracts frames on scene changes, and analyzes them using computer vision and NLP models.

## Overview

SocialArchive automates the process of:
1. **Downloading** Instagram content (Reels with metadata)
2. **Extracting** keyframes based on structural/scene changes (not facial movements)
3. **Analyzing** frames with:
   - **Object Detection** (YOLO)
   - **Image Captioning** (BLIP)
   - **Optical Character Recognition** (EasyOCR)
4. **Transcribing** audio using OpenAI Whisper

## Project Structure

```
.
├── main.py                           # Entry point
├── requirements.txt                  # Python dependencies
├── clean_cache.py                    # Cache cleanup utility
├── yolov10n.pt                       # YOLO model (not in git)
│
├── downloadRes/                      # Download module
│   ├── download.py                   # Content type detection & routing
│   ├── reel/
│   │   ├── downloadReel.py          # Main reel download orchestrator
│   │   ├── metadata.py              # Extract metadata via instaloader
│   │   ├── video.py                 # Download video file
│   │   └── audio.py                 # Extract audio to MP3
│   └── post/                        # (Stub for future Post support)
│
├── processing/                       # Core analysis pipeline
│   ├── registry.py                  # Orchestrates refinement process
│   ├── audio_transcription/
│   │   └── transcribe.py            # Whisper audio transcription
│   ├── video_frame_extraction/
│   │   ├── mp4_specialization.py    # Smart keyframe extraction
│   │   └── mp4_specialization.py.bak # Backup (older version)
│   └── video_transcription/
│       └── frame_analyzer.py        # YOLO + BLIP + EasyOCR analysis
│
├── misc/                            # Experimental/utility scripts
│   ├── frame_analyzer.py            # Alternative frame analyzer
│   ├── gpu_tester.py                # CPU-optimized parallel processing
│   ├── hf_img_txt.py                # LLaVA OneVision video summarization
│   └── frame_analyzer.py            # Duplicate (for testing)
│
├── ingestion/                       # Input files (not in git)
│   ├── video.mp4
│   ├── audio.mp3
│   └── metadata.json
│
├── artifacts/                       # Output files (not in git)
│   ├── video_frames/                # Extracted keyframes
│   ├── transcription.txt            # Audio transcription
│   ├── refined_frames.json          # Frame analysis results
│   └── example_refined_frames.json  # Example output
│
└── extracted_frames/                # (Legacy/unused)
```

## Installation

### Prerequisites
- Python 3.8+
- Instaloader (for Instagram downloads)
- FFmpeg (for audio extraction)

### Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd SocialArchive
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download YOLO model:
```bash
# The yolov10n.pt model will be auto-downloaded on first run
# Or manually download from: https://github.com/THU-MIG/yolov10
```

## Usage

### Basic Usage

```bash
python main.py
```

Then enter an Instagram Reel or Post URL when prompted:
```
Enter the Instagram Post or Reel URL: https://www.instagram.com/reel/DUInVzxkqiq/...
```

The script will:
1. Clear previous artifacts
2. Download the content
3. Extract audio and metadata
4. Perform refinement analysis
5. Save results to `artifacts/`

### Output Files

After running, check:
- **`artifacts/transcription.txt`** — Full audio transcription
- **`artifacts/video_frames/`** — Keyframes extracted from video
- **`artifacts/refined_frames.json`** — Frame analysis with:
  - Detected objects (via YOLO)
  - Image captions (via BLIP)
  - Extracted text (via EasyOCR)
  - Timestamps

### Example Output

```json
{
  "frame_file": "keyframe_0001_frame_000042.jpg",
  "timestamp": "00:01",
  "objects": "person (0.95), text (0.87)",
  "caption": "A person holding a smartphone displaying text",
  "ocr_text": "Follow us on Instagram @example"
}
```

## Configuration

### Keyframe Extraction Tuning

In [`processing/registry.py`](processing/registry.py), adjust:

```python
extract_frames(
    hist_threshold=0.28,       # Lower = more frames (0.18–0.45)
    ssim_threshold=0.89,       # Lower = more frames (0.82–0.93)
    min_frame_interval=8       # Min frames between saves (~0.3s @ 30fps)
)
```

### Frame Analysis Settings

In [`processing/registry.py`](processing/registry.py):

```python
analyze_frames_directory(
    conf_threshold=0.50,       # YOLO confidence minimum
    caption_max_tokens=45,     # BLIP caption length
    caption_num_beams=3        # Beam search quality (lower = faster)
)
```

## Models Used

| Component | Model | Source |
|-----------|-------|--------|
| Object Detection | YOLOv10n | [THU-MIG/yolov10](https://github.com/THU-MIG/yolov10) |
| Image Captioning | BLIP Base | [Salesforce/blip-image-captioning-base](https://huggingface.co/Salesforce/blip-image-captioning-base) |
| OCR | EasyOCR | [JaidedAI/EasyOCR](https://github.com/JaidedAI/EasyOCR) |
| Audio Transcription | Whisper Base | [OpenAI/Whisper](https://github.com/openai/whisper) |

## Performance Notes

- **CPU Mode**: Optimized for Intel i7 + Iris Xe (see [`misc/gpu_tester.py`](misc/gpu_tester.py))
- **Memory**: ~2GB for model loading
- **Speed**: Frame analysis ~2–5 frames/min depending on hardware

## Experimental Features

- **[`misc/hf_img_txt.py`](misc/hf_img_txt.py)** — LLaVA OneVision video summarization (alternative to frame-by-frame analysis)
- **[`misc/gpu_tester.py`](misc/gpu_tester.py)** — Parallel frame processing with `ProcessPoolExecutor`

## Troubleshooting

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### YOLO Model Not Found
The model auto-downloads. If issues persist:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov10n.pt')"
```

### Instagram Login Issues
Some accounts may require additional authentication. Check [instaloader documentation](https://instaloader.github.io/).

### Memory Issues
Reduce `caption_max_tokens` or `num_workers` in analysis settings.

## Cleanup

Run to clear all downloaded/processed files:
```bash
python -c "from clean_cache import clear_existing_data; clear_existing_data()"
```

## Dependencies

See [`requirements.txt`](requirements.txt) for the full list. Key packages:
- `instaloader` — Instagram content download
- `moviepy` — Audio extraction
- `opencv-python` — Video/image processing
- `torch` — Deep learning backend
- `ultralytics` — YOLO
- `transformers` — BLIP & Whisper
- `easyocr` — OCR
- `openai-whisper` — Audio transcription

## License

[Specify your license here]

## Notes

- All downloaded content should comply with Instagram's Terms of Service
- Model weights are large (~2GB total) and are not versioned in git
- GPU support available but defaults to CPU for compatibility