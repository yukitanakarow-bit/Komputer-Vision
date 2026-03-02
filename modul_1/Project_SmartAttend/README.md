# 📱 SMARTATTEND - Sistem Pencatat Kehadiran Digital

## 🎯 Deskripsi Project

**SmartAttend** adalah sebuah sistem pencatatan kehadiran digital berbasis kartu identitas yang mengotomasi proses capture dan pemrosesan foto kartu identitas siswa/pegawai. Sistem ini dirancang untuk menggantikan sistem absensi manual yang masih banyak digunakan di sekolah-sekolah.

### Fitur Utama:
✅ **Load & Capture Image** - Load gambar dari file atau capture dari webcam  
✅ **Image Processing** - Resize standar, enhance kualitas, adjustment brightness/contrast  
✅ **Annotation** - Tambahkan timestamp, watermark, dan border  
✅ **Smart Storage** - Organisasi folder berdasarkan tanggal dengan naming standard  
✅ **Collage Generator** - Buat preview collage 2x2 dari 4 gambar  
✅ **GUI Interface** - User-friendly Tkinter GUI dengan preview real-time  
✅ **Batch Processing** - Proses multiple gambar sekaligus  

---

## 📋 Project Structure

```
Project_SmartAttend/
├── main.py                  # Program utama dengan GUI Tkinter
├── config.py               # Konfigurasi & konstanta
├── utils.py                # Fungsi-fungsi utility & helper
├── capture_module.py       # Modul capture gambar
├── process_module.py       # Modul image processing
│
├── input/                  # Folder untuk gambar input
│   └── sample_kartu.jpg
│
├── output/                 # Folder untuk output hasil
│   ├── 2024-01-15/        # Organisasi per tanggal
│   │   ├── 20240115_083045_kartu.jpg
│   │   └── ...
│   └── collages/          # Folder untuk collage
│       └── summary_20240115_083045.jpg
│
├── logs/                   # Folder untuk log files
│   └── smartattend.log
│
└── README.md              # File dokumentasi ini
```

---

## 🚀 Instalasi & Setup

### Prasyarat:
- Python 3.8 atau lebih baru
- pip (Python package manager)
- Webcam (optional, hanya jika ingin capture dari kamera)

### Langkah Instalasi:

#### 1. Clone atau Download Project
```bash
# Jika menggunakan git
git clone <repo-url>
cd Project_SmartAttend

# Atau ekstrak dari ZIP file
```

#### 2. Install Dependencies
```bash
# Install semua library yang diperlukan
pip install -r requirements.txt

# Atau install manual
pip install opencv-python numpy matplotlib pillow
```

#### 3. Verifikasi Instalasi
```bash
# Jalankan test untuk memastikan semua library terinstall dengan benar
python -c "import cv2, numpy, PIL; print('✓ All libraries installed!')"
```

---

## 📖 Cara Penggunaan

### Opsi 1: Menggunakan GUI (Recommended)

#### Menjalankan Program:
```bash
python main.py
```

#### Menggunakan Interface:

**1. Load Gambar dari File:**
- Klik tombol "📂 Buka Gambar dari File"
- Pilih gambar dari folder (format: JPG, PNG, BMP)
- Gambar akan ditampilkan di panel preview kanan

**2. Capture dari Webcam:**
```
Opsi A: Single Capture
- Klik "📸 Capture Webacm (1 frame)"
- Sistem akan capture 1 frame dari webcam Anda

Opsi B: Batch Capture (4 frames)
- Klik "📷 Capture Batch (4 frames)"
- Sistem akan capture 4 frame dengan interval 1 detik
- Berikan posisi kartu berbeda untuk setiap capture

Opsi C: Preview Webcam
- Klik "📷 Buka Webcam"
- Lihat preview real-time dari webcam
- Tekan 'q' atau ESC untuk menutup preview
```

**3. Process Gambar:**
- Atur opsi pemrosesan di panel kiri:
  - ✓ Timestamp: Tampilkan waktu pengambilan
  - ✓ Watermark: Tambahkan logo SmartAttend
  - ✓ Border: Tambahkan frame di sekitar gambar
  - ✓ Auto Enhancement: Otomatis perbaiki kualitas
  - Brightness: Sesuaikan kecerahan (-50 hingga 50)
  - Contrast: Sesuaikan kontras (0.5 hingga 3.0)
- Klik "🔄 Process Gambar"
- Hasil akan tampil di panel processed image

