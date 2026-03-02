"""
================================================================================
KONFIGURASI SISTEM PENCATAT KEHADIRAN DIGITAL BERBASIS KARTU IDENTITAS
================================================================================

Modul ini berisi semua konstanta dan parameter konfigurasi yang digunakan
dalam Sistem SmartAttend untuk memastikan consistency di seluruh aplikasi.

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import os
from pathlib import Path

# ============================================================================
# KONFIGURASI DIREKTORI & PATH
# ============================================================================

# Dapatkan direktori root project
PROJECT_ROOT = Path(__file__).parent.absolute()

# Direktori input dan output
INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
COLLAGE_DIR = OUTPUT_DIR / "collages"
LOG_DIR = PROJECT_ROOT / "logs"

# Buat direktori jika belum ada
for directory in [INPUT_DIR, OUTPUT_DIR, COLLAGE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# KONFIGURASI GAMBAR & PEMROSESAN
# ============================================================================

# Dimensi kartu standar (pixel)
CARD_WIDTH = 400
CARD_HEIGHT = 250
CARD_ASPECT_RATIO = CARD_WIDTH / CARD_HEIGHT

# Format dan kualitas penyimpanan
OUTPUT_FORMAT = "jpg"
OUTPUT_QUALITY = 95  # 0-100, semakin tinggi semakin bagus tapi file lebih besar
RESIZE_INTERPOLATION = "LANCZOS4"  # Metode interpolasi: "LINEAR", "CUBIC", "LANCZOS4"

# ============================================================================
# KONFIGURASI ANNOTATION
# ============================================================================

# Watermark
WATERMARK_TEXT = "SmartAttend v1.0"
WATERMARK_POSITION = "bottom-right"  # top-left, top-right, bottom-left, bottom-right

# Border
BORDER_WIDTH = 3
BORDER_COLOR = (200, 200, 200)  # BGR format

# Timestamp
TIMESTAMP_FONT_SCALE = 0.5
TIMESTAMP_THICKNESS = 1
TIMESTAMP_COLOR = (0, 0, 0)  # BGR: Black
TIMESTAMP_BG_COLOR = (220, 220, 220)  # BGR: Light gray

# Watermark font
WATERMARK_FONT_SCALE = 0.4
WATERMARK_THICKNESS = 1
WATERMARK_COLOR = (150, 150, 150)  # BGR: Gray

# ============================================================================
# KONFIGURASI BRIGHTNESS & CONTRAST
# ============================================================================

# Range nilai yang disarankan
MIN_BRIGHTNESS = 40.0
MAX_BRIGHTNESS = 200.0
MIN_CONTRAST = 0.5
MAX_CONTRAST = 2.0

# Default adjustment jika mode otomatis
AUTO_BRIGHTNESS_ADJUST = False
AUTO_CONTRAST_ADJUST = False

# ============================================================================
# KONFIGURASI COLLAGE
# ============================================================================

# Layout collage
COLLAGE_GRID = (2, 2)  # 2x2 grid = 4 gambar
COLLAGE_SPACING = 10  # Jarak antar gambar (pixel)
COLLAGE_BACKGROUND_COLOR = (255, 255, 255)  # BGR: White

# Title collage
COLLAGE_TITLE_FONT_SCALE = 1.0
COLLAGE_TITLE_THICKNESS = 2
COLLAGE_TITLE_COLOR = (0, 0, 0)  # BGR: Black
COLLAGE_TITLE_BG_COLOR = (200, 220, 255)  # BGR: Light blue
COLLAGE_TITLE_HEIGHT = 60  # Tinggi area untuk title

# ============================================================================
# KONFIGURASI WEBCAM
# ============================================================================

WEBCAM_ID = 0  # ID kamera (0 untuk built-in camera)
WEBCAM_FRAME_WIDTH = 640
WEBCAM_FRAME_HEIGHT = 480
WEBCAM_FPS = 30
WEBCAM_FLIP_VERTICAL = False
WEBCAM_FLIP_HORIZONTAL = False

# ============================================================================
# KONFIGURASI FILE NAMING
# ============================================================================

# Format naming file: YYYYMMDD_HHMMSS_kartu.jpg
# Contoh: 20240115_083045_kartu.jpg
FILE_NAMING_FORMAT = "{timestamp}_{type}.{ext}"
FILE_TYPE_CARD = "kartu"
FILE_TYPE_COLLAGE = "summary"

# ============================================================================
# KONFIGURASI LOGGING
# ============================================================================

LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "smartattend.log"

# ============================================================================
# KONFIGURASI GUI TKINTER
# ============================================================================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
WINDOW_TITLE = "SmartAttend - Sistem Pencatat Kehadiran Digital"
BACKGROUND_COLOR = "#f0f0f0"
ACCENT_COLOR = "#2196F3"  # Blue
SUCCESS_COLOR = "#4CAF50"  # Green
ERROR_COLOR = "#F44336"   # Red

# Font
FONT_FAMILY = "Arial"
FONT_SIZE_TITLE = 18
FONT_SIZE_NORMAL = 12
FONT_SIZE_SMALL = 10

# ============================================================================
# KONFIGURASI VALIDASI
# ============================================================================

# Format file yang diterima
ACCEPTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

# Ukuran file maksimum (MB)
MAX_FILE_SIZE = 50

# Minimum dimensi gambar input (pixel)
MIN_IMAGE_WIDTH = 200
MIN_IMAGE_HEIGHT = 150

# ============================================================================
# PARAMETER PERFORMA
# ============================================================================

# Threading
USE_THREADING = True
MAX_WORKERS = 4

# Caching
ENABLE_CACHE = True
CACHE_SIZE_MB = 100

# ============================================================================
# PESAN & STRING KONSTANTA
# ============================================================================

MSG_SUCCESS_LOAD = "✓ Gambar berhasil dimuat"
MSG_SUCCESS_PROCESS = "✓ Proses gambar berhasil"
MSG_SUCCESS_SAVE = "✓ Gambar berhasil disimpan ke: {}"
MSG_SUCCESS_COLLAGE = "✓ Collage berhasil dibuat: {}"

MSG_ERROR_LOAD = "✗ Gagal membuka gambar: {}"
MSG_ERROR_FORMAT = "✗ Format gambar tidak didukung"
MSG_ERROR_SIZE = "✗ Ukuran gambar terlalu besar"
MSG_ERROR_DIMENSION = "✗ Dimensi gambar terlalu kecil"

# ============================================================================
# DEBUG MODE
# ============================================================================

DEBUG = False  # Set True untuk menampilkan debug info
VERBOSE = False  # Set True untuk output yang lebih detail
SAVE_INTERMEDIATE_RESULTS = False  # Simpan hasil intermediate (untuk debug)

# ============================================================================
