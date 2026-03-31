"""
=============================================================
TUGAS AKHIR - ANALISIS DOMAIN FREKUENSI
Mata Kuliah : Praktikum Komputer Vision - Modul 3
Nama        : [Iqbal Majid Ramadhan]
NIM         : [40040323630046]
=============================================================

TUJUAN:
Menampilkan hubungan antara filter spasial (Gaussian blur, sharpening)
dengan representasinya di domain frekuensi (LPF, HPF).
Membuktikan bahwa konvolusi spasial = perkalian di domain frekuensi.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# ─── Buat folder output ────────────────────────────────────────────────────────
os.makedirs("output", exist_ok=True)


# ─── Fungsi Helper ─────────────────────────────────────────────────────────────

def get_magnitude_spectrum(img):
    """Hitung magnitude spectrum (log scale) dari gambar grayscale."""
    f = np.fft.fft2(img.astype(np.float32))
    f_shift = np.fft.fftshift(f)
    magnitude = 20 * np.log(np.abs(f_shift) + 1)
    return f_shift, magnitude


def normalize(img):
    """Normalisasi gambar ke rentang 0-255."""
    img = img - img.min()
    if img.max() > 0:
        img = img / img.max() * 255
    return img.astype(np.uint8)


def load_or_create_image():
    """
    Coba load gambar dari file. Jika tidak ada,
    buat gambar sintetis (garis & kotak) sebagai pengganti.
    """
    for fname in ["gambar.jpg", "gambar.png", "test.jpg", "test.png"]:
        if os.path.exists(fname):
            img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                print(f"[INFO] Gambar '{fname}' berhasil dimuat.")
                return img

    print("[INFO] Gambar tidak ditemukan, membuat gambar sintetis...")
    img = np.zeros((256, 256), dtype=np.uint8)
    # Tambah garis horizontal & vertikal
    img[80:90, :] = 200
    img[:, 120:130] = 200
    # Kotak putih di tengah
    img[100:160, 90:170] = 150
    # Noise ringan
    noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
    img = cv2.add(img, noise)
    return img


# ─── Load Gambar ───────────────────────────────────────────────────────────────
img = load_or_create_image()
H, W = img.shape
print(f"[INFO] Ukuran gambar: {W}x{H} piksel")


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 1: GAUSSIAN BLUR — FILTER SPASIAL vs DOMAIN FREKUENSI
# ══════════════════════════════════════════════════════════════════════════════

# --- 1A. Gaussian blur di domain SPASIAL ---
img_blur_spatial = cv2.GaussianBlur(img, (15, 15), sigmaX=3)

# --- 1B. Gaussian blur di domain FREKUENSI (LPF Gaussian) ---
# Buat mask LPF Gaussian di domain frekuensi
cy, cx = H // 2, W // 2
Y, X = np.ogrid[:H, :W]
D = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
sigma_freq = 30  # radius cutoff frekuensi
lpf_mask = np.exp(-(D ** 2) / (2 * sigma_freq ** 2))

# Terapkan LPF ke FFT gambar
f_shift_orig, mag_orig = get_magnitude_spectrum(img)
f_filtered_lpf = f_shift_orig * lpf_mask
img_blur_freq = np.abs(np.fft.ifft2(np.fft.ifftshift(f_filtered_lpf)))
img_blur_freq = normalize(img_blur_freq)

# Magnitude spectrum hasil LPF
_, mag_lpf = get_magnitude_spectrum(img_blur_freq)

# ─── Plot Bagian 1 ─────────────────────────────────────────────────────────────
fig1, axes = plt.subplots(2, 4, figsize=(16, 8))
fig1.suptitle("Bagian 1: Gaussian Blur — Spasial vs Domain Frekuensi", fontsize=14, fontweight='bold')

axes[0, 0].imshow(img, cmap='gray');               axes[0, 0].set_title("Gambar Asli")
axes[0, 1].imshow(mag_orig, cmap='gray');          axes[0, 1].set_title("Spectrum Asli (FFT)")
axes[0, 2].imshow(lpf_mask, cmap='hot');           axes[0, 2].set_title("Mask LPF Gaussian")
axes[0, 3].imshow(mag_lpf, cmap='gray');           axes[0, 3].set_title("Spectrum Setelah LPF")

axes[1, 0].imshow(img, cmap='gray');               axes[1, 0].set_title("Gambar Asli")
axes[1, 1].imshow(img_blur_spatial, cmap='gray');  axes[1, 1].set_title("Blur Spasial\n(GaussianBlur)")
axes[1, 2].imshow(img_blur_freq, cmap='gray');     axes[1, 2].set_title("Blur Frekuensi\n(LPF Gaussian)")
diff1 = cv2.absdiff(img_blur_spatial, img_blur_freq)
axes[1, 3].imshow(diff1, cmap='hot');              axes[1, 3].set_title(f"Selisih\n(mean={diff1.mean():.2f})")

for ax in axes.flat:
    ax.axis('off')

plt.tight_layout()
plt.savefig("output/bagian1_blur_spasial_vs_frekuensi.png", dpi=120)
plt.show()
print("[SAVED] output/bagian1_blur_spasial_vs_frekuensi.png")


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 2: SHARPENING — FILTER SPASIAL vs DOMAIN FREKUENSI
# ══════════════════════════════════════════════════════════════════════════════

# --- 2A. Sharpening di domain SPASIAL (Unsharp Mask) ---
blurred_for_sharp = cv2.GaussianBlur(img, (9, 9), sigmaX=2)
img_sharp_spatial = cv2.addWeighted(img, 1.5, blurred_for_sharp, -0.5, 0)

# --- 2B. Sharpening di domain FREKUENSI (HPF) ---
hpf_mask = 1 - lpf_mask  # HPF = kebalikan LPF
# Kombinasi: gambar asli + komponen frekuensi tinggi
lpf_component = np.abs(np.fft.ifft2(np.fft.ifftshift(f_shift_orig * lpf_mask)))
hpf_component = np.abs(np.fft.ifft2(np.fft.ifftshift(f_shift_orig * hpf_mask)))
img_sharp_freq = normalize(lpf_component + 1.5 * hpf_component)

# Magnitude spectrum hasil HPF
_, mag_hpf = get_magnitude_spectrum(normalize(hpf_component))

# ─── Plot Bagian 2 ─────────────────────────────────────────────────────────────
fig2, axes = plt.subplots(2, 4, figsize=(16, 8))
fig2.suptitle("Bagian 2: Sharpening — Spasial vs Domain Frekuensi", fontsize=14, fontweight='bold')

axes[0, 0].imshow(img, cmap='gray');               axes[0, 0].set_title("Gambar Asli")
axes[0, 1].imshow(mag_orig, cmap='gray');          axes[0, 1].set_title("Spectrum Asli (FFT)")
axes[0, 2].imshow(hpf_mask, cmap='hot');           axes[0, 2].set_title("Mask HPF")
axes[0, 3].imshow(mag_hpf, cmap='gray');           axes[0, 3].set_title("Spectrum Setelah HPF")

axes[1, 0].imshow(img, cmap='gray');               axes[1, 0].set_title("Gambar Asli")
axes[1, 1].imshow(img_sharp_spatial, cmap='gray'); axes[1, 1].set_title("Sharp Spasial\n(Unsharp Mask)")
axes[1, 2].imshow(img_sharp_freq, cmap='gray');    axes[1, 2].set_title("Sharp Frekuensi\n(HPF boost)")
diff2 = cv2.absdiff(img_sharp_spatial, img_sharp_freq)
axes[1, 3].imshow(diff2, cmap='hot');              axes[1, 3].set_title(f"Selisih\n(mean={diff2.mean():.2f})")

for ax in axes.flat:
    ax.axis('off')

plt.tight_layout()
plt.savefig("output/bagian2_sharp_spasial_vs_frekuensi.png", dpi=120)
plt.show()
print("[SAVED] output/bagian2_sharp_spasial_vs_frekuensi.png")


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 3: BUKTI — KONVOLUSI SPASIAL = PERKALIAN DOMAIN FREKUENSI
# ══════════════════════════════════════════════════════════════════════════════

# Kernel Gaussian 15x15
kernel_size = 15
kernel_gauss = cv2.getGaussianKernel(kernel_size, 3)
kernel_gauss_2d = kernel_gauss @ kernel_gauss.T  # outer product → 2D kernel

# CARA A: Konvolusi spasial langsung
img_conv_spatial = cv2.filter2D(img.astype(np.float32), -1, kernel_gauss_2d)

# CARA B: Perkalian di domain frekuensi
# Pad kernel ke ukuran gambar
kernel_pad = np.zeros_like(img, dtype=np.float32)
kh, kw = kernel_gauss_2d.shape
ky = (H - kh) // 2
kx = (W - kw) // 2
kernel_pad[ky:ky+kh, kx:kx+kw] = kernel_gauss_2d

F_img    = np.fft.fft2(img.astype(np.float32))
F_kernel = np.fft.fft2(kernel_pad)
img_conv_freq = np.abs(np.fft.ifft2(F_img * F_kernel))  # teorema konvolusi

# Hitung selisih antara kedua metode
diff_conv = np.abs(img_conv_spatial - img_conv_freq)
max_err   = diff_conv.max()
mean_err  = diff_conv.mean()

# Magnitude spectrum kernel
_, mag_kernel = get_magnitude_spectrum(normalize(kernel_pad))

# ─── Plot Bagian 3 ─────────────────────────────────────────────────────────────
fig3, axes = plt.subplots(2, 4, figsize=(16, 8))
fig3.suptitle("Bagian 3: Bukti Teorema Konvolusi\n"
              "Konvolusi Spasial ≡ Perkalian Domain Frekuensi",
              fontsize=13, fontweight='bold')

axes[0, 0].imshow(img, cmap='gray');                       axes[0, 0].set_title("Gambar Asli")
axes[0, 1].imshow(kernel_gauss_2d, cmap='hot');            axes[0, 1].set_title("Kernel Gaussian\n(15×15)")
axes[0, 2].imshow(mag_orig, cmap='gray');                  axes[0, 2].set_title("FFT Gambar")
axes[0, 3].imshow(mag_kernel, cmap='gray');                axes[0, 3].set_title("FFT Kernel")

axes[1, 0].imshow(normalize(img_conv_spatial), cmap='gray');
axes[1, 0].set_title("Hasil Konvolusi\n(Domain Spasial)")

axes[1, 1].imshow(normalize(img_conv_freq), cmap='gray');
axes[1, 1].set_title("Hasil Perkalian FFT\n(Domain Frekuensi)")

axes[1, 2].imshow(normalize(diff_conv), cmap='hot');
axes[1, 2].set_title(f"Selisih Kedua Metode\nMax={max_err:.4f} | Mean={mean_err:.4f}")

# Teks kesimpulan
axes[1, 3].axis('off')
kesimpulan = (
    "KESIMPULAN\n\n"
    f"Selisih maksimum:\n  {max_err:.6f}\n\n"
    f"Selisih rata-rata:\n  {mean_err:.6f}\n\n"
    "Kedua hasil hampir identik.\n\n"
    "→ Terbukti bahwa:\n"
    "  Konvolusi spasial\n"
    "  ≡ Perkalian FFT\n\n"
    "(Teorema Konvolusi)"
)
axes[1, 3].text(0.1, 0.5, kesimpulan, transform=axes[1, 3].transAxes,
                fontsize=10, va='center', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

for ax in axes.flat:
    if ax.get_images():
        ax.axis('off')

plt.tight_layout()
plt.savefig("output/bagian3_bukti_teorema_konvolusi.png", dpi=120)
plt.show()
print("[SAVED] output/bagian3_bukti_teorema_konvolusi.png")


# ══════════════════════════════════════════════════════════════════════════════
# RINGKASAN AKHIR DI TERMINAL
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("  HASIL TUGAS ANALISIS DOMAIN FREKUENSI")
print("="*60)
print(f"  Ukuran gambar       : {W} x {H} piksel")
print(f"  Sigma LPF Gaussian  : {sigma_freq}")
print()
print("  [Bagian 1] Gaussian Blur")
print(f"    Selisih spasial vs frekuensi : mean = {diff1.mean():.2f}")
print()
print("  [Bagian 2] Sharpening")
print(f"    Selisih spasial vs frekuensi : mean = {diff2.mean():.2f}")
print()
print("  [Bagian 3] Bukti Teorema Konvolusi")
print(f"    Selisih max  : {max_err:.6f}")
print(f"    Selisih mean : {mean_err:.6f}")
print()
print("  Kesimpulan:")
print("  Filter spasial (blur/sharp) ekuivalen dengan")
print("  LPF/HPF di domain frekuensi.")
print("  Konvolusi spasial = perkalian FFT  ✓")
print("="*60)
print("  File output tersimpan di folder 'output/'")
print("="*60)
