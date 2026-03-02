#!/usr/bin/env python3
# ============================================================
# SETUP IMAGES: Generate sample images for BAB 1
# ============================================================
# Deskripsi: Script untuk membuat dan mendownload gambar sample
#            yang digunakan dalam praktikum Bab 1
# ============================================================

import os
import urllib.request
import ssl
import sys

# Disable SSL verification untuk beberapa server
ssl._create_default_https_context = ssl._create_unverified_context

# Setup directory
DIR_SCRIPT = os.path.dirname(os.path.abspath(__file__))
DIR_DATA = os.path.join(DIR_SCRIPT, "data", "images")
DIR_OUTPUT = os.path.join(DIR_SCRIPT, "output")

# Buat folder yang diperlukan
os.makedirs(DIR_DATA, exist_ok=True)
os.makedirs(DIR_OUTPUT, exist_ok=True)

# Buat folder output untuk setiap program
for i in range(1, 8):
    os.makedirs(os.path.join(DIR_OUTPUT, f"output{i}"), exist_ok=True)

print("=" * 80)
print("SETUP IMAGES FOR BAB 1: PENDAHULUAN")
print("=" * 80)

# ============================================================
# IMAGE DEFINITIONS
# ============================================================

IMAGES_TO_DOWNLOAD = [
    ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=640", "portrait.jpg"),
    ("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=640", "landscape.jpg"),
    ("https://images.unsplash.com/photo-1486325212027-8081e485255e?w=640", "building.jpg"),
    ("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=640", "forest.jpg"),
    ("https://images.unsplash.com/photo-1525909002-1b05e0c869d8?w=640", "colorful.jpg"),
]

def download_images():
    """Download images dari URL."""
    print("\n[1/2] DOWNLOADING IMAGES...")
    
    sukses = 0
    gagal = 0
    
    for url, filename in IMAGES_TO_DOWNLOAD:
        filepath = os.path.join(DIR_DATA, filename)
        
        if os.path.exists(filepath):
            print(f"  [SKIP] {filename} sudah ada")
            sukses += 1
            continue
        
        try:
            print(f"  [DOWNLOAD] {filename}...", end=" ", flush=True)
            urllib.request.urlretrieve(url, filepath)
            size = os.path.getsize(filepath) / 1024
            print(f"OK ({size:.1f} KB)")
            sukses += 1
        except Exception as e:
            print(f"GAGAL ({str(e)[:50]})")
            gagal += 1
    
    print(f"  Download: {sukses} sukses, {gagal} gagal")
    return sukses > 0


def generate_synthetic_images():
    """Generate synthetic images using numpy and OpenCV."""
    print("\n[2/2] GENERATING SYNTHETIC IMAGES...")
    
    try:
        import numpy as np
        import cv2
    except ImportError:
        print("  [ERROR] numpy dan opencv-python diperlukan!")
        print("  Install dengan: pip install numpy opencv-python")
        return False
    
    generated = 0
    
    # 1. Color bars test pattern
    filepath = os.path.join(DIR_DATA, "color_bars.png")
    if not os.path.exists(filepath):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        colors = [
            [255, 255, 255], [0, 255, 255], [255, 255, 0], [0, 255, 0],
            [255, 0, 255], [0, 0, 255], [255, 0, 0], [0, 0, 0]
        ]
        bar_width = 640 // 8
        for i, c in enumerate(colors):
            img[:, i*bar_width:(i+1)*bar_width] = c
        cv2.imwrite(filepath, img)
        print(f"  [OK] color_bars.png")
        generated += 1
    
    # 2. Grayscale gradient
    filepath = os.path.join(DIR_DATA, "gradient.png")
    if not os.path.exists(filepath):
        img = np.zeros((256, 512), dtype=np.uint8)
        for i in range(256):
            img[i, :] = i
        cv2.imwrite(filepath, img)
        print(f"  [OK] gradient.png")
        generated += 1
    
    # 3. Checkerboard
    filepath = os.path.join(DIR_DATA, "checkerboard.png")
    if not os.path.exists(filepath):
        img = np.zeros((400, 400), dtype=np.uint8)
        for i in range(0, 400, 50):
            for j in range(0, 400, 50):
                if (i//50 + j//50) % 2:
                    img[i:i+50, j:j+50] = 255
        cv2.imwrite(filepath, img)
        print(f"  [OK] checkerboard.png")
        generated += 1
    
    # 4. Shapes demo
    filepath = os.path.join(DIR_DATA, "shapes_demo.png")
    if not os.path.exists(filepath):
        img = np.zeros((400, 600, 3), dtype=np.uint8)
        # Background
        for i in range(400):
            img[i, :] = [int(i/2), int(100 + i/4), int(200 - i/4)]
        # Shapes
        cv2.rectangle(img, (50, 50), (150, 150), (255, 255, 255), -1)
        cv2.circle(img, (300, 100), 50, (0, 255, 255), -1)
        cv2.line(img, (400, 50), (550, 150), (255, 0, 0), 3)
        cv2.putText(img, "OpenCV", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.5, (255, 255, 255), 2)
        cv2.imwrite(filepath, img)
        print(f"  [OK] shapes_demo.png")
        generated += 1
    
    # 5. Sample portrait jika download gagal
    filepath = os.path.join(DIR_DATA, "portrait.jpg")
    if not os.path.exists(filepath):
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        # Skin tone background
        img[:, :] = [180, 200, 230]
        # Face shape
        cv2.ellipse(img, (256, 256), (150, 200), 0, 0, 360, (160, 180, 210), -1)
        # Eyes
        cv2.circle(img, (200, 220), 25, (50, 50, 50), -1)
        cv2.circle(img, (312, 220), 25, (50, 50, 50), -1)
        cv2.circle(img, (200, 220), 10, (255, 255, 255), -1)
        cv2.circle(img, (312, 220), 10, (255, 255, 255), -1)
        # Nose
        cv2.line(img, (256, 240), (256, 290), (120, 140, 170), 3)
        # Mouth
        cv2.ellipse(img, (256, 340), (50, 20), 0, 0, 180, (100, 100, 200), -1)
        cv2.imwrite(filepath, img)
        print(f"  [OK] portrait.jpg (synthetic)")
        generated += 1
    
    print(f"  Generated: {generated} images")
    return True


def main():
    """Main setup function."""
    print(f"\nDirectory: {DIR_SCRIPT}")
    print(f"Data folder: {DIR_DATA}")
    print(f"Output folder: {DIR_OUTPUT}\n")
    
    # Download images
    download_images()
    
    # Generate synthetic images
    generate_synthetic_images()
    
    # List final images
    print("\n" + "=" * 80)
    print("GAMBAR YANG TERSEDIA")
    print("=" * 80)
    
    if os.path.exists(DIR_DATA):
        files = sorted(os.listdir(DIR_DATA))
        for f in files:
            size = os.path.getsize(os.path.join(DIR_DATA, f)) / 1024
            print(f"  {f:30} ({size:.1f} KB)")
        print(f"\nTotal: {len(files)} files")
    
    print("\n" + "=" * 80)
    print("✅ SETUP COMPLETE!")
    print("=" * 80)
    print("\nSekarang Anda bisa menjalankan program praktikum:")
    print("  python3 01_loading_gambar.py")
    print("  python3 run_all_tests.py  (untuk test semua program)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
