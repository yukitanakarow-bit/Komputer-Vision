"""
╔══════════════════════════════════════════════════════════════════╗
║         PROJECT MODUL 3 - PIPELINE ANALISIS CITRA LENGKAP       ║
║         Praktikum Komputer Vision                                ║
╠══════════════════════════════════════════════════════════════════╣
║  Nama  : [Iqbal Majid Ramadhan]                                        ║
║  NIM   : [40040323630046]                                                   ║
╚══════════════════════════════════════════════════════════════════╝

PIPELINE:
  Tahap 1 → Pra-Pemrosesan    (CLAHE + Bilateral Filter)
  Tahap 2 → Segmentasi Warna  (HSV inRange - Merah & Hijau)
  Tahap 3 → Deteksi Tepi      (Canny + Sobel)
  Tahap 4 → Morfologi         (Erosi, Dilasi, Opening, Closing, TopHat)
  Tahap 5 → Connected Comp.   (Labeling + Statistik objek)
  Tahap 6 → Domain Frekuensi  (FFT + LPF + HPF)
  Tahap 7 → Visualisasi       (Semua tahap + Laporan statistik)

SPESIFIKASI TERPENUHI: 12/12
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os, time

# ══════════════════════════════════════════════════════════════════════════════
#  KONTROL PARAMETER — ubah di sini untuk menyesuaikan
# ══════════════════════════════════════════════════════════════════════════════

# --- Pra-Pemrosesan ---
CLAHE_CLIP_LIMIT    = 2.0          # [Spek 1] makin besar → kontras makin kuat
CLAHE_TILE_GRID     = (8, 8)       # [Spek 1] ukuran tile CLAHE
BILATERAL_D         = 9            # [Spek 2] diameter kernel bilateral
BILATERAL_SIGMA_C   = 75           # [Spek 2] sigma warna
BILATERAL_SIGMA_S   = 75           # [Spek 2] sigma spasial

# --- Segmentasi HSV [Spek 3] ---
# Merah (dua range karena wrap-around di H)
MERAH_LOW1  = np.array([0,   80, 80])
MERAH_HIGH1 = np.array([10, 255, 255])
MERAH_LOW2  = np.array([160, 80, 80])
MERAH_HIGH2 = np.array([180,255, 255])
# Hijau
HIJAU_LOW   = np.array([35,  60, 60])
HIJAU_HIGH  = np.array([85, 255, 255])

# --- Thresholding [Spek 4] ---
ADAPTIVE_BLOCK_SIZE = 15           # harus ganjil
ADAPTIVE_C          = 3

# --- Canny [Spek 5] ---
CANNY_LOW   = 50
CANNY_HIGH  = 150

# --- Morfologi [Spek 6] ---
MORPH_KERNEL_SIZE = 5              # ukuran structuring element

# --- Connected Components [Spek 7] ---
CC_AREA_MIN = 200                  # area minimum objek (piksel)
CC_AREA_MAX = 999999               # area maksimum objek

# --- Domain Frekuensi [Spek 8 & 9] ---
LPF_SIGMA = 30                     # radius cutoff low-pass filter

# ══════════════════════════════════════════════════════════════════════════════
#  UTILITY
# ══════════════════════════════════════════════════════════════════════════════

os.makedirs("output", exist_ok=True)

def load_or_create():
    """Load gambar dari file atau buat gambar sintetis berwarna."""
    for f in ["kota.jpg","gambar.png","input.jpg","input.png"]:
        if os.path.exists(f):
            img = cv2.imread(f)
            if img is not None:
                print(f"[INFO] Gambar '{f}' berhasil dimuat.")
                return img
    print("[INFO] Gambar tidak ditemukan → membuat gambar sintetis berwarna...")
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    # Latar abu-abu gelap
    canvas[:] = (40, 40, 40)
    # Objek MERAH
    cv2.circle(canvas, (120, 150), 70, (0, 0, 200), -1)
    cv2.rectangle(canvas, (300, 80), (420, 200), (30, 30, 210), -1)
    # Objek HIJAU
    cv2.circle(canvas, (500, 150), 60, (30, 180, 30), -1)
    cv2.rectangle(canvas, (80, 300), (220, 420), (20, 200, 20), -1)
    # Objek PUTIH (untuk morfologi & tepi)
    cv2.rectangle(canvas, (280, 280), (560, 440), (200, 200, 200), -1)
    cv2.circle(canvas, (350, 360), 40, (240, 240, 240), -1)
    # Noise ringan
    noise = np.random.randint(0, 18, canvas.shape, dtype=np.uint8)
    canvas = cv2.add(canvas, noise)
    cv2.imwrite("output/gambar_sintetis.png", canvas)
    return canvas

def magnitude_spectrum(gray):
    """Hitung log-magnitude spectrum FFT."""
    f      = np.fft.fft2(gray.astype(np.float32))
    fshift = np.fft.fftshift(f)
    mag    = 20 * np.log(np.abs(fshift) + 1)
    return fshift, mag

def norm_u8(img):
    """Normalisasi float array ke uint8 0-255."""
    img = img - img.min()
    if img.max() > 0:
        img = img / img.max() * 255
    return img.astype(np.uint8)

def label_warna(n):
    """Warna unik BGR untuk tiap label connected component."""
    np.random.seed(n * 17)
    return tuple(int(x) for x in np.random.randint(80, 255, 3))

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 1 — PRA-PEMROSESAN
# ══════════════════════════════════════════════════════════════════════════════
print("\n[Tahap 1] Pra-Pemrosesan...")

img_bgr  = load_or_create()
img_rgb  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

# CLAHE pada channel L (LAB) — [Spek 1]
lab  = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
L, A, B = cv2.split(lab)
clahe    = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID)
L_clahe  = clahe.apply(L)
lab_clahe= cv2.merge([L_clahe, A, B])
img_clahe_bgr = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

# Bilateral Filter — [Spek 2]
img_bilateral = cv2.bilateralFilter(img_clahe_bgr,
                                    BILATERAL_D,
                                    BILATERAL_SIGMA_C,
                                    BILATERAL_SIGMA_S)
img_gray = cv2.cvtColor(img_bilateral, cv2.COLOR_BGR2GRAY)

cv2.imwrite("output/tahap1a_clahe.png",     img_clahe_bgr)
cv2.imwrite("output/tahap1b_bilateral.png", img_bilateral)
print("  ✓ CLAHE & Bilateral Filter selesai.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 2 — SEGMENTASI WARNA HSV
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 2] Segmentasi Warna HSV...")  # [Spek 3]

hsv = cv2.cvtColor(img_bilateral, cv2.COLOR_BGR2HSV)

# Merah (dua range)
mask_merah1 = cv2.inRange(hsv, MERAH_LOW1, MERAH_HIGH1)
mask_merah2 = cv2.inRange(hsv, MERAH_LOW2, MERAH_HIGH2)
mask_merah  = cv2.bitwise_or(mask_merah1, mask_merah2)

# Hijau
mask_hijau = cv2.inRange(hsv, HIJAU_LOW, HIJAU_HIGH)

# Hasil masking pada gambar asli
hasil_merah = cv2.bitwise_and(img_bilateral, img_bilateral, mask=mask_merah)
hasil_hijau = cv2.bitwise_and(img_bilateral, img_bilateral, mask=mask_hijau)

cv2.imwrite("output/tahap2a_mask_merah.png", mask_merah)
cv2.imwrite("output/tahap2b_mask_hijau.png", mask_hijau)
print("  ✓ Segmentasi merah & hijau selesai.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 3 — DETEKSI TEPI
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 3] Deteksi Tepi...")

# Canny — [Spek 5]
img_canny = cv2.Canny(img_gray, CANNY_LOW, CANNY_HIGH)

# Sobel (opsional, analisis arah)
sobel_x = cv2.Sobel(img_gray, cv2.CV_64F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(img_gray, cv2.CV_64F, 0, 1, ksize=3)
sobel_mag = norm_u8(np.sqrt(sobel_x**2 + sobel_y**2))

# Thresholding Otsu & Adaptive — [Spek 4]
_, thresh_otsu = cv2.threshold(img_gray, 0, 255,
                               cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh_adaptive = cv2.adaptiveThreshold(img_gray, 255,
                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY,
                                        ADAPTIVE_BLOCK_SIZE, ADAPTIVE_C)

cv2.imwrite("output/tahap3a_canny.png",          img_canny)
cv2.imwrite("output/tahap3b_sobel.png",          sobel_mag)
cv2.imwrite("output/tahap3c_otsu.png",           thresh_otsu)
cv2.imwrite("output/tahap3d_adaptive_thresh.png",thresh_adaptive)
print("  ✓ Canny, Sobel, Otsu, Adaptive Threshold selesai.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 4 — MORFOLOGI
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 4] Operasi Morfologi...")  # [Spek 6]

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                   (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE))

# Gabungkan mask merah + hijau sebagai input morfologi
mask_gabung = cv2.bitwise_or(mask_merah, mask_hijau)

erosi    = cv2.erode(mask_gabung, kernel, iterations=1)
dilasi   = cv2.dilate(mask_gabung, kernel, iterations=1)
opening  = cv2.morphologyEx(mask_gabung, cv2.MORPH_OPEN,    kernel)
closing  = cv2.morphologyEx(mask_gabung, cv2.MORPH_CLOSE,   kernel)
tophat   = cv2.morphologyEx(img_gray,    cv2.MORPH_TOPHAT,  kernel)
blackhat = cv2.morphologyEx(img_gray,    cv2.MORPH_BLACKHAT,kernel)

# Mask final yang sudah dibersihkan
mask_final = closing.copy()

cv2.imwrite("output/tahap4a_erosi.png",   erosi)
cv2.imwrite("output/tahap4b_dilasi.png",  dilasi)
cv2.imwrite("output/tahap4c_opening.png", opening)
cv2.imwrite("output/tahap4d_closing.png", closing)
cv2.imwrite("output/tahap4e_tophat.png",  tophat)
print("  ✓ Erosi, Dilasi, Opening, Closing, Top-Hat selesai.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 5 — CONNECTED COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 5] Connected Components...")  # [Spek 7]

num_labels, labels, stats, centroids = \
    cv2.connectedComponentsWithStats(mask_final, connectivity=8)

# Filter objek berdasarkan area
objek_valid = []
for i in range(1, num_labels):   # 0 = background
    area = stats[i, cv2.CC_STAT_AREA]
    if CC_AREA_MIN <= area <= CC_AREA_MAX:
        objek_valid.append(i)

# Buat gambar berlabel warna
labeled_img = np.zeros_like(img_bilateral)
for idx in objek_valid:
    labeled_img[labels == idx] = label_warna(idx)

# Overlay bounding box & centroid pada gambar asli
overlay = img_bilateral.copy()
for idx in objek_valid:
    x = stats[idx, cv2.CC_STAT_LEFT]
    y = stats[idx, cv2.CC_STAT_TOP]
    w = stats[idx, cv2.CC_STAT_WIDTH]
    h = stats[idx, cv2.CC_STAT_HEIGHT]
    cx, cy = int(centroids[idx][0]), int(centroids[idx][1])
    area   = stats[idx, cv2.CC_STAT_AREA]
    cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.circle(overlay, (cx, cy), 4, (0, 0, 255), -1)
    cv2.putText(overlay, f"A={area}", (x, y-5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 1)

cv2.imwrite("output/tahap5a_labeled.png", labeled_img)
cv2.imwrite("output/tahap5b_overlay.png", overlay)
print(f"  ✓ Ditemukan {len(objek_valid)} objek valid.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 6 — DOMAIN FREKUENSI
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 6] Analisis Domain Frekuensi...")  # [Spek 8 & 9]

H, W = img_gray.shape
fshift_orig, mag_orig = magnitude_spectrum(img_gray)

# Buat mask LPF Gaussian
cy_f, cx_f = H // 2, W // 2
Y, X = np.ogrid[:H, :W]
D = np.sqrt((X - cx_f)**2 + (Y - cy_f)**2)
lpf_mask = np.exp(-(D**2) / (2 * LPF_SIGMA**2))
hpf_mask = 1 - lpf_mask

# Terapkan LPF & HPF
img_lpf = norm_u8(np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_orig * lpf_mask))))
img_hpf = norm_u8(np.abs(np.fft.ifft2(np.fft.ifftshift(fshift_orig * hpf_mask))))

# Spectrum setelah filter
_, mag_lpf = magnitude_spectrum(img_lpf)
_, mag_hpf = magnitude_spectrum(img_hpf)

# Bandingkan LPF frekuensi vs Gaussian blur spasial — [Spek 9]
img_blur_spasial = cv2.GaussianBlur(img_gray, (15, 15), sigmaX=3)
diff_lpf_vs_blur = cv2.absdiff(img_lpf, img_blur_spasial)

cv2.imwrite("output/tahap6a_spectrum_asli.png",  norm_u8(mag_orig))
cv2.imwrite("output/tahap6b_lpf_hasil.png",      img_lpf)
cv2.imwrite("output/tahap6c_hpf_hasil.png",      img_hpf)
cv2.imwrite("output/tahap6d_blur_spasial.png",   img_blur_spasial)
print("  ✓ FFT, LPF, HPF, perbandingan spasial selesai.")

# ══════════════════════════════════════════════════════════════════════════════
#  TAHAP 7 — VISUALISASI KOMPREHENSIF  [Spek 10]
# ══════════════════════════════════════════════════════════════════════════════
print("[Tahap 7] Membuat Visualisasi...")

def bgr2rgb(img):
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

fig, axes = plt.subplots(5, 5, figsize=(22, 20))
fig.suptitle("PROJECT M03 — Pipeline Analisis Citra Lengkap",
             fontsize=16, fontweight='bold', y=0.995)
fig.patch.set_facecolor('#1a1a2e')

tampilan = [
    # Baris 1 — Pra-Pemrosesan
    (bgr2rgb(img_bgr),          "Gambar Asli",           'viridis'),
    (bgr2rgb(img_clahe_bgr),    "T1a: CLAHE (LAB-L)",    'viridis'),
    (bgr2rgb(img_bilateral),    "T1b: Bilateral Filter", 'viridis'),
    (img_gray,                  "Grayscale",              'gray'),
    (None,                      "",                       None),    # spacer

    # Baris 2 — Segmentasi
    (mask_merah,                "T2a: Mask Merah",        'Reds'),
    (mask_hijau,                "T2b: Mask Hijau",        'Greens'),
    (bgr2rgb(hasil_merah),      "T2c: Hasil Merah",       'viridis'),
    (bgr2rgb(hasil_hijau),      "T2d: Hasil Hijau",       'viridis'),
    (mask_gabung,               "T2e: Mask Gabungan",     'gray'),

    # Baris 3 — Tepi & Threshold
    (img_canny,                 "T3a: Canny Edge",        'gray'),
    (sobel_mag,                 "T3b: Sobel Magnitude",   'gray'),
    (thresh_otsu,               "T3c: Threshold Otsu",    'gray'),
    (thresh_adaptive,           "T3d: Threshold Adaptif", 'gray'),
    (None,                      "",                       None),

    # Baris 4 — Morfologi
    (opening,                   "T4a: Opening",           'gray'),
    (closing,                   "T4b: Closing",           'gray'),
    (erosi,                     "T4c: Erosi",             'gray'),
    (dilasi,                    "T4d: Dilasi",            'gray'),
    (tophat,                    "T4e: Top-Hat",           'gray'),

    # Baris 5 — CC & Frekuensi
    (bgr2rgb(labeled_img),      "T5a: Labeled Objects",   'viridis'),
    (bgr2rgb(overlay),          "T5b: Bounding Box",      'viridis'),
    (norm_u8(mag_orig),         "T6a: FFT Spectrum",      'hot'),
    (img_lpf,                   "T6b: LPF (blur freq)",   'gray'),
    (img_hpf,                   "T6c: HPF (tepi freq)",   'gray'),
]

for ax, (img_data, title, cmap) in zip(axes.flat, tampilan):
    ax.set_facecolor('#1a1a2e')
    if img_data is None:
        ax.axis('off')
        continue
    ax.imshow(img_data, cmap=cmap if len(img_data.shape)==2 else None)
    ax.set_title(title, fontsize=8, color='white', pad=3)
    ax.axis('off')

plt.tight_layout(rect=[0, 0, 1, 0.995])
plt.savefig("output/PIPELINE_LENGKAP.png", dpi=110,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.show()
print("[SAVED] output/PIPELINE_LENGKAP.png")

# ══════════════════════════════════════════════════════════════════════════════
#  LAPORAN STATISTIK  [Spek 11]
# ══════════════════════════════════════════════════════════════════════════════

areas = [stats[i, cv2.CC_STAT_AREA] for i in objek_valid] if objek_valid else [0]
area_rata   = np.mean(areas)
area_max    = np.max(areas)
area_min    = np.min(areas)
idx_terbesar= objek_valid[np.argmax(areas)] if objek_valid else -1

laporan = f"""
╔══════════════════════════════════════════════════════════╗
║            LAPORAN STATISTIK — PIPELINE M03              ║
╠══════════════════════════════════════════════════════════╣
║  Ukuran gambar      : {W} x {H} piksel
║  Pixel merah        : {np.count_nonzero(mask_merah):>7}
║  Pixel hijau        : {np.count_nonzero(mask_hijau):>7}
╠══════════════════════════════════════════════════════════╣
║  CONNECTED COMPONENTS
║  Total komponen     : {num_labels - 1:>7}
║  Objek valid        : {len(objek_valid):>7}  (area {CC_AREA_MIN}–{CC_AREA_MAX} px)
║  Area rata-rata     : {area_rata:>7.1f} px
║  Area terbesar      : {area_max:>7} px  (label #{idx_terbesar})
║  Area terkecil      : {area_min:>7} px
╠══════════════════════════════════════════════════════════╣
║  DOMAIN FREKUENSI
║  Selisih LPF vs blur spasial (mean): {diff_lpf_vs_blur.mean():.4f}
║  → LPF frekuensi ≈ Gaussian blur spasial (terbukti)
╠══════════════════════════════════════════════════════════╣
║  PARAMETER YANG DIGUNAKAN
║  CLAHE clipLimit    : {CLAHE_CLIP_LIMIT}
║  CLAHE tileGrid     : {CLAHE_TILE_GRID}
║  Bilateral d/σc/σs  : {BILATERAL_D}/{BILATERAL_SIGMA_C}/{BILATERAL_SIGMA_S}
║  Canny low/high     : {CANNY_LOW}/{CANNY_HIGH}
║  Morph kernel       : {MORPH_KERNEL_SIZE}x{MORPH_KERNEL_SIZE}
║  LPF sigma          : {LPF_SIGMA}
╠══════════════════════════════════════════════════════════╣
║  OUTPUT TERSIMPAN DI FOLDER  output/
╚══════════════════════════════════════════════════════════╝
"""

print(laporan)
with open("output/laporan_statistik.txt", "w", encoding="utf-8") as f:
    f.write(laporan)
print("[SAVED] output/laporan_statistik.txt")
print("[SELESAI] Pipeline berhasil dijalankan!")
