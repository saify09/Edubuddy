try:
    import easyocr
    import cv2
    import numpy as np
except ImportError:
    easyocr = None
    cv2 = None
    np = None

# Initialize reader once (lazy load could be better but this is fine for now)
# Using CPU to avoid CUDA issues if not present, and English language
reader = None
if easyocr:
    try:
        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
    except Exception as e:
        print(f"Warning: EasyOCR failed to initialize: {e}")
        reader = None

def preprocess_image(image):
    """
    Applies preprocessing to improve OCR accuracy.
    Converts to grayscale, denoises, and applies adaptive thresholding.
    """
    try:
        if cv2 is None:
            return image

        # Check if it's a path or numpy array
        if isinstance(image, str):
            if not os.path.exists(image):
                return None
            img = cv2.imread(image)
        else:
            img = image

        if img is None:
            return None

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Remove noise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Adaptive thresholding to binarize (black text on white bg)
        # This helps significantly with varying lighting and noise
        processed = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        return processed
    except Exception as e:
        print(f"Warning: Image preprocessing failed: {e}")
        return image # Fallback to original

def parse_image(file_path: str) -> str:
    """
    Extracts text from an image file using EasyOCR with preprocessing.
    """
    if not reader:
        return "[Error: OCR Engine not available]"

    try:
        # Preprocess
        processed_img = preprocess_image(file_path)
        result = []
        
        if processed_img is not None:
             result = reader.readtext(processed_img, detail=0)
        
        # Fallback to original if preprocessing yielded no text
        if not result:
            # print("DEBUG: Preprocessing yielded no text, trying original...")
            result = reader.readtext(file_path, detail=0)
             
        return " ".join(result)
    except Exception as e:
        return f"[Error extracting text from image: {str(e)}]"
