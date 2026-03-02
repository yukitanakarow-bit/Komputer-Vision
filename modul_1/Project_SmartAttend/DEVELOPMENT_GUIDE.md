# 🛠️ DEVELOPMENT GUIDE - SmartAttend

Panduan lengkap untuk developer yang ingin extend atau customize SmartAttend.

## 📐 Project Architecture

### Module Dependency Graph:

```
┌──────────────────────────────────────────────────────────────┐
│                   main.py (GUI Layer)                        │
│              ▲                             ▲                 │
│              │ (uses)                      │ (uses)           │
│              │                             │                 │
│   ┌──────────▼─────────────┐    ┌────────▼──────────────┐    │
│   │ capture_module.py       │    │ process_module.py     │    │
│   │ - load_image_from_file  │    │ - resize_card        │    │
│   │ - WebcamCapture         │    │ - add_timestamp      │    │
│   │ - capture_batch         │    │ - add_watermark      │    │
│   │                         │    │ - add_border         │    │
│   └────────────┬────────────┘    └────────┬─────────────┘    │
│                │                          │                  │
│                │ (uses)                   │ (uses)          │
│                └──────────────┬───────────┘                  │
│                               ▼                              │
│                        ┌──────────────┐                      │
│                        │  utils.py    │                      │
│                        │ - File I/O   │                      │
│                        │ - Logging    │                      │
│                        │ - Validation │                      │
│                        └──────────────┘                      │
│                               ▲                              │
│                               │ (uses)                       │
│                        ┌──────▼────────┐                     │
│                        │  config.py    │                     │
│                        │ (Constants)   │                     │
│                        └───────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

## 🎨 Module Roles

### config.py
**Fungsi**: Centralized configuration & constants

```python
# Contoh menambah parameter baru:
ADD_SHADOW_EFFECT = True           # Fitur baru
SHADOW_INTENSITY = 0.3             # Parameter baru
SAVE_DEBUG_IMAGES = False          # Debug flag
```

### utils.py
**Fungsi**: Utility functions & helpers

```python
# Contoh menambah fungsi baru:
def add_shadow_effect(image, intensity=0.5):
    """Add shadow effect untuk depth."""
    shadow = cv2.GaussianBlur(image, (21, 21), 0)
    return cv2.addWeighted(image, 1-intensity, shadow, intensity, 0)
```

### capture_module.py
**Fungsi**: Semua operasi input (load file, webcam)

```python
# Contoh class baru untuk advanced capture:
class AdvancedWebcamCapture(WebcamCapture):
    """Extended webcam dengan motion detection."""
    
    def detect_motion(self):
        """Detect gerakan untuk auto-capture."""
        # Implementation
        pass
```

### process_module.py
**Fungsi**: Semua operasi image processing

```python
# Contoh fungsi baru:
def add_shadow_effect(image, intensity=config.SHADOW_INTENSITY):
    """Apply shadow effect untuk kedalaman."""
    # Implementation
    pass

# Tambahkan ke process_card_image():
if add_shadow:
    result = add_shadow_effect(result)
```

### main.py
**Fungsi**: GUI & orchestration

```python
# Contoh menambah fitur baru di GUI:
def advanced_filter_dialog(self):
    """Open dialog untuk advanced filters."""
    # Ask user for parameters
    # Apply filters
    # Update preview
    pass
```

---

## 🔧 Cara Extend Project

### Scenario 1: Tambah Fitur Filter Baru

**Step 1**: Buat fungsi di `process_module.py`

```python
def apply_blur(image, kernel_size=5):
    """Apply Gaussian blur."""
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

