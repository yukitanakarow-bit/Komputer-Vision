"""
================================================================================
CONTOH PENGGUNAAN - SIMPLE EXAMPLES
================================================================================

File ini berisi berbagai contoh penggunaan SmartAttend untuk memudahkan
pemahaman terhadap setiap fitur.

Jalankan dengan: python simple_examples.py

Author: Tim SmartAttend
Date: 2024
================================================================================
"""

import cv2
from pathlib import Path

import config
from capture_module import (load_image_from_file, WebcamCapture, 
                           capture_multiple_from_webcam, load_multiple_images_from_folder)
from process_module import (process_card_image, convert_color_space, ColorSpace,
                           resize_card_standard, add_border, add_timestamp,
                           add_watermark, equalize_histogram)
from utils import (logger, safe_write_image, create_dated_folder, 
                  generate_filename, get_image_info, get_image_brightness)

# ============================================================================
# EXAMPLE 1: Load dan tampilkan gambar dari file
# ============================================================================

def example_1_load_image():
    """
    Example 1: Load gambar dari file dan tampilkan di window.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Load Gambar dari File")
    print("="*60)
    
    # Path ke gambar
    image_path = "input/sample_kartu.jpg"
    
    # Check apakah file ada
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        print("💡 Silakan copy sample gambar ke folder 'input/'")
        return
    
    # Load gambar
    image = load_image_from_file(image_path)
    
    if image is not None:
        # Tampilkan info
        info = get_image_info(image)
        print(f"\n✓ Gambar berhasil dimuat!")
        print(f"  → Dimensi: {info['width']}x{info['height']}")
        print(f"  → Channels: {info['channels']}")
        print(f"  → Size: {info['size_mb']:.2f} MB")
        
        # Tampilkan di window
        cv2.imshow("Original Image", image)
        print("\n💡 Tekan ESC untuk menutup window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 2: Resize gambar ke ukuran standar
# ============================================================================

def example_2_resize_image():
    """
    Example 2: Resize gambar ke ukuran kartu standar (400x250).
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Resize Gambar ke Ukuran Standar")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    # Load gambar
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    print(f"\nOriginal dimension: {image.shape[1]}x{image.shape[0]}")
    
    # Resize
    resized = resize_card_standard(image)
    
    print(f"Resized dimension: {resized.shape[1]}x{resized.shape[0]}")
    print(f"✓ Gambar berhasil di-resize dengan aspect ratio terjaga")
    
    # Tampilkan comparison
    cv2.imshow("Original", cv2.resize(image, (400, 300)))
    cv2.imshow("Resized (standardized)", cv2.resize(resized, (400, 300)))
    print("\n💡 Tekan ESC untuk menutup window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 3: Tambahkan border
# ============================================================================

def example_3_add_border():
    """
    Example 3: Tambahkan border/frame ke gambar.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Tambahkan Border ke Gambar")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    # Resize dulu
    resized = resize_card_standard(image)
    
    # Tambah border
    bordered = add_border(resized, thickness=5, color=(0, 0, 0))
    
    print("✓ Border berhasil ditambahkan")
    print(f"  → Original: {resized.shape}")
    print(f"  → With border: {bordered.shape}")
    
    cv2.imshow("With Border", cv2.resize(bordered, (400, 300)))
    print("\n💡 Tekan ESC untuk menutup window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 4: Tambahkan timestamp & watermark
# ============================================================================

def example_4_add_annotation():
    """
    Example 4: Tambahkan timestamp dan watermark.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Tambahkan Timestamp & Watermark")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    # Resize
    resized = resize_card_standard(image)
    
    # Tambah border
    bordered = add_border(resized)
    
    # Tambah timestamp
    with_ts = add_timestamp(bordered)
    
    # Tambah watermark
    with_wm = add_watermark(with_ts)
    
    print("✓ Timestamp dan watermark berhasil ditambahkan")
    
    cv2.imshow("With Annotation", cv2.resize(with_wm, (400, 300)))
    print("\n💡 Tekan ESC untuk menutup window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 5: Full processing pipeline
# ============================================================================

def example_5_full_processing():
    """
    Example 5: Full processing pipeline dari load hingga save.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Full Processing Pipeline")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    # Load
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    # Full processing
    print("\nMemulai full processing...")
    processed = process_card_image(
        image,
        add_ts=True,
        add_wm=True,
        add_frame=True,
        auto_enhance_flag=False,
        brightness=0,
        contrast=1.0
    )
    
    print("✓ Processing selesai")
    
    # Save
    dated_folder = create_dated_folder()
    filename = generate_filename("kartu")
    filepath = dated_folder / filename
    
    if safe_write_image(str(filepath), processed, quality=config.OUTPUT_QUALITY):
        print(f"✓ Gambar disimpan ke: {filepath}")
    
    # Tampilkan
    cv2.imshow("Processed Result", cv2.resize(processed, (400, 300)))
    print("\n💡 Tekan ESC untuk menutup window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 6: Convert color space
# ============================================================================

def example_6_color_conversion():
    """
    Example 6: Konversi antar color space.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Color Space Conversion")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    # Konversi ke berbagai color space
    gray = convert_color_space(image, ColorSpace.GRAY)
    rgb = convert_color_space(image, ColorSpace.RGB)
    hsv = convert_color_space(image, ColorSpace.HSV)
    
    print("✓ Konversi color space berhasil")
    print(f"  → Grayscale shape: {gray.shape}")
    print(f"  → RGB shape: {rgb.shape}")
    print(f"  → HSV shape: {hsv.shape}")
    
    # Tampilkan comparison
    cv2.imshow("Original (BGR)", cv2.resize(image, (300, 200)))
    cv2.imshow("Grayscale", cv2.resize(gray, (300, 200)))
    cv2.imshow("Equalized", cv2.resize(equalize_histogram(gray), (300, 200)))
    
    print("\n💡 Tekan ESC untuk menutup window...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ============================================================================
# EXAMPLE 7: Batch processing dari folder
# ============================================================================

def example_7_batch_processing():
    """
    Example 7: Batch processing dari multiple images.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Batch Processing dari Folder")
    print("="*60)
    
    image_folder = "input"
    
    # Load semua gambar dari folder
    images = load_multiple_images_from_folder(image_folder)
    
    if len(images) == 0:
        print(f"⚠️  Tidak ada gambar di folder '{image_folder}'")
        return
    
    print(f"\n✓ {len(images)} gambar dimuat")
    
    # Process semua
    dated_folder = create_dated_folder()
    
    for idx, (filepath, image) in enumerate(images, 1):
        print(f"\nProcessing {idx}/{len(images)}: {Path(filepath).name}")
        
        # Process
        processed = process_card_image(image)
        
        # Save
        filename = f"{idx:02d}_{generate_filename('batch')}"
        save_path = dated_folder / filename
        safe_write_image(str(save_path), processed)
        
        print(f"  ✓ Disimpan ke: {filename}")
    
    print(f"\n✓ Batch processing selesai!")
    print(f"  → Output folder: {dated_folder}")

# ============================================================================
# EXAMPLE 8: Webcam capture
# ============================================================================

def example_8_webcam_capture():
    """
    Example 8: Capture dari webcam.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Webcam Capture")
    print("="*60)
    
    try:
        # Inisialisasi webcam
        webcam = WebcamCapture()
        
        if not webcam.is_opened:
            print("❌ Webcam tidak dapat dibuka")
            return
        
        print("✓ Webcam terbuka")
        print("💡 Tekan 'ESC' atau 'q' untuk capture dan lanjut...")
        
        # Capture single frame
        frame = webcam.capture_single_frame()
        
        if frame is not None:
            # Process
            processed = process_card_image(frame)
            
            # Save
            dated_folder = create_dated_folder()
            filename = generate_filename("webcam")
            filepath = dated_folder / filename
            safe_write_image(str(filepath), processed)
            
            print(f"✓ Frame disimpan ke: {filepath}")
            
            # Tamppilkan
            cv2.imshow("Captured & Processed", cv2.resize(processed, (400, 300)))
            print("\n💡 Tekan ESC untuk menutup window...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        webcam.release()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# ============================================================================
# EXAMPLE 9: Get image statistics
# ============================================================================

def example_9_image_statistics():
    """
    Example 9: Dapatkan statistik gambar.
    """
    print("\n" + "="*60)
    print("EXAMPLE 9: Image Statistics")
    print("="*60)
    
    image_path = "input/sample_kartu.jpg"
    if not Path(image_path).exists():
        print(f"⚠️  File tidak ditemukan: {image_path}")
        return
    
    image = load_image_from_file(image_path)
    if image is None:
        return
    
    # Get info
    info = get_image_info(image)
    brightness = get_image_brightness(image)
    
    print("\n📊 Image Statistics:")
    print(f"  → Width: {info['width']} px")
    print(f"  → Height: {info['height']} px")
    print(f"  → Aspect Ratio: {info['aspect_ratio']:.2f}")
    print(f"  → Channels: {info['channels']}")
    print(f"  → Data Type: {info['dtype']}")
    print(f"  → Size: {info['size_mb']:.2f} MB")
    print(f"  → Brightness (0-255): {brightness:.1f}")

# ============================================================================
# MAIN MENU
# ============================================================================

def main():
    """Main menu untuk memilih example."""
    print("\n" + "="*60)
    print("   SMARTATTEND - SIMPLE EXAMPLES")
    print("="*60)
    
    examples = {
        "1": ("Load Image from File", example_1_load_image),
        "2": ("Resize Image", example_2_resize_image),
        "3": ("Add Border", example_3_add_border),
        "4": ("Add Annotation", example_4_add_annotation),
        "5": ("Full Processing Pipeline", example_5_full_processing),
        "6": ("Color Space Conversion", example_6_color_conversion),
        "7": ("Batch Processing", example_7_batch_processing),
        "8": ("Webcam Capture", example_8_webcam_capture),
        "9": ("Image Statistics", example_9_image_statistics),
    }
    
    print("\nPilih example untuk menjalankan:")
    for key, (title, _) in examples.items():
        print(f"  {key}. {title}")
    print("  0. Exit")
    
    while True:
        choice = input("\nMasukkan pilihan (0-9): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        
        if choice in examples:
            title, func = examples[choice]
            print(f"\n▶️  Menjalankan: {title}")
            try:
                func()
                print()
            
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
        else:
            print("❌ Pilihan tidak valid!")

if __name__ == "__main__":
    main()

# ============================================================================
