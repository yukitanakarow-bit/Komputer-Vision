"""
================================================================================
MODUL UTILITAS - FUNGSI HELPER & SUPPORTING FUNCTIONS
================================================================================

Modul ini berisi fungsi-fungsi utility yang digunakan di berbagai bagian
dari Sistem SmartAttend untuk menghindari redundancy dan meningkatkan readability.

Fungsi-fungsi yang tersedia:
- File handling & directory management
- Logging & error handling
- String formatting & date/time utilities
- Image validation
- Directory organization

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import os
import logging
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Union, Tuple, Optional
import config

# ============================================================================
# SETUP LOGGING
# ============================================================================

def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger untuk tracking dan debugging.
    
    Args:
        name (str): Nama logger (biasanya __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Program dimulai")
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # File handler
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = setup_logger(__name__)

# ============================================================================
# FILE & DIRECTORY UTILITIES
# ============================================================================

def create_dated_folder() -> Path:
    """
    Buat/dapatkan folder output berdasarkan tanggal hari ini.
    Struktur: output/YYYY-MM-DD/
    
    Returns:
        Path: Path ke folder yang sudah dibuat
    
    Example:
        >>> folder = create_dated_folder()
        >>> print(folder)
        output/2024-01-15
    """
    today = datetime.now().strftime("%Y-%m-%d")
    dated_folder = config.OUTPUT_DIR / today
    dated_folder.mkdir(parents=True, exist_ok=True)
    
    if config.VERBOSE:
        logger.info(f"Folder tanggal siap: {dated_folder}")
    
    return dated_folder


def generate_filename(file_type: str = "kartu") -> str:
    """
    Generate nama file dengan format: YYYYMMDD_HHMMSS_{type}.{ext}
    Contoh: 20240115_083045_kartu.jpg
    
    Args:
        file_type (str): Tipe file ('kartu', 'summary', dll)
    
    Returns:
        str: Nama file yang sudah di-generate
    
    Example:
        >>> filename = generate_filename("kartu")
        >>> print(filename)
        20240115_083045_kartu.jpg
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file_type}.{config.OUTPUT_FORMAT}"
    return filename


def get_file_size(filepath: Union[str, Path]) -> float:
    """
    Dapatkan ukuran file dalam MB.
    
    Args:
        filepath (Union[str, Path]): Path ke file
    
    Returns:
        float: Ukuran file dalam MB
    """
    return os.path.getsize(filepath) / (1024 * 1024)


# ============================================================================
# IMAGE VALIDATION & CHECKING
# ============================================================================

def is_valid_image_format(filepath: Union[str, Path]) -> bool:
    """
    Check apakah file memiliki format gambar yang didukung.
    
    Args:
        filepath (Union[str, Path]): Path ke file
    
    Returns:
        bool: True jika format valid, False sebaliknya
    
    Example:
        >>> is_valid_image_format("photo.jpg")
        True
        >>> is_valid_image_format("document.txt")
        False
    """
    ext = Path(filepath).suffix.lower()
    return ext in config.ACCEPTED_IMAGE_FORMATS


def validate_image_file(filepath: Union[str, Path]) -> Tuple[bool, str]:
    """
    Validasi image file secara lengkap.
    Check: format, ukuran file, existence, dimensi
    
    Args:
        filepath (Union[str, Path]): Path ke file
    
    Returns:
        Tuple[bool, str]: (is_valid, message)
    
    Example:
        >>> valid, msg = validate_image_file("photo.jpg")
        >>> if valid:
        ...     print("File valid!")
        ... else:
        ...     print(f"Error: {msg}")
    """
    filepath = Path(filepath)
    
    # Check existence
    if not filepath.exists():
        return False, f"File tidak ditemukan: {filepath}"
    
    # Check format
    if not is_valid_image_format(filepath):
        return False, f"Format tidak didukung. Gunakan: {config.ACCEPTED_IMAGE_FORMATS}"
    
    # Check file size
    file_size_mb = get_file_size(filepath)
    if file_size_mb > config.MAX_FILE_SIZE:
        return False, f"Ukuran file terlalu besar ({file_size_mb:.1f} MB > {config.MAX_FILE_SIZE} MB)"
    
    # Check image dimensions
    try:
        img = cv2.imread(str(filepath))
        if img is None:
            return False, "Gagal membaca file gambar"
        
        height, width = img.shape[:2]
        if width < config.MIN_IMAGE_WIDTH or height < config.MIN_IMAGE_HEIGHT:
            return False, f"Dimensi gambar terlalu kecil ({width}x{height})"
        
        return True, "File valid"
    
    except Exception as e:
        return False, f"Error saat validasi: {str(e)}"


def get_image_info(image: np.ndarray) -> dict:
    """
    Dapatkan informasi detail tentang gambar.
    
    Args:
        image (np.ndarray): Gambar dalam format numpy array
    
    Returns:
        dict: Informasi gambar (width, height, channels, dtype, size_mb)
    
    Example:
        >>> img = cv2.imread("photo.jpg")
        >>> info = get_image_info(img)
        >>> print(f"Dimensi: {info['width']}x{info['height']}")
    """
    if image is None:
        return {}
    
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1
    size_bytes = image.nbytes
    size_mb = size_bytes / (1024 * 1024)
    
    return {
        "width": width,
        "height": height,
        "channels": channels,
        "aspect_ratio": width / height if height != 0 else 0,
        "dtype": str(image.dtype),
        "size_bytes": size_bytes,
        "size_mb": size_mb
    }