def apply_edge_detection(image):
    """Apply Canny edge detection."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
```

**Step 2**: Update `config.py` jika ada parameter

```python
# Add ke config.py
BLUR_KERNEL_SIZE = 5
EDGE_THRESHOLD_LOW = 100
EDGE_THRESHOLD_HIGH = 200
```

**Step 3**: Add ke GUI di `main.py`

```python
# Di setup_ui()
ttk.Checkbutton(process_frame, text="✓ Apply Blur", 
               variable=self.var_blur).pack(anchor=tk.W, padx=5, pady=3)

# Di process_image()
if self.var_blur.get():
    self.current_processed = apply_blur(self.current_processed)
```

**Step 4**: Test

```python
# Test di simple_examples.py
def example_10_blur_filter():
    image = load_image_from_file("input/sample_kartu.jpg")
    blurred = apply_blur(image, kernel_size=7)
    cv2.imshow("Blurred", blurred)
    cv2.waitKey(0)
```

### Scenario 2: Tambah Fitur Deteksi Wajah

**Step 1**: Install dependency

```bash
pip install dlib face-recognition
```

**Step 2**: Buat module baru `face_detection.py`

```python
"""Face detection & recognition module."""
import face_recognition
import numpy as np

def detect_face(image):
    """Detect wajah dalam gambar."""
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)
    return face_locations

def crop_face(image, face_location):
    """Crop area wajah."""
    top, right, bottom, left = face_location
    return image[top:bottom, left:right]

def auto_crop_to_face(image):
    """Otomatis crop fokus ke wajah."""
    faces = detect_face(image)
    if len(faces) > 0:
        return crop_face(image, faces[0])
    return image  # No face detected
```

**Step 3**: Integrate ke main

```python
# Di process_module.py
def process_card_image(..., crop_to_face=False):
    result = image.copy()
    
    if crop_to_face:
        from face_detection import auto_crop_to_face
        result = auto_crop_to_face(result)
    
    # Continue dengan yang lain...
```

### Scenario 3: Tambah Database Integration

**Step 1**: Create `database.py`

```python
"""Database integration module."""
import sqlite3
from datetime import datetime

class AttendanceDB:
    """SQLite database untuk attendance records."""
    
    def __init__(self, db_file="attendance.db"):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                user_id TEXT,
                timestamp DATETIME,
                image_path TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_attendance(self, user_id, image_path, status="present"):
        """Log attendance record."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attendance (user_id, timestamp, image_path, status)
            VALUES (?, ?, ?, ?)
        ''', (user_id, datetime.now(), image_path, status))
        
        conn.commit()
        conn.close()
    
    def get_records(self, date):
        """Get attendance for specific date."""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM attendance WHERE DATE(timestamp) = ?
        ''', (date,))
        
        records = cursor.fetchall()
        conn.close()
        
        return records
```

**Step 2**: Use di main.py

```python
from database import AttendanceDB

class SmartAttendGUI:
    def __init__(self, root):
        # ... existing code ...
        self.db = AttendanceDB()
    
    def save_image(self):
        # ... existing save code ...
        
        # Log ke database
        self.db.log_attendance(
            user_id=self.user_id_var.get(),
            image_path=str(filepath),
            status="present"
        )
```

---

## 🧪 Testing & Quality Assurance

### Unit Testing Example

Create `test_process_module.py`:

```python
import unittest
import cv2
import numpy as np
from process_module import resize_card_standard, add_border

class TestProcessModule(unittest.TestCase):
    
    def setUp(self):
        """Setup test fixtures."""
        self.sample_image = np.random.randint(0, 256, (300, 400, 3), dtype=np.uint8)
    
    def test_resize_card_standard(self):
        """Test resize ke ukuran standar."""
        result = resize_card_standard(self.sample_image)
        
        self.assertEqual(result.shape[0], 250)  # Height
        self.assertEqual(result.shape[1], 400)  # Width
        self.assertEqual(result.shape[2], 3)    # Channels
    
    def test_add_border(self):
        """Test border addition."""
        result = add_border(self.sample_image, thickness=5)
        
        self.assertEqual(result.shape[0], self.sample_image.shape[0] + 10)
        self.assertEqual(result.shape[1], self.sample_image.shape[1] + 10)

if __name__ == '__main__':
    unittest.main()
```

Run tests:

```bash
python -m pytest test_process_module.py -v
# atau
python -m unittest test_process_module.py
```

---

## 📊 Performance Optimization

### Profile Code

```python
import cProfile
import pstats
from io import StringIO

# Profile processing
pr = cProfile.Profile()
pr.enable()

