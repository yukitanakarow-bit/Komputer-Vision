"""
Quick Test Script untuk Validasi Fix Resize
"""

import cv2
import numpy as np
from pathlib import Path

# Import modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

from process_module import resize_card_standard
from utils import safe_write_image, create_dated_folder

def test_resize_with_various_inputs():
    """Test resize dengan berbagai input sizes."""
    
    print("\n" + "="*60)
    print("TEST: Resize Function dengan Berbagai Input Sizes")
    print("="*60)
    
    test_cases = [
        ("Wide image", (300, 800, 3)),      # Aspect ratio tinggi (wide)
        ("Tall image", (800, 300, 3)),       # Aspect ratio rendah (tall)
        ("Square image", (400, 400, 3)),     # Square
        ("Large image", (1080, 1080, 3)),    # Large
        ("Small image", (100, 100, 3)),      # Small
    ]
    
    for name, shape in test_cases:
        print(f"\n🧪 Testing: {name}")
        print(f"   Input shape: {shape}")
        
        try:
            # Create dummy image
            img = np.random.randint(0, 256, shape, dtype=np.uint8)
            
            # Resize
            resized = resize_card_standard(img)
            
            print(f"   ✓ Output shape: {resized.shape}")
            print(f"   ✓ Success!")
            
            # Validate output
            assert resized.shape[0] == 250, f"Height should be 250, got {resized.shape[0]}"
            assert resized.shape[1] == 400, f"Width should be 400, got {resized.shape[1]}"
            assert resized.shape[2] == 3, f"Channels should be 3, got {resized.shape[2]}"
        
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

def test_with_real_image():
    """Test dengan gambar asli."""
    
    print("\n" + "="*60)
    print("TEST: With Real Image")
    print("="*60)
    
    input_dir = Path(__file__).parent / "input"
    image_files = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
    
    if len(image_files) == 0:
        print("⚠️  Tidak ada image di folder input/")
        print("💡 Tip: Silakan copy sample gambar ke folder input/ untuk test ini")
        return
    
    for image_path in image_files[:2]:  # Test 2 gambar pertama
        print(f"\n📷 Testing: {image_path.name}")
        
        try:
            img = cv2.imread(str(image_path))
            print(f"   Input shape: {img.shape}")
            
            resized = resize_card_standard(img)
            print(f"   Output shape: {resized.shape}")
            
            # Save untuk verify
            output_dir = create_dated_folder()
            output_path = output_dir / f"test_{image_path.stem}_resized.jpg"
            safe_write_image(str(output_path), resized)
            
            print(f"   ✓ Saved to: {output_path}")
            
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SmartAttend - Resize Function Test Suite")
    print("="*60)
    
    print("\n✓ Testing with dummy images...")
    test_resize_with_various_inputs()
    
    print("\n✓ Testing with real image (if available)...")
    test_with_real_image()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