**4. Simpan Gambar:**
- Klik "💾 Simpan Gambar"
- Gambar akan disimpan ke folder `output/YYYY-MM-DD/`
- Nama file format: `YYYYMMDD_HHMMSS_kartu.jpg`

**5. Buat Collage:**

Opsi A: Simple Collage (2x2)
```
- Capture atau load minimal 4 gambar
- Klik "🎨 Buat Collage 2x2"
- Akan menggunakan 4 gambar pertama
- Disimpan ke output dengan nama `summary_YYYYMMDD_HHMMSS.jpg`
```

Opsi B: Batch Collage
```
- Load atau capture banyak gambar (ex: 8, 12, 16 gambar)
- Klik "📊 Buat Collage Batch"
- Akan membuat multiple collage 2x2
- Contoh: 12 gambar = 3 collage
```

### Opsi 2: Command Line / Script Mode

Untuk advanced users yang ingin mengintegrasikan dalam script:

```python
# Contoh 1: Load dan process gambar dari file
from capture_module import load_image_from_file
from process_module import process_card_image
from utils import safe_write_image, create_dated_folder

# Load gambar
image = load_image_from_file("input/my_photo.jpg")

# Process dengan semua opsi
processed = process_card_image(
    image,
    add_ts=True,        # Tambah timestamp
    add_wm=True,        # Tambah watermark
    add_frame=True,     # Tambah border
    auto_enhance_flag=True,  # Auto enhancement
    brightness=10,      # Brightness +10
    contrast=1.2        # Contrast 1.2x
)

# Simpan hasil
dated_folder = create_dated_folder()
filepath = dated_folder / "kartu.jpg"
safe_write_image(str(filepath), processed, quality=95)
print(f"✓ Disimpan ke: {filepath}")
```

```python
# Contoh 2: Capture dari webcam
from capture_module import WebcamCapture
from process_module import process_card_image
from utils import safe_write_image, create_dated_folder

# Inisialisasi webcam
webcam = WebcamCapture()

# Preview webcam
webcam.preview("Preview", duration_ms=5000)

# Capture single frame
frame = webcam.capture_single_frame()

# Process
processed = process_card_image(frame)

# Save
dated_folder = create_dated_folder()
filepath = dated_folder / "kartu.jpg"
safe_write_image(str(filepath), processed)

# Release webcam
webcam.release()
```

```python
# Contoh 3: Batch processing
from capture_module import capture_multiple_from_webcam
from process_module import process_card_image
from utils import safe_write_image, create_dated_folder, generate_filename

# Capture 4 frame dari webcam
frames = capture_multiple_from_webcam(num_frames=4, delay_ms=1000)

# Process semua
dated_folder = create_dated_folder()
for i, frame in enumerate(frames):
    processed = process_card_image(frame)
    filename = generate_filename("kartu")
    filepath = dated_folder / filename
    safe_write_image(str(filepath), processed)
    print(f"✓ Kartu {i+1} disimpan")
```

---

## ⚙️ Konfigurasi

### File config.py

Semua parameter konfigurasi dapat diubah di file `config.py`:

```python
# CARD DIMENSIONS
CARD_WIDTH = 400          # Lebar kartu (pixel)
CARD_HEIGHT = 250         # Tinggi kartu (pixel)

# OUTPUT QUALITY
OUTPUT_QUALITY = 95       # Kualitas JPEG (0-100)

# BORDER
BORDER_WIDTH = 3          # Ketebalan border (pixel)
BORDER_COLOR = (200, 200, 200)  # Warna BGR

# TIMESTAMP
TIMESTAMP_FONT_SCALE = 0.5       # Ukuran font
TIMESTAMP_COLOR = (0, 0, 0)      # Warna teks
TIMESTAMP_BG_COLOR = (220, 220, 220)  # Warna background

# WATERMARK
WATERMARK_TEXT = "SmartAttend v1.0"  # Teks watermark
WATERMARK_POSITION = "bottom-right"  # Posisi

# WEBCAM
WEBCAM_FRAME_WIDTH = 640   # Resolusi kamera
WEBCAM_FRAME_HEIGHT = 480
WEBCAM_FPS = 30
```

Lihat file `config.py` untuk parameter lengkapnya.

---

## 📊 Contoh Output

