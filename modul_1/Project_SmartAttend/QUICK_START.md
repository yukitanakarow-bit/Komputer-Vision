# 🚀 QUICK START - SmartAttend

Panduan cepat untuk memulai menggunakan SmartAttend dalam 5 menit!

## 1️⃣ Install Dependencies

```bash
# Copy-paste command ini di terminal/command prompt

# Windows
cd "path/ke/Project_SmartAttend"
pip install -r requirements.txt

# Linux/Mac
cd path/ke/Project_SmartAttend
pip install -r requirements.txt
```

## 2️⃣ Siapkan Gambar Input

Letakkan gambar kartu Anda di folder `input/`

```
Project_SmartAttend/
├── input/
│   ├── kartu1.jpg      ← Gambar Anda di sini
│   ├── kartu2.png
│   └── ...
```

## 3️⃣ Jalankan Program

### 💻 Opsi A: GUI (User-Friendly)

```bash
python main.py
```

Kemudian:
1. Klik **"📂 Buka Gambar dari File"** untuk load gambar
2. Klik **"🔄 Process Gambar"** untuk proseskan
3. Klik **"💾 Simpan Gambar"** untuk simpan hasil
4. Hasil akan tersimpan di folder `output/YYYY-MM-DD/`

### 🎓 Opsi B: Simple Examples (Learning)

```bash
python simple_examples.py
```

Pilih example nomor untuk belajar step-by-step.

## 4️⃣ Lihat Hasil

Hasil pemrosesan tersimpan di:

```
Project_SmartAttend/
└── output/
    ├── 2024-01-15/
    │   ├── 20240115_083045_kartu.jpg    ← Output gambar
    │   └── ...
    └── collages/
        └── summary_20240115_083045.jpg  ← Collage
```

## ⚡ Quick Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Jalankan GUI
python main.py

# Jalankan examples interaktif
python simple_examples.py

# Verifikasi instalasi
python -c "import cv2, numpy; print('✓ OK')"
```

## 🎯 Fitur-Fitur Utama

| Fitur | Shortcut |
|-------|----------|
| Load gambar | Button "📂 Buka Gambar" |
| Capture webcam | Button "📷 Capture" |
| Process | Button "🔄 Process" |
| Save | Button "💾 Simpan" |
| Collage | Button "🎨 Collage" |

## 🎮 Tips & Tricks

### 💡 Untuk Hasil Terbaik:

1. **Pencahayaan**: Foto di tempat yang terang
2. **Posisi**: Kartu lurus dan fokus
3. **Contrast**: Tingkatkan slider Contrast jika gambar gelap
4. **Watermark**: Check box untuk menambahkan/menghilangkan
5. **Quality**: Default 95 sudah bagus, bisa naik jika perlu

### 🚀 Batch Processing:

```bash
# Capture 4 frame sekaligus dari webcam
1. Klik "📷 Capture Batch (4 frames)"
2. Klik "🔄 Process Gambar" (ubah settings jika perlu)
3. Klik "🎨 Buat Collage 2x2"
4. Done! ✓
```

## ❌ Troubleshooting Cepat

| Problem | Solusi |
|---------|--------|
| "No module opencv" | `pip install opencv-python` |
| Webcam error | Cek permission, coba USB cam lain |
| File not found | Pastikan gambar di folder `input/` |
| Gambar blur | Naik `OUTPUT_QUALITY` di config.py |
| GUI error | Update Python ke 3.8+ |

## 📚 Dokumentasi Lengkap

Lihat file `README.md` untuk dokumentasi mendetail.

## ✅ Checklist First Run

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Copy gambar ke folder `input/`
- [ ] Run `python main.py`
- [ ] Load gambar → Process → Save
- [ ] Buka folder `output/` untuk melihat hasil
- [ ] Celebrate! 🎉

---

**Selesai!** Sekarang Anda siap menggunakan SmartAttend.

Untuk bantuan lebih lanjut, baca README.md atau jalankan simple_examples.py

Happy coding! 🚀

---

*Created with ❤️ by SmartAttend Team*
