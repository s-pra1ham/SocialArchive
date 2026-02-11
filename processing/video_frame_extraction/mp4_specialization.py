import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim


def extract_frames(
    video_path,
    output_folder,
    hist_threshold=0.30,          # χ² distance — lower = more sensitive
    ssim_threshold=0.88,          # 1.0 = identical, 0.85–0.92 common range
    min_frame_interval=8,         # ~0.3 s at 30 fps — prevents burst saves
    use_grayscale_for_ssim=True,
    hist_method=cv2.HISTCMP_CHISQR
):
    """
    Extract keyframes on **structural / scene changes** with reduced sensitivity
    to talking-head micro-movements.

    Two checks:
      1. Color histogram difference (robust to small motion & lighting)
      2. SSIM structural similarity (catches layout / composition change)

    Triggers save when **either** difference is large enough.

    Args:
        hist_threshold:     smaller → more keyframes (0.18–0.45 typical)
        ssim_threshold:     smaller → more keyframes (0.82–0.93 typical)
        min_frame_interval: min frames between two saved keyframes
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    print(f"Video FPS ≈ {fps:.1f}")

    ret, prev_frame = cap.read()
    if not ret:
        print("Video is empty")
        return

    # Precompute initial histogram (BGR channels separately)
    prev_hist = []
    for channel in cv2.split(prev_frame):
        h = cv2.calcHist([channel], [0], None, [256], [0, 256])
        h = cv2.normalize(h, h).flatten()
        prev_hist.append(h)

    # Initial reference for SSIM (grayscale)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Save first frame
    frame_idx = 0
    saved_count = 0
    cv2.imwrite(os.path.join(output_folder, f"keyframe_{saved_count:04d}_frame_{frame_idx:06d}.jpg"), prev_frame)
    saved_count += 1
    last_save_idx = 0

    print("Extracting keyframes...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_idx += 1

        # Enforce minimum interval
        if frame_idx - last_save_idx < min_frame_interval:
            continue

        # ── Histogram comparison ───────────────────────────────────────
        hist_diff_max = 0
        for i, channel in enumerate(cv2.split(frame)):
            h = cv2.calcHist([channel], [0], None, [256], [0, 256])
            h = cv2.normalize(h, h).flatten()
            diff = cv2.compareHist(prev_hist[i], h, hist_method)
            hist_diff_max = max(hist_diff_max, diff)

        # ── SSIM (on grayscale or color) ───────────────────────────────
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ssim_value = ssim(prev_gray, curr_gray, data_range=curr_gray.max() - curr_gray.min())

        # Decide whether to save
        should_save = False
        reason = ""

        if hist_diff_max > hist_threshold:
            should_save = True
            reason += f"hist={hist_diff_max:.3f} "

        if ssim_value < ssim_threshold:
            should_save = True
            reason += f"ssim={ssim_value:.3f}"

        if should_save:
            filename = os.path.join(output_folder, f"keyframe_{saved_count:04d}_frame_{frame_idx:06d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Saved {os.path.basename(filename)}  | {reason.strip()}")

            # Update references
            prev_hist = [cv2.normalize(cv2.calcHist([ch], [0], None, [256], [0, 256]), cv2.normalize(cv2.calcHist([ch], [0], None, [256], [0, 256]), ch)).flatten()
                         for ch in cv2.split(frame)]
            prev_gray = curr_gray
            last_save_idx = frame_idx
            saved_count += 1

    cap.release()
    print(f"\nDone. Saved {saved_count} keyframes from ~{frame_idx} frames.")


if __name__ == "__main__":
    VIDEO = "ingestion/video.mp4"
    OUT_DIR = "artifacts/video_frames"

    extract_frames(
        video_path=VIDEO,
        output_folder=OUT_DIR,
        hist_threshold=0.28,       # ← tune this first (start 0.22–0.35)
        ssim_threshold=0.89,       # ← tune second (0.86–0.92)
        min_frame_interval=8       # adjust based on fps (8–15 common)
    )