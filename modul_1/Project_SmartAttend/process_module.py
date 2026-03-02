"""
================================================================================
MODUL PEMROSESAN GAMBAR - IMAGE PROCESSING & TRANSFORMATION
================================================================================

Modul ini menangani semua operasi pemrosesan gambar:
- Resize & aspect ratio preservation
- Color space conversion
- Brightness & contrast adjustment
- Border & frame addition
- Annotation (timestamp, watermark, text)
- Image quality improvement

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional
from enum import Enum

import config
from utils import (logger, safe_write_image, 
                   get_image_brightness, get_image_contrast,
                   adjust_brightness_contrast, auto_adjust_brightness_contrast)

# ============================================================================
# COLOR SPACE & CONVERSION
# ============================================================================

class ColorSpace(Enum):
    """Enum untuk color space yang didukung."""
    BGR = "BGR"
    RGB = "RGB"
    GRAY = "GRAY"
    HSV = "HSV"

def convert_color_space(image: np.ndarray, 
                       target_space: ColorSpace = ColorSpace.GRAY) -> np.ndarray:
    """
    Konversi gambar ke color space yang ditentukan.
    
    Args:
        image (np.ndarray): Gambar input (BGR)
        target_space (ColorSpace): Target color space
    
    Returns:
        np.ndarray: Gambar yang sudah di-konversi
    
    Example:
        >>> img_gray = convert_color_space(img, ColorSpace.GRAY)
        >>> img_hsv = convert_color_space(img, ColorSpace.HSV)
    """
    if target_space == ColorSpace.GRAY:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    elif target_space == ColorSpace.RGB:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    elif target_space == ColorSpace.HSV:
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    elif target_space == ColorSpace.BGR:
        return image
    
    logger.warning(f"Tidak dapat konversi ke {target_space.value}")
    return image


def convert_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Konversi gambar ke grayscale.
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        np.ndarray: Grayscale image
    """
    return convert_color_space(image, ColorSpace.GRAY)

# ============================================================================
# RESIZE & SCALING
# ============================================================================

