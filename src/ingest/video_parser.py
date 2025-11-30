try:
    import cv2
    import easyocr
    import numpy as np
except ImportError:
    cv2 = None
    easyocr = None
    np = None
import os

# Re-use the reader from image_parser if possible, or init new one
reader = None
if easyocr:
    try:
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    except:
        reader = None

def parse_video(file_path: str, interval_seconds: int = 5) -> str:
    """
    Extracts text from video frames at specified intervals using OCR.
    """
    if not reader:
        return "[Error: OCR Engine not available]"
    
    if cv2 is None:
        return "[Error: OpenCV not available]"

    text_content = []
    cap = cv2.VideoCapture(file_path)
    
    if not cap.isOpened():
        return "[Error: Could not open video file]"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 24 # Fallback
    
    frame_interval = int(fps * interval_seconds)
    frame_count = 0
    
    print(f"Processing video {file_path} every {interval_seconds} seconds...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            try:
                # Convert to grayscale for preprocessing (similar to image_parser)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Denoise
                denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
                # Threshold
                processed_frame = cv2.adaptiveThreshold(
                    denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                
                result = reader.readtext(processed_frame, detail=0)
                frame_text = " ".join(result)
                if frame_text.strip():
                    timestamp = frame_count / fps
                    text_content.append(f"[Time: {timestamp:.1f}s] {frame_text}")
            except Exception as e:
                print(f"Error OCRing frame at {frame_count}: {e}")
        
        frame_count += 1

    cap.release()
    return "\n".join(text_content)
