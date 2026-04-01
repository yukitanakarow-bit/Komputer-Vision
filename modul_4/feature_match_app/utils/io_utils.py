"""
utils/io_utils.py
Fungsi utilitas untuk input/output file gambar dan data.
"""

import cv2
import os
import numpy as np


def load_image(path, grayscale=False):
    """
    Muat gambar dari path dengan error handling.

    Args:
        path: Path ke file gambar
        grayscale: Jika True, muat sebagai grayscale

    Returns:
        Gambar (numpy array) atau None jika gagal
    """
    if not os.path.exists(path):
        print(f"[ERROR] File tidak ditemukan: {path}")
        return None

    flag = cv2.IMREAD_GRAYSCALE if grayscale else cv2.IMREAD_COLOR
    img = cv2.imread(path, flag)

    if img is None:
        print(f"[ERROR] Gagal membaca gambar: {path}")
        return None

    return img


def load_images_from_folder(folder, grayscale=False, extensions=('.jpg', '.jpeg', '.png', '.bmp')):
    """
    Muat semua gambar dari sebuah folder.

    Args:
        folder: Path folder
        grayscale: Muat sebagai grayscale
        extensions: Tuple ekstensi yang diizinkan

    Returns:
        Dict {nama_file: gambar}
    """
    images = {}
    if not os.path.exists(folder):
        print(f"[WARN] Folder tidak ditemukan: {folder}")
        return images

    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith(extensions):
            path = os.path.join(folder, fname)
            img = load_image(path, grayscale)
            if img is not None:
                images[fname] = img

    print(f"[INFO] Loaded {len(images)} gambar dari {folder}")
    return images


def save_image(image, path):
    """
    Simpan gambar ke path dengan membuat folder jika perlu.

    Args:
        image: Gambar (numpy array)
        path: Path tujuan
    """
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    success = cv2.imwrite(path, image)
    if success:
        print(f"[INFO] Gambar disimpan: {path}")
    else:
        print(f"[ERROR] Gagal menyimpan gambar: {path}")
    return success


def ensure_dir(path):
    """Pastikan direktori ada, buat jika belum ada."""
    os.makedirs(path, exist_ok=True)
    return path
