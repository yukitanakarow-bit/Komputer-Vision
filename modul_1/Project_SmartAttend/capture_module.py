"""
================================================================================
MODUL CAPTURE - CAPTURE GAMBAR DARI WEBCAM ATAU FILE
================================================================================

Modul ini menangani semua operasi capture gambar dari berbagai sumber:
- Load gambar dari file (jpg, png, bmp, dll)
- Capture dari webcam secara real-time
- Preview dan validasi gambar yang di-capture

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Callable
from datetime import datetime
import threading
import queue

import config
from utils import (safe_read_image, validate_image_file, 
                   logger, get_image_info,
                   # helpers for saving captures directly
                   safe_write_image, create_dated_folder, generate_filename)

# ============================================================================
# LOAD IMAGE FROM FILE
# ============================================================================

def load_image_from_file(filepath: str) -> Optional[np.ndarray]:
    """
    Load gambar dari file dengan validasi lengkap.
    
    Args:
        filepath (str): Path ke file gambar
    
    Returns:
        Optional[np.ndarray]: Gambar dalam format BGR atau None jika gagal
    
    Example:
        >>> img = load_image_from_file("input/kartu.jpg")
        >>> if img is not None:
        ...     print(f"Gambar berhasil dimuat: {img.shape}")
    """
    # Validasi file
    valid, msg = validate_image_file(filepath)
    if not valid:
        logger.error(f"❌ {msg}")
        return None
    
    # Baca gambar
    image = safe_read_image(filepath)
    if image is None:
        logger.error(f"❌ Gagal membaca file: {filepath}")
        return None
    
    logger.info(f"✓ Gambar berhasil dimuat: {filepath}")
    info = get_image_info(image)
    logger.info(f"  → Dimensi: {info['width']}x{info['height']}, "
                f"Channels: {info['channels']}, Size: {info['size_mb']:.2f} MB")
    
    return image


def load_image_with_preview(filepath: str, window_name: str = "Preview Gambar") -> Optional[np.ndarray]:
    """
    Load gambar dan tampilkan preview dalam window.
    Tekan ESC untuk menutup window.
    
    Args:
        filepath (str): Path ke file gambar
        window_name (str): Nama window preview
    
    Returns:
        Optional[np.ndarray]: Gambar atau None jika gagal
    """
    image = load_image_from_file(filepath)
    if image is None:
        return None
    
    # Tampilkan preview
    cv2.imshow(window_name, image)
    logger.info("Tekan ESC untuk menutup preview...")
    
    while True:
        key = cv2.waitKey(30) & 0xFF
        if key == 27:  # ESC
            break
    
    cv2.destroyAllWindows()
    return image


# ============================================================================
# WEBCAM CAPTURE
# ============================================================================

class WebcamCapture:
    """
    Class untuk menangani webcam capture dengan preview real-time.
    
    Attributes:
        camera_id (int): ID camera (default: 0)
        frame_width (int): Lebar frame
        frame_height (int): Tinggi frame
        fps (int): Frame per second
    
    Example:
        >>> webcam = WebcamCapture()
        >>> for frame in webcam.get_frames():
        ...     cv2.imshow("Webcam", frame)
        ...     if cv2.waitKey(1) & 0xFF == ord('q'):
        ...         break
        >>> webcam.release()
    """
    
    def __init__(self, 
                 camera_id: int = config.WEBCAM_ID,
                 frame_width: int = config.WEBCAM_FRAME_WIDTH,
                 frame_height: int = config.WEBCAM_FRAME_HEIGHT,
                 fps: int = config.WEBCAM_FPS):
        """
        Inisialisasi webcam capture.
        
        Args:
            camera_id (int): ID camera
            frame_width (int): Lebar frame
            frame_height (int): Tinggi frame
            fps (int): Frame per second
        """
        self.camera_id = camera_id
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        
        # Buka camera
        self.cap = cv2.VideoCapture(self.camera_id)
        self.is_opened = self.cap.isOpened()
        
        if not self.is_opened:
            logger.error("❌ Webcam tidak dapat dibuka")
            return
        
        # Set properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        # Get actual properties
        self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"✓ Webcam opened: {self.actual_width}x{self.actual_height} @ {self.actual_fps} FPS")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Ambil satu frame dari webcam.
        
        Returns:
            Optional[np.ndarray]: Frame atau None jika gagal
        """
        if not self.is_opened:
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            logger.error("❌ Gagal membaca frame dari webcam")
            return None
        
        # Apply flip jika diperlukan
        if config.WEBCAM_FLIP_HORIZONTAL:
            frame = cv2.flip(frame, 1)
        if config.WEBCAM_FLIP_VERTICAL:
            frame = cv2.flip(frame, 0)
        
        return frame
    
    def get_frames(self):
        """
        Generator untuk mendapatkan frame secara kontinyu.
        
        Yields:
            np.ndarray: Frame dari webcam
        
        Example:
            >>> webcam = WebcamCapture()
            >>> for frame in webcam.get_frames():
            ...     cv2.imshow("Webcam", frame)
            ...     if cv2.waitKey(1) & 0xFF == ord('q'):
            ...         break
        """
        while self.is_opened:
            frame = self.get_frame()
            if frame is None:
                break
            yield frame
    
    def capture_single_frame(self, save: bool = True) -> Optional[np.ndarray]:
        """
        Capture satu frame tunggal dengan peringatan.
        Secara default frame juga disimpan ke dalam folder output harian.

        Args:
            save (bool): Jika True, hasil capture ditulis ke disk.
        """
        frame = self.get_frame()
        if frame is None:
            logger.error("❌ Gagal capture frame")
            return None
        
        logger.info(f"✓ Frame di-capture: {frame.shape}")
        if save:
            try:
                dated = create_dated_folder()
                fname = generate_filename("capture")
                filepath = dated / fname
                safe_write_image(str(filepath), frame, quality=config.OUTPUT_QUALITY)
            except Exception as e:
                logger.error(f"Error saving captured frame: {e}")
        return frame
    
    def preview(self, window_name: str = "Webcam Preview", duration_ms: int = 5000):
        """
        Tampilkan preview webcam.
        
        Args:
            window_name (str): Nama window
            duration_ms (int): Durasi preview dalam millisecond (-1 untuk indefinite)
        """
        logger.info(f"Preview webcam (tekan 'q' atau ESC untuk keluar)...")
        
        start_time = datetime.now()
        frame_count = 0
        
        while self.is_opened:
            frame = self.get_frame()
            if frame is None:
                break
            
            # Add info text
            cv2.putText(frame, f"Press 'q' or ESC to exit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {frame_count / (datetime.now() - start_time).total_seconds():.1f}", 
                       (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 1)
            
            cv2.imshow(window_name, frame)
            frame_count += 1
            
            # Check duration
            if duration_ms > 0:
                if (datetime.now() - start_time).total_seconds() * 1000 >= duration_ms:
                    break
            
            # Check key press
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q') or key == 27:  # 'q' atau ESC
                break
        
        cv2.destroyAllWindows()
        logger.info("Preview ditutup")
    
    def release(self):
        """
        Release webcam dan close semua window.
        HARUS dipanggil sebelum program berakhir!
        """
        if self.is_opened:
            self.cap.release()
            self.is_opened = False
            logger.info("✓ Webcam released")
        
        cv2.destroyAllWindows()


# ============================================================================
# ADVANCED CAPTURE FEATURES
# ============================================================================

class WebcamCaptureWithROI(WebcamCapture):
    """
    Extended WebcamCapture dengan Region of Interest (ROI) selection.
    User dapat menentukan area yang ingin di-capture.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roi_points = []
        self.roi_mode = False
    
    def on_mouse_click(self, event, x, y, flags, param):
        """Mouse callback untuk ROI selection."""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.roi_points.append((x, y))
            if len(self.roi_points) == 2:
                self.roi_mode = False
    
    def select_roi(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Biarkan user memilih ROI dari webcam preview.
        
        Returns:
            Tuple[int, int, int, int]: (x1, y1, x2, y2) atau None
        """
        self.roi_points = []
        self.roi_mode = True
        window_name = "Pilih ROI (drag atau 2 klik)"
        
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.on_mouse_click)
        
        logger.info("Silakan drag untuk memilih ROI...")
        
        for frame in self.get_frames():
            cv2.imshow(window_name, frame)
            
            if len(self.roi_points) == 2:
                break
            
            key = cv2.waitKey(30) & 0xFF
            if key == 27:  # ESC
                break
        
        cv2.destroyAllWindows()
        
        if len(self.roi_points) == 2:
            x1, y1 = self.roi_points[0]
            x2, y2 = self.roi_points[1]
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        
        return None
    
    def capture_with_roi(self, roi: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Capture frame dengan ROI tertentu.
        
        Args:
            roi (Tuple): (x1, y1, x2, y2)
        
        Returns:
            Optional[np.ndarray]: Cropped frame
        """
        frame = self.get_frame()
        if frame is None:
            return None
        
        x1, y1, x2, y2 = roi
        cropped = frame[y1:y2, x1:x2]
        
        logger.info(f"✓ Frame di-crop: {cropped.shape}")
        return cropped


# ============================================================================
# BATCH CAPTURE UTILITIES
# ============================================================================

def capture_multiple_from_webcam(num_frames: int = 4, 
                                 delay_ms: int = 1000,
                                 save: bool = True) -> list:
    """
    Capture beberapa frame dari webcam dengan interval tertentu.
    Secara default setiap frame juga disimpan ke dalam folder output harian.

    Args:
        num_frames (int): Jumlah frame yang ingin di-capture
        delay_ms (int): Delay antar capture dalam millisecond
        save (bool): Jika True, setiap frame akan ditulis ke disk
    
    Returns:
        list: List of captured frames
    
    Example:
        >>> frames = capture_multiple_from_webcam(4, 1000)
        >>> print(f"Captured {len(frames)} frames")
    """
    webcam = WebcamCapture()
    frames = []
    
    logger.info(f"Prepare untuk capture {num_frames} frame...")
    
    for i in range(num_frames):
        logger.info(f"Capture frame {i+1}/{num_frames}...")
        frame = webcam.get_frame()
        
        if frame is not None:
            frames.append(frame)
            logger.info(f"✓ Frame {i+1} captured")
            # save immediately if requested
            if save:
                try:
                    dated = create_dated_folder()
                    fname = generate_filename("capture")
                    filepath = dated / fname
                    safe_write_image(str(filepath), frame, quality=config.OUTPUT_QUALITY)
                except Exception as e:
                    logger.error(f"Error saving captured frame: {e}")
        
        if delay_ms > 0 and i < num_frames - 1:
            import time
            time.sleep(delay_ms / 1000)
    
    webcam.release()
    logger.info(f"✓ Total {len(frames)} frames berhasil di-capture")
    
    return frames


def load_multiple_images_from_folder(folder_path: str) -> list:
    """
    Load semua gambar dari folder.
    
    Args:
        folder_path (str): Path ke folder
    
    Returns:
        list: List of loaded images
    
    Example:
        >>> images = load_multiple_images_from_folder("input/")
        >>> print(f"Loaded {len(images)} images")
    """
    folder = Path(folder_path)
    images = []
    
    if not folder.exists():
        logger.error(f"❌ Folder tidak ditemukan: {folder}")
        return images
    
    # Cari semua file gambar
    for ext in config.ACCEPTED_IMAGE_FORMATS:
        for img_path in folder.glob(f"*{ext}"):
            image = load_image_from_file(str(img_path))
            if image is not None:
                images.append((str(img_path), image))
    
    logger.info(f"✓ {len(images)} gambar berhasil dimuat dari {folder}")
    
    return images

# ============================================================================