# ============================================================================
# IMAGE STATISTICS & ADJUSTMENT
# ============================================================================

def get_image_brightness(image: np.ndarray) -> float:
    """
    Hitung rata-rata brightness dari gambar.
    Range: 0-255 (0=gelap, 255=terang)
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        float: Brightness value
    """
    if len(image.shape) == 3:
        # Untuk BGR/RGB, konversi ke grayscale dulu
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    return np.mean(gray)


def get_image_contrast(image: np.ndarray) -> float:
    """
    Hitung contrast dari gambar menggunakan standard deviation.
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        float: Contrast value (standard deviation)
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    return np.std(gray)


def adjust_brightness_contrast(image: np.ndarray, 
                               brightness: float = 0.0, 
                               contrast: float = 1.0) -> np.ndarray:
    """
    Adjust brightness dan contrast gambar.
    Formula: adjusted = contrast * (pixel + brightness)
    
    Args:
        image (np.ndarray): Gambar input
        brightness (float): -100 to 100 (negative = darker, positive = brighter)
        contrast (float): 0.5 to 3.0 (< 1 = lower contrast, > 1 = higher contrast)
    
    Returns:
        np.ndarray: Adjusted image
    
    Example:
        >>> img = cv2.imread("photo.jpg")
        >>> adjusted = adjust_brightness_contrast(img, brightness=10, contrast=1.2)
    """
    # Validasi input
    brightness = np.clip(brightness, -100, 100)
    contrast = np.clip(contrast, 0.5, 3.0)
    
    # Apply adjustment
    adjusted = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    
    return adjusted


def auto_adjust_brightness_contrast(image: np.ndarray) -> np.ndarray:
    """
    Otomatis adjust brightness dan contrast menggunakan histogram
    equalization dan CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    Args:
        image (np.ndarray): Gambar input
    
    Returns:
        np.ndarray: Adjusted image
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    adjusted_gray = clahe.apply(gray)
    
    # Jika input adalah BGR, konversi kembali
    if len(image.shape) == 3:
        adjusted = cv2.cvtColor(adjusted_gray, cv2.COLOR_GRAY2BGR)
        return adjusted
    else:
        return adjusted_gray


# ============================================================================
# HISTOGRAM & VISUALIZATION
# ============================================================================

def get_histogram(image: np.ndarray, bins: int = 256) -> dict:
    """
    Hitung histogram dari gambar.
    
    Args:
        image (np.ndarray): Gambar input
        bins (int): Jumlah bins untuk histogram
    
    Returns:
        dict: Histogram untuk setiap channel
    """
    if len(image.shape) == 3:
        channels = cv2.split(image)
        color = ('b', 'g', 'r')
    else:
        channels = [image]
        color = ('gray',)
    
    histogram = {}
    for i, col in enumerate(color):
        hist = cv2.calcHist([channels[i]], [0], None, [bins], [0, 256])
        histogram[col] = hist.flatten()
    
    return histogram


# ============================================================================
# PATH & STRING UTILITIES
# ============================================================================

def format_timestamp(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object menjadi string yang readable.
    
    Args:
        dt (datetime): Datetime object (default: sekarang)
        format_str (str): Format string
    
    Returns:
        str: Formatted timestamp
    
    Example:
        >>> ts = format_timestamp()
        >>> print(ts)
        2024-01-15 08:30:45
    """
    if dt is None:
        dt = datetime.now()
    
    return dt.strftime(format_str)


def format_filesize(size_bytes: int) -> str:
    """
    Format ukuran file menjadi readable format (B, KB, MB, GB).
    
    Args:
        size_bytes (int): Ukuran dalam bytes
    
    Returns:
        str: Formatted size
    
    Example:
        >>> print(format_filesize(1024 * 1024))
        1.0 MB
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"


# ============================================================================
# ERROR HANDLING & SAFE OPERATIONS
# ============================================================================

def safe_read_image(filepath: Union[str, Path]) -> Optional[np.ndarray]:
    """
    Baca gambar dengan error handling yang baik.
    
    Args:
        filepath (Union[str, Path]): Path ke file gambar
    
    Returns:
        Optional[np.ndarray]: Gambar atau None jika gagal
    """
    try:
        img = cv2.imread(str(filepath))
        if img is None:
            logger.error(f"Gagal membaca gambar: {filepath}")
            return None
        
        if config.VERBOSE:
            logger.info(f"✓ Berhasil membaca: {filepath}")
        
        return img
    
    except Exception as e:
        logger.error(f"Error saat membaca gambar: {str(e)}")
        return None


def safe_write_image(filepath: Union[str, Path], image: np.ndarray, quality: int = 95) -> bool:
    """
    Tulis gambar dengan error handling yang baik.
    
    Args:
        filepath (Union[str, Path]): Path untuk menyimpan file
        image (np.ndarray): Gambar yang akan disimpan
        quality (int): Kualitas JPEG (0-100)
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Tentukan parameter berdasarkan format file
        ext = filepath.suffix.lower()
        if ext in ['.jpg', '.jpeg']:
            params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        elif ext == '.png':
            params = [cv2.IMWRITE_PNG_COMPRESSION, 9]
        else:
            params = []
        
        success = cv2.imwrite(str(filepath), image, params)
        
        if success:
            if config.VERBOSE:
                logger.info(f"✓ Gambar disimpan: {filepath}")
            return True
        else:
            logger.error(f"Gagal menyimpan gambar: {filepath}")
            return False
    
    except Exception as e:
        logger.error(f"Error saat menyimpan gambar: {str(e)}")
        return False

# ============================================================================
