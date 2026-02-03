import cv2
import os

def extract_frames(video_path, output_folder, threshold=10000):
    """
    Extracts frames from a video only when a significant visual change occurs.
    
    Args:
        video_path (str): Path to the input video.
        output_folder (str): Directory to save extracted frames.
        threshold (int): Sensitivity of change detection. 
                         Higher = less sensitive (needs bigger changes to trigger).
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Read the first frame as the initial reference
    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Could not read the first frame.")
        return

    # Pre-process the first frame (Grayscale + Blur to reduce noise)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. Pre-process current frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # 2. Compute the absolute difference between current and previous frame
        frame_diff = cv2.absdiff(prev_gray, gray)
        # 3. Apply thresholding to create a binary mask of the changes
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

        # 4. Count white pixels (representing change)
        change_score = cv2.countNonZero(thresh)
        
        if change_score > threshold:
            frame_filename = os.path.join(output_folder, f"change_{saved_count:04d}.png")
            cv2.imwrite(frame_filename, frame)
            # print(f"Change detected! Saved: {frame_filename} (Score: {change_score})")
            
            # Update reference frame so we detect the NEXT change relative to this one
            prev_gray = gray
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Extraction complete. Saved {saved_count} frames from {frame_count} total frames.")


if __name__ == "__main__":
    # --- Usage ---
    video_file = 'ingestion/video.mp4'
    output_directory = 'artifacts/video_frames'
    
    # Run the function (Adjust threshold based on your video's movement)
    extract_frames(video_file, output_directory, threshold=15000)