processed = process_card_image(image)

pr.disable()
s = StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats()
print(s.getvalue())
```

### Optimize Slow Functions

```python
# Sebelum: Slow
def process_image_slow(image):
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            image[i, j] = image[i, j] * 1.2

# Sesudah: Fast (vectorized)
def process_image_fast(image):
    return cv2.convertScaleAbs(image, alpha=1.2, beta=0)
```

---

## 🐛 Debugging Tips

### Enable Debug Mode

```python
# config.py
DEBUG = True
VERBOSE = True
SAVE_INTERMEDIATE_RESULTS = True
```

### Add Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Processing image: {image.shape}")
logger.info("Image processed successfully")
logger.warning("Image quality may be affected")
logger.error("Failed to process image")
```

### Save Intermediate Results

```python
if config.SAVE_INTERMEDIATE_RESULTS:
    cv2.imwrite("debug/01_original.jpg", image)
    cv2.imwrite("debug/02_resized.jpg", resized)
    cv2.imwrite("debug/03_bordered.jpg", bordered)
    cv2.imwrite("debug/04_final.jpg", processed)
```

---

## 🚀 Deployment

### Create Executable (Windows)

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed main.py

# Result di: dist/main.exe
```

### Create Package

```bash
# Create setup.py
python setup.py sdist bdist_wheel

# Upload ke PyPI
pip install twine
twine upload dist/*
```

---

## 📚 Code Style Guide

### Follow PEP 8

```python
# Good
def add_border(image, thickness=5, color=(0, 0, 0)):
    """Add border to image."""
    # Implementation
    return result

# Bad
def addBorder(img,t=5,c=(0,0,0)):
    #Add border
    return result
```

### Documentation

Every function harus punya docstring:

```python
def resize_card_standard(image: np.ndarray,
                        width: int = 400,
                        height: int = 250) -> np.ndarray:
    """
    Resize gambar ke ukuran standar kartu.
    
    Args:
        image (np.ndarray): Input image (BGR)
        width (int): Target width in pixels
        height (int): Target height in pixels
    
    Returns:
        np.ndarray: Resized image dengan dimensions (height, width, 3)
    
    Example:
        >>> img = cv2.imread("photo.jpg")
        >>> resized = resize_card_standard(img)
    """
    # Implementation
    pass
```

---

## 📋 Checklist untuk Extension

- [ ] Buat fungsi baru di modul yang sesuai
- [ ] Add parameter ke `config.py` kalau perlu
- [ ] Add docstring komprehensif
- [ ] Test dengan berbagai input
- [ ] Add ke GUI kalau user-facing
- [ ] Update README documentation
- [ ] Add example di `simple_examples.py`
- [ ] Check code style (PEP 8)
- [ ] Performance check
- [ ] Error handling lengkap

---

## 🎓 Learning Path

Untuk developer yang ingin master SmartAttend:

1. **Pemula** (1-2 hari)
   - Read QUICK_START.md
   - Run simple_examples.py
   - Understand file structure

2. **Intermediate** (1 minggu)
   - Modify config parameters
   - Run main.py dan explore GUI
   - Add simple filter (Scenario 1)

3. **Advanced** (2-3 minggu)
   - Implement face detection (Scenario 2)
   - Add database integration (Scenario 3)
   - Write unit tests
   - Create executable

4. **Expert** (4+ minggu)
   - Optimize performance
   - Deploy to production
   - Contribute improvements
   - Mentor developers baru

---

## 📞 Contributing

Untuk contribute ke project:

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 🎉 Tips Sukses Development

✅ **DO:**
- Write clean, readable code
- Add comments & docstrings
- Test thoroughly
- Keep backward compatibility
- Update documentation
- Ask for help when stuck

❌ **DON'T:**
- Hardcode values (use config)
- Ignore error cases
- Write massive functions (break into smaller ones)
- Skip documentation
- Modify others' code without discussion

---

**Happy Developing!** 🚀

*Remember: Good code is not just about functionality,*  
*it's about clarity, maintainability, and elegance.*

---

*Last Updated: 2024-01-15*  
*Version: 1.0.0*
