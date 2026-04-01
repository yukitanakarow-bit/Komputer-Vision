# FeatureMatch Vision App
**Proyek Modul 4: Deteksi Fitur dan Pencocokan**

---

## Struktur Folder

```
feature_match_app/
  main.py                 ← Entry point utama
  detector_benchmark.py   ← Fase 1: Benchmark detektor
  robust_matcher.py       ← Fase 2: Robust matching
  object_recognizer.py    ← Fase 3: Object recognition
  image_retriever.py      ← Fase 4: Image retrieval
  utils/
    visualization.py
    io_utils.py
  data/
    templates/            ← Gambar template (JPG/PNG)
    database/             ← Gambar database retrieval
    query/                ← Gambar query
  results/                ← Output otomatis tersimpan di sini
  requirements.txt
  README.md
```

---

## Instalasi

```bash
pip install -r requirements.txt
```

> Pastikan menggunakan `opencv-contrib-python` agar SIFT, AKAZE, dsb tersedia.

---

## Cara Menjalankan

### Jalankan semua fase sekaligus (demo otomatis dengan gambar sintetis)
```bash
python main.py
```

### Jalankan fase tertentu
```bash
python main.py --fase 1                        # Benchmark detektor
python main.py --fase 2                        # Robust Matcher
python main.py --fase 3                        # Object Recognition
python main.py --fase 4                        # Image Retrieval
```

### Dengan gambar sendiri
```bash
# Fase 1 — benchmark pada gambar kamu
python main.py --fase 1 --img foto.jpg

# Fase 2 — matching dua gambar
python main.py --fase 2 --img gambar1.jpg --img2 gambar2.jpg

# Fase 3 — scene + templates di folder data/templates/
python main.py --fase 3 --img scene.jpg

# Fase 4 — query gambar terhadap database di data/database/
python main.py --fase 4 --img query.jpg --db data/database
```

### Jalankan modul secara individual
```bash
python detector_benchmark.py foto.jpg
python robust_matcher.py gambar1.jpg gambar2.jpg
python object_recognizer.py scene.jpg template1.jpg template2.jpg
python image_retriever.py data/database query.jpg
```

---

## Konfigurasi

Semua parameter dapat diubah melalui dictionary `CONFIG` di `main.py`:

```python
CONFIG = {
    'benchmark': {
        'detectors': ['Harris', 'Shi-Tomasi', 'SIFT', 'ORB', 'AKAZE', 'FAST', 'BRISK'],
    },
    'matcher': {
        'combinations': [('SIFT', 'FLANN'), ('ORB', 'BF'), ('AKAZE', 'FLANN')],
        'ratio': 0.75,
        'ransac_thresh': 5.0,
    },
    'recognizer': {
        'min_inliers': 10,
        'confidence_threshold': 0.25,
    },
    'retrieval': {
        'top_k': 5,
    },
}
```

---

## Tips Penggunaan

- **Gambar template/database** harus berformat JPG atau PNG dan ditempatkan di folder `data/templates/` dan `data/database/`.
- Jika folder kosong, semua fase akan otomatis menggunakan **gambar sintetis** untuk demo.
- Semua hasil visualisasi tersimpan otomatis di folder `results/`.
- Untuk menyesuaikan threshold deteksi, ubah `min_inliers` dan `confidence_threshold` di `CONFIG`.

---

## Hasil Output

| File | Keterangan |
|------|------------|
| `results/benchmark_keypoints.png` | Visualisasi keypoint semua detektor |
| `results/benchmark_chart.png` | Bar chart perbandingan detektor |
| `results/match_SIFT_FLANN.png` | Hasil matching SIFT+FLANN |
| `results/match_ORB_BF.png` | Hasil matching ORB+BF |
| `results/match_AKAZE_FLANN.png` | Hasil matching AKAZE+FLANN |
| `results/recognition_result.png` | Bounding box objek terdeteksi |
| `results/retrieval_result.png` | Top-K hasil image retrieval |
| `results/retrieval_index.pkl` | Index fitur database (tersimpan) |
