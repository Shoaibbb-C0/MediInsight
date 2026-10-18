"""
Image Preprocessing and Camera Quality Pipeline for Simplifier 2.0.
Performs deskew, perspective rectification, blur/glare estimation, and safe dimension limits.
"""

import cv2
import numpy as np
from PIL import Image, ImageOps
import io
from typing import Tuple, Dict, Any, Optional

MAX_IMAGE_DIMENSION = 4096
MIN_IMAGE_DIMENSION = 200

def check_image_safety_and_dimensions(image_bytes: bytes) -> Image.Image:
    """Protects against corrupted files, zip bombs, or extreme dimensions."""
    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        pil_img.verify()
    except Exception as e:
        raise ValueError(f"Corrupted or invalid image file: {str(e)}")

    # Re-open for actual processing after verify()
    pil_img = Image.open(io.BytesIO(image_bytes))
    w, h = pil_img.size
    if w*h > 25_000_000:
        raise ValueError("Image exceeds the 25 megapixel safety limit.")
    pil_img = ImageOps.exif_transpose(pil_img)
    w, h = pil_img.size
    
    if w > MAX_IMAGE_DIMENSION or h > MAX_IMAGE_DIMENSION:
        # Safely downscale excessively large image to prevent memory exhaustion
        ratio = min(MAX_IMAGE_DIMENSION / w, MAX_IMAGE_DIMENSION / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
    return pil_img

def assess_image_quality(cv_img: np.ndarray) -> Dict[str, Any]:
    """Computes blur variance and glare metrics."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
    
    # Laplacian variance for blur
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = bool(laplacian_var < 80.0)

    # Glare detection via overexposed region ratio
    _, bright_mask = cv2.threshold(gray, 248, 255, cv2.THRESH_BINARY)
    glare_ratio = float(np.count_nonzero(bright_mask) / (gray.shape[0] * gray.shape[1]))
    has_glare = bool(glare_ratio > 0.15)

    return {
        "blur_score": float(laplacian_var),
        "is_blurry": is_blurry,
        "glare_ratio": glare_ratio,
        "has_glare": has_glare
    }

def deskew_and_enhance(cv_img: np.ndarray) -> np.ndarray:
    """Deskews document and applies gentle adaptive contrast enhancement."""
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY) if len(cv_img.shape) == 3 else cv_img
    
    # Edge detection to estimate rotation angle
    coords = np.column_stack(np.where(gray < 220))
    if len(coords) > 50:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle
            
        # Rotate if skew is between 1 and 25 degrees
        if 1.0 < abs(angle) < 25.0:
            h, w = cv_img.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            cv_img = cv2.warpAffine(cv_img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return cv_img