### Individual Card dengan Annotation:
```
┌────────────────────────────────────┐
│                                    │
│    ┌──────────────────────────┐   │
│    │                          │   │
│    │   [Gambar Kartu]         │   │
│    │   (400 x 250 pixel)      │   │
│    │                          │   │
│    └──────────────────────────┘   │
│   ┌──────────────────────────┐    │
│   │ 2024-01-15 08:30:45      │    │
│   │ SmartAttend v1.0         │    │
│   └──────────────────────────┘    │
└────────────────────────────────────┘
```

### Collage 2x2 Summary:
```
┌──────────────────────────────────────────────────┐
│        DAILY SUMMARY: 2024-01-15                 │
├──────────────────┬──────────────────┬────────────┤
│   Kartu #1       │   Kartu #2       │ Spacing    │
│   (400x250)      │   (400x250)      │   10px     │
├──────────────────┼──────────────────┤────────────┤
│   Kartu #3       │   Kartu #4       │ Spacing    │
│   (400x250)      │   (400x250)      │   10px     │
└──────────────────┴──────────────────┴────────────┘
```

---

## 🔍 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'cv2'"
**Solusi:**
```bash
pip install opencv-python
pip install opencv-contrib-python  # Untuk fitur tambahan
```

### Error: "ModuleNotFoundError: No module named 'PIL'"
**Solusi:**
```bash
pip install Pillow
```

### Webcam tidak terbuka
**Cek:**
1. Pastikan webcam terdeteksi sistem
2. Coba ubah `WEBCAM_ID` di config.py (dari 0 ke 1, 2, dst)
3. Periksa permission aplikasi ke webcam
```python
# Cek webcam yang tersedia
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✓ Webcam {i} tersedia")
        cap.release()
```

### Gambar output blur atau kualitas buruk
**Solusi:**
1. Tingkatkan `OUTPUT_QUALITY` di config.py (hingga 100)
2. Gunakan input gambar dengan resolusi lebih tinggi
3. Aktifkan `AUTO_BRIGHTNESS_ADJUST` untuk perbaikan otomatis
4. Atur slider Contrast lebih tinggi

### Output folder sangat besar
**Solusi:**
1. Kurangi `OUTPUT_QUALITY` menjadi 85-90
2. Gunakan format PNG untuk kualitas lossless
3. Buat script yang menghapus old files secara otomatis

---

## 📈 Fitur Bonus yang Tersedia

### ✨ Advanced Features:

1. **ROI Selection Webcam**
```python
from capture_module import WebcamCaptureWithROI

webcam = WebcamCaptureWithROI()
roi = webcam.select_roi()  # User pilih area
frame = webcam.capture_with_roi(roi)
```

2. **Histogram Equalization**
```python
from process_module import equalize_histogram, auto_enhance

# Method 1: Simple equalization
enhanced = equalize_histogram(image)

# Method 2: Auto enhancement (CLAHE)
enhanced = auto_enhance(image)
```

3. **Color Space Conversion**
```python
from process_module import convert_color_space, ColorSpace

gray_img = convert_color_space(img, ColorSpace.GRAY)
rgb_img = convert_color_space(img, ColorSpace.RGB)
hsv_img = convert_color_space(img, ColorSpace.HSV)
```

4. **Batch Load dari Folder**
```python
from capture_module import load_multiple_images_from_folder

images = load_multiple_images_from_folder("input/batch")
print(f"Loaded {len(images)} images")
```

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Intel Core i3 | Intel Core i5+ |
| RAM | 4 GB | 8 GB+ |
| Storage | 500 MB | 5.0 GB |
| Python | 3.8 | 3.9+ |
| Webcam | Optional | HD (720p+) |
| OS | Windows/Linux/Mac | Windows 10+ / Ubuntu 20.04+ |

---

## 📝 Log & Debugging

### Melihat Log:
Semua aktivitas tercatat di file `logs/smartattend.log`

```bash
# Windows
type logs\smartattend.log

# Linux/Mac
cat logs/smartattend.log

# Real-time monitoring
tail -f logs/smartattend.log
```

### Enable Debug Mode:
```python
# Di config.py
DEBUG = True
VERBOSE = True
```

---

## 🎓 Learning Outcomes

Setelah mengikuti project ini, Anda akan memahami:

✅ **Image Processing Fundamentals**
- Loading, saving, dan manipulasi gambar
- Color space conversions
- Resize dengan aspect ratio preservation
- Brightness & contrast adjustments