def resize_card_standard(image: np.ndarray,
                        width: int = config.CARD_WIDTH,
                        height: int = config.CARD_HEIGHT,
                        preserve_aspect: bool = True,
                        fill_color: Tuple[int, int, int] = (255, 255, 255)) -> np.ndarray:
    """
    Resize gambar ke ukuran standar kartu dengan menjaga aspect ratio.
    Jika aspect ratio berbeda, akan di-pad dengan warna tertentu.
    
    Args:
        image (np.ndarray): Gambar input
        width (int): Target width
        height (int): Target height
        preserve_aspect (bool): Jaga aspect ratio
        fill_color (Tuple): Warna padding (BGR)
    
    Returns:
        np.ndarray: Resized image dengan dimensi (height, width, channels)
    
    Example:
        >>> img_resized = resize_card_standard(img)
        >>> print(img_resized.shape)  # (250, 400, 3)
    """
    if not preserve_aspect:
        # Simple resize tanpa menjaga aspect ratio
        resized = cv2.resize(image, (width, height), 
                            interpolation=cv2.INTER_LANCZOS4)
        if config.VERBOSE:
            logger.info(f"✓ Gambar di-resize ke {width}x{height} (tanpa aspect ratio)")
        return resized
    
    # Preserve aspect ratio
    h, w = image.shape[:2]
    
    # Validasi dimensi input
    if h == 0 or w == 0:
        logger.error("❌ Invalid image dimensions")
        return image
    
    aspect_ratio = w / h
    target_ratio = width / height
    
    if aspect_ratio > target_ratio:
        # Gambar lebih wide, resize berdasarkan height
        new_h = height
        new_w = int(height * aspect_ratio)
    else:
        # Gambar lebih tall, resize berdasarkan width
        new_w = width
        new_h = int(width / aspect_ratio)
    
    # Clamp ke maximum size untuk avoid oversizing
    if new_w > width * 2 or new_h > height * 2:
        scale = min(width / w, height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
    
    # Resize
    resized = cv2.resize(image, (new_w, new_h), 
                        interpolation=cv2.INTER_LANCZOS4)
    
    # Create canvas dengan ukuran target
    if len(image.shape) == 3:
        canvas = np.full((height, width, image.shape[2]), fill_color, dtype=np.uint8)
    else:
        canvas = np.full((height, width), fill_color if isinstance(fill_color, int) else fill_color[0], 
                        dtype=np.uint8)
    
    # Calculate safe offsets
    y_offset = max(0, (height - new_h) // 2)
    x_offset = max(0, (width - new_w) // 2)
    
    # Calculate safe region untuk paste (handle edge cases)
    y_end = min(height, y_offset + new_h)
    x_end = min(width, x_offset + new_w)
    
    resized_y_end = y_end - y_offset
    resized_x_end = x_end - x_offset
    
    # Paste resized image ke tengah canvas dengan size checking
    if resized_y_end > 0 and resized_x_end > 0:
        canvas[y_offset:y_end, x_offset:x_end] = resized[:resized_y_end, :resized_x_end]
    
    if config.VERBOSE:
        logger.info(f"✓ Gambar di-resize ke {width}x{height} (aspect ratio preserved)")
    
    return canvas


def smart_resize(image: np.ndarray,
                max_width: int = config.CARD_WIDTH,
                max_height: int = config.CARD_HEIGHT) -> np.ndarray:
    """
    Smart resize yang automatically adjust berdasarkan dimensi input.
    Jika gambar lebih kecil dari target, tidak di-upscale untuk menghindari blur.
    
    Args:
        image (np.ndarray): Gambar input
        max_width (int): Maximum width
        max_height (int): Maximum height
    
    Returns:
        np.ndarray: Resized image
    """
    h, w = image.shape[:2]
    
    # Jika sudah cukup kecil, pad aja
    if w <= max_width and h <= max_height:
        return resize_card_standard(image, max_width, max_height)
    
    # Jika terlalu besar, downscale
    scale = min(max_width / w, max_height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized = cv2.resize(image, (new_w, new_h), 
                        interpolation=cv2.INTER_LANCZOS4)
    
    return resized


# ============================================================================
# BORDER & FRAME
# ============================================================================

def add_border(image: np.ndarray,
              thickness: int = config.BORDER_WIDTH,
              color: Tuple[int, int, int] = config.BORDER_COLOR) -> np.ndarray:
    """
    Tambahkan border/frame ke gambar.
    
    Args:
        image (np.ndarray): Gambar input
        thickness (int): Ketebalan border dalam pixel
        color (Tuple): Warna border (BGR)
    
    Returns:
        np.ndarray: Gambar dengan border
    
    Example:
        >>> img_border = add_border(img, thickness=5, color=(0, 0, 0))
    """
    h, w = image.shape[:2]
    
    # Buat canvas baru dengan ukuran lebih besar
    new_h = h + 2 * thickness
    new_w = w + 2 * thickness
    
    if len(image.shape) == 3:
        bordered = np.full((new_h, new_w, image.shape[2]), color, dtype=np.uint8)
    else:
        bordered = np.full((new_h, new_w), color if isinstance(color, int) else color[0], 
                          dtype=np.uint8)
    
    # Paste original image di tengah
    bordered[thickness:thickness+h, thickness:thickness+w] = image
    
    if config.VERBOSE:
        logger.info(f"✓ Border ditambahkan ({thickness}px)")
    
    return bordered


def add_double_border(image: np.ndarray,
                     outer_thickness: int = 3,
                     inner_thickness: int = 1,
                     outer_color: Tuple[int, int, int] = (0, 0, 0),
                     inner_color: Tuple[int, int, int] = (200, 200, 200)) -> np.ndarray:
    """
    Tambahkan double border untuk efek yang lebih menarik.
    
    Args:
        image (np.ndarray): Gambar input
        outer_thickness (int): Ketebalan border luar
        inner_thickness (int): Ketebalan border dalam
        outer_color (Tuple): Warna border luar
        inner_color (Tuple): Warna border dalam
    
    Returns:
        np.ndarray: Gambar dengan double border
    """
    # Add outer border
    image = add_border(image, outer_thickness, outer_color)
    
    # Add inner border
    image = add_border(image, inner_thickness, inner_color)
    
    return image

# ============================================================================
# ANNOTATION (TIMESTAMP & WATERMARK)
# ============================================================================

def add_timestamp(image: np.ndarray,
                 timestamp: datetime = None,
                 position: str = "bottom-right",
                 font_scale: float = config.TIMESTAMP_FONT_SCALE,
                 color: Tuple[int, int, int] = config.TIMESTAMP_COLOR,
                 bg_color: Tuple[int, int, int] = config.TIMESTAMP_BG_COLOR,
                 thickness: int = config.TIMESTAMP_THICKNESS) -> np.ndarray:
    """
    Tambahkan timestamp pada gambar.
    
    Args:
        image (np.ndarray): Gambar input
        timestamp (datetime): Waktu custom (default: sekarang)
        position (str): Posisi timestamp 
                       ('top-left', 'top-right', 'bottom-left', 'bottom-right')
        font_scale (float): Ukuran font
        color (Tuple): Warna teks (BGR)
        bg_color (Tuple): Warna background
        thickness (int): Ketebalan teks
    
    Returns:
        np.ndarray: Gambar dengan timestamp
    
    Example:
        >>> img_ts = add_timestamp(img, position="bottom-right")
    """
    image = image.copy()
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Format timestamp: YYYY-MM-DD HH:MM:SS
    ts_text = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    h, w = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = font_scale
    thickness = thickness
    
    # Get text size untuk background
    (text_width, text_height), baseline = cv2.getTextSize(
        ts_text, font, font_scale, thickness)
    
    # Tentukan koordinat
    padding = 5
    text_width += padding * 2
    text_height += padding * 2
    
    if "top" in position:
        y = padding + text_height
    else:
        y = h - padding
    
    if "left" in position:
        x = padding
    else:
        x = w - text_width + padding
    
    # Draw background rectangle
    cv2.rectangle(image, (x - padding, y - text_height), 
                 (x + text_width - padding, y + baseline), 
                 bg_color, -1)
    
    # Draw text
    cv2.putText(image, ts_text, (x, y - baseline), 
               font, font_scale, color, thickness)
    
    if config.VERBOSE:
        logger.info(f"✓ Timestamp ditambahkan: {ts_text}")
    
    return image


def add_watermark(image: np.ndarray,
                 text: str = config.WATERMARK_TEXT,
                 position: str = "bottom-right",
                 font_scale: float = config.WATERMARK_FONT_SCALE,
                 color: Tuple[int, int, int] = config.WATERMARK_COLOR,
                 thickness: int = config.WATERMARK_THICKNESS,
                 opacity: float = 0.7) -> np.ndarray:
    """
    Tambahkan watermark pada gambar.
    
    Args:
        image (np.ndarray): Gambar input
        text (str): Teks watermark
        position (str): Posisi
        font_scale (float): Ukuran font
        color (Tuple): Warna (BGR)
        thickness (int): Ketebalan teks
        opacity (float): Transparansi (0-1)
    
    Returns:
        np.ndarray: Gambar dengan watermark
    """
    image_with_wm = image.copy()
    
    h, w = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, font, font_scale, thickness)
    
    # Tentukan koordinat
    padding = 10
    
    if "top" in position:
        y = padding + text_height
    else:
        y = h - padding
    
    if "left" in position:
        x = padding
    else:
        x = w - text_width - padding
    
    # Buat transparent overlay
    overlay = image.copy()
    cv2.putText(overlay, text, (x, y), font, font_scale, color, thickness)
    
    # Blend dengan original
    image_with_wm = cv2.addWeighted(image_with_wm, 1 - opacity, 
                                    overlay, opacity, 0)
    
    if config.VERBOSE:
        logger.info(f"✓ Watermark ditambahkan: {text}")
    
    return image_with_wm


def add_annotation_box(image: np.ndarray,
                      text_lines: list,
                      position: str = "top-left",
                      bg_color: Tuple[int, int, int] = (240, 240, 240),
                      text_color: Tuple[int, int, int] = (0, 0, 0),
                      font_scale: float = 0.5,
                      padding: int = 5) -> np.ndarray:
    """
    Tambahkan annotation box (multi-line text dengan background).
    
    Args:
        image (np.ndarray): Gambar input
        text_lines (list): List of text strings
        position (str): Posisi
        bg_color (Tuple): Warna background
        text_color (Tuple): Warna teks
        font_scale (float): Ukuran font
        padding (int): Padding dalam box
    
    Returns:
        np.ndarray: Gambar dengan annotation box
    """
    image = image.copy()
    h, w = image.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Calculate box dimensions
    max_text_width = 0
    total_text_height = 0
    
    for text in text_lines:
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, 1)
        max_text_width = max(max_text_width, text_width)
        total_text_height += text_height + 2
    
    box_width = max_text_width + 2 * padding
    box_height = total_text_height + 2 * padding
    
    # Tentukan koordinat
    if "top" in position:
        box_y = 0
    else:
        box_y = h - box_height
    
    if "left" in position:
        box_x = 0
    else:
        box_x = w - box_width
    
    # Draw box
    cv2.rectangle(image, (box_x, box_y), 
                 (box_x + box_width, box_y + box_height), 
                 bg_color, -1)
    
    # Draw text
    y_offset = box_y + padding
    for text in text_lines:
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, 1)
        cv2.putText(image, text, (box_x + padding, y_offset + text_height), 
                   font, font_scale, text_color, 1)
        y_offset += text_height + 2
    
    return image

# ============================================================================
# BRIGHTNESS & CONTRAST ADJUSTMENT
# ============================================================================

def equalize_histogram(image: np.ndarray) -> np.ndarray:
    """
    Apply histogram equalization untuk meningkatkan contrast.
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        np.ndarray: Hasil equalization
    """
    if len(image.shape) == 3:
        # Untuk BGR, convert ke HSV, equalize V, then convert back
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.equalizeHist(v)
        hsv = cv2.merge((h, s, v))
        result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    else:
        result = cv2.equalizeHist(image)
    
    if config.VERBOSE:
        logger.info("✓ Histogram equalization applied")
    
    return result


def auto_enhance(image: np.ndarray) -> np.ndarray:
    """
    Otomatis enhance gambar dengan multiple techniques.
    Kombinasi: histogram equalization + CLAHE.
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        np.ndarray: Enhanced image
    """
    # Apply CLAHE
    enhanced = auto_adjust_brightness_contrast(image)
    
    if config.VERBOSE:
        logger.info("✓ Auto enhancement applied")
    
    return enhanced

# ============================================================================
# FULL PIPELINE - PROCESS CARD IMAGE
# ============================================================================

def process_card_image(image: np.ndarray,
                      add_ts: bool = True,
                      add_wm: bool = True,
                      add_frame: bool = True,
                      auto_enhance_flag: bool = False,
                      brightness: float = 0.0,
                      contrast: float = 1.0) -> np.ndarray:
    """
    Process kartu gambar dengan full pipeline.
    Urutan: Resize → EnhanceOpsional → Border → Timestamp → Watermark
    
    Args:
        image (np.ndarray): Gambar input
        add_ts (bool): Tambahkan timestamp
        add_wm (bool): Tambahkan watermark
        add_frame (bool): Tambahkan border
        auto_enhance_flag (bool): Apply auto enhancement
        brightness (float): Brightness adjustment
        contrast (float): Contrast adjustment
    
    Returns:
        np.ndarray: Processed image
    
    Example:
        >>> processed = process_card_image(img)
    """
    result = image.copy()
    
    logger.info("Memulai card image processing...")
    
    # 1. Resize ke ukuran standar
    result = resize_card_standard(result)
    logger.info("✓ Resize ke ukuran standar")
    
    # 2. Auto enhance (optional)
    if auto_enhance_flag:
        result = auto_enhance(result)
        logger.info("✓ Auto enhancement applied")
    
    # 3. Manual brightness/contrast adjustment
    if brightness != 0.0 or contrast != 1.0:
        result = adjust_brightness_contrast(result, brightness, contrast)
        logger.info(f"✓ Brightness/Contrast adjusted (B:{brightness}, C:{contrast})")
    
    # 4. Add border
    if add_frame:
        result = add_double_border(result)
        logger.info("✓ Double border ditambahkan")
    
    # 5. Add timestamp
    if add_ts:
        result = add_timestamp(result)
        logger.info("✓ Timestamp ditambahkan")
    
    # 6. Add watermark
    if add_wm:
        result = add_watermark(result)
        logger.info("✓ Watermark ditambahkan")
    
    logger.info("✓ Card image processing selesai")
    
    return result


# ============================================================================