✅ **OpenCV Basics**
- Bekerja dengan numpy arrays
- Drawing primitives (rectangle, text, etc)
- Image annotations
- Webcam capture & real-time processing

✅ **Software Architecture**
- Modular design dengan separate concerns
- Configuration management
- Error handling & logging
- GUI development dengan Tkinter

✅ **Practical Applications**
- File organization & naming conventions
- Batch processing
- Real-time preview
- User interface design

---

## 📌 Rubrik Penilaian

### Scoring Breakdown:
| Component | Bobot | Detail |
|-----------|-------|--------|
| **Fungsionalitas** | 40% | Load/Capture, Processing, Annotation, Save, Collage |
| **Code Quality** | 20% | Structure, PEP8,Comments, Docstrings |
| **Dokumentasi** | 15% | README, Code comments, Screenshots |
| **Kreativitas** | 15% | Bonus features, UI/UX, Added functionality |
| **Presentasi** | 10% | Demo quality, Explanation, Demo video |

---

## 📸 Tangkapan Layar

### GUI Main Window:
![Main Interface](screenshot_gui.png)

### Processing Result:
![Processed Card](screenshot_result.png)

### Collage Output:
![Collage 2x2](screenshot_collage.png)

*Note: Screenshot akan ditampilkan setelah demo pertama kali*

---

## 📞 Support & Questions

Untuk pertanyaan atau issue:
1. Check troubleshooting section di atas
2. Lihat log files di `logs/smartattend.log`
3. Baca dokumentasi kode di dalam masing-masing function (docstrings)
4. Hubungi tim developer

---

## 📄 License

Project ini dibuat untuk keperluan Praktikum Komputer Vision (Modul 01).
Bebas untuk dimodifikasi dan dikembangkan sesuai kebutuhan.

---

## 👨‍💻 Development Notes

### Architecture Overview:
```
┌─────────────────────────────────────────────┐
│            SMARTATTEND GUI (main.py)        │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  User Interface (Tkinter)            │  │
│  │  - File dialogs                      │  │
│  │  - Live preview windows              │  │
│  │  - Control buttons & sliders         │  │
│  └──────────────────────────────────────┘  │
│                    ↓↑                       │
│  ┌──────────────┐  ↓↑  ┌────────────────┐  │
│  │ capture_mod  │       │ process_mod    │  │
│  │ - Load file  │       │ - Resize       │  │
│  │ - Webcam     │       │ - Border       │  │
│  │ - Frames     │       │ - Annotation   │  │
│  └──────────────┘       └────────────────┘  │
│         ↓                       ↓            │
│  ┌─────────────────────────────────────┐   │
│  │         utils.py (Helper)           │   │
│  │  - File I/O     - Validation        │   │
│  │  - Logging      - Image stats       │   │
│  └─────────────────────────────────────┘   │
│         ↓↑                                  │
│  ┌─────────────────────────────────────┐   │
│  │    config.py (Configuration)        │   │
│  │  - All parameters & constants       │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Key Features Implementation:
1. **Modular Design**: Separate module untuk capture, process, utils
2. **Error Handling**: Try-except dengan meaningful error messages
3. **Logging**: Comprehensive logging untuk debugging
4. **Threading**: GUI tidak freeze saat operasi berat
5. **Configuration**: Centralized config untuk easy customization

---

## 🚀 Future Enhancements

Idea untuk pengembangan lebih lanjut:
- [ ] Face detection untuk auto-crop kartu
- [ ] OCR untuk extract text dari kartu
- [ ] Database integration untuk simpan metadata
- [ ] Email notification setelah upload
- [ ] Mobile app version
- [ ] Cloud storage integration
- [ ] Advanced analytics & reporting
- [ ] Real-time face recognition

---

## ✅ Checklist Pengerjaan

- [x] Project structure & folder organization
- [x] Config.py dengan semua parameter
- [x] Utils.py dengan helper functions
- [x] Capture module (load file & webcam)
- [x] Process module (resize, border, annotation)
- [x] Main.py GUI dengan Tkinter
- [x] Collage generator
- [x] Complete documentation (README)
- [x] Error handling & logging
- [x] Code comments & docstrings
- [x] Test dengan berbagai input
- [x] Demo video preparation

---

**Status: ✅ COMPLETE**

Terima kasih telah menggunakan SmartAttend!  
Happy coding! 🚀

---

*Last Updated: 2024-01-15*  
*Version: 1.0.0*
