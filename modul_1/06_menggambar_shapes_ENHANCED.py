# ============================================================================
# PROGRAM: 06_menggambar_shapes_ENHANCED.py
# PRAKTIKUM COMPUTER VISION - BAB 1: PENDAHULUAN
# ============================================================================
# Deskripsi: Program ini mendemonstrasikan cara menggambar berbagai bentuk
#            geometri dan teks pada gambar dengan dokumentasi LENGKAP untuk
#            setiap parameter fungsi cv2.
#
# FITUR KHUSUS:
# - Setiap cv2 function call dilengkapi komentar penjelasan parameter
# - Fokus pada cv2.putText(), cv2.line(), cv2.rectangle(), cv2.circle()
# - Contoh penggunaan dengan berbagai kombinasi parameter
#
# TUJUAN PEMBELAJARAN:
#   1. Memahami cara menggambar shapes pada gambar OpenCV
#   2. Menulis teks pada gambar dengan cv2.putText()
#   3. Mengerti makna setiap parameter fungsi drawing
#   4. Menguasai color format BGR OpenCV
# ============================================================================

# REFERENSI: Lihat CV2_FUNCTIONS_REFERENCE.py untuk dokumentasi lengkap cv2 functions

# ====================
# IMPORT LIBRARY
# ====================
import cv2          # Library OpenCV untuk computer vision
import numpy as np  # Library NumPy untuk array operations
import matplotlib.pyplot as plt  # Untuk visualization
import os           # Library untuk operasi file

# ============================================================================
# VARIABEL YANG BISA DIUBAH-UBAH (EKSPERIMEN)
# ============================================================================

# Ukuran canvas (tinggi, lebar) dalam pixel
CANVAS_SIZE = (600, 800)

# Warna latar belakang dalam format BGR
# BGR = Blue, Green, Red (bukan RGB!)
# (30, 30, 30) = Abu-abu gelap
WARNA_BACKGROUND = (30, 30, 30)

# Font untuk teks
FONT = cv2.FONT_HERSHEY_SIMPLEX  # Font paling umum

# ============================================================================
# FUNGSI HELPER
# ============================================================================

def buat_canvas(ukuran=CANVAS_SIZE, warna=WARNA_BACKGROUND):
    """
    Membuat canvas kosong untuk menggambar
    
    Parameter:
        ukuran (tuple): (tinggi, lebar) dalam pixel
        warna (tuple): Warna BGR untuk background
        
    Return:
        numpy.ndarray: Array gambar dengan warna uniform
    """
    tinggi, lebar = ukuran
    # Buat array 3D dengan shape (tinggi, lebar, 3_channels)
    # Semua pixel diisi dengan warna yang sama
    canvas = np.full((tinggi, lebar, 3), warna, dtype=np.uint8)
    return canvas


def simpan_gambar(gambar, nama_file):
    """Menyimpan gambar ke file"""
    direktori_script = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(direktori_script, "output", "output6")
    os.makedirs(output_dir, exist_ok=True)
    path_output = os.path.join(output_dir, nama_file)
    cv2.imwrite(path_output, gambar)
    print(f"[SUKSES] Gambar disimpan: {path_output}")


# ============================================================================
# DEMO 1: MENGGAMBAR GARIS (cv2.line)
# ============================================================================

def demo_menggambar_garis():
    """
    Mendemonstrasikan cara menggambar garis dengan cv2.line()
    
    Sintaks: cv2.line(gambar, titik_awal, titik_akhir, warna, ketebalan, tipe_garis)
    """
    print("\n" + "="*70)
    print("DEMO 1: MENGGAMBAR GARIS (cv2.line)")
    print("="*70)
    
    canvas = buat_canvas()
    
    # ==== CONTOH 1: Garis sederhana ====
    print("\n1. Garis Horizontal Sederhana")
    print("   Code: cv2.line(canvas, (50, 50), (750, 50), (255, 0, 0), 2)")
    print("   Penjelasan:")
    print("      - canvas         : Gambar yang akan digambar")
    print("      - (50, 50)       : Koordinat awal (x=50, y=50)")
    print("      - (750, 50)      : Koordinat akhir (x=750, y=50)")
    print("      - (255, 0, 0)    : Warna BIRU dalam format BGR")
    print("      - 2              : Ketebalan garis 2 pixel")
    #
    # Parameter penjelasan:
    # canvas       = gambar yang akan dimodifikasi
    # (50, 50)     = posisi X=50 pixel dari kiri, Y=50 pixel dari atas
    # (750, 50)    = posisi tujuan (horizontal line karena Y sama)
    # (255, 0, 0)  = BGR format: Blue=255, Green=0, Red=0 → BIRU
    # 2            = ketebalan garis
    #
    cv2.line(canvas, (50, 50), (750, 50), (255, 0, 0), 2)
    
    # Tulis label untuk garis ini
    # Parameter cv2.putText dijelaskan di bawah
    cv2.putText(
        canvas,                                 # a) Gambar yang akan ditulis
        "Garis Horizontal",                     # b) Teks yang ditampilkan
        (300, 70),                              # c) Posisi (x=300, y=70) - BAWAH KIRI teks
        cv2.FONT_HERSHEY_SIMPLEX,              # d) Jenis font
        0.6,                                    # e) Ukuran font (1.0 = normal)
        (255, 255, 255),                       # f) Warna teks BGR = PUTIH
        1                                       # g) Ketebalan teks
    )
    
    # ==== CONTOH 2: Garis vertikal ====
    print("\n2. Garis Vertikal")
    print("   Koordinat awal dan akhir memiliki X yang sama")
    cv2.line(
        canvas,                                 # Gambar
        (400, 100),                             # Titik awal (x=400, y=100)
        (400, 500),                             # Titik akhir (x=400, y=500) - VERTIKAL
        (0, 255, 0),                            # Warna HIJAU BGR
        2                                       # Ketebalan
    )
    cv2.putText(canvas, "Vertikal", (420, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # ==== CONTOH 3: Garis diagonal ====
    print("\n3. Garis Diagonal")
    print("   Koordinat awal dan akhir berbeda di X dan Y")
    cv2.line(
        canvas,
        (100, 150),                             # Titik awal
        (300, 350),                             # Titik akhir (diagonal)
        (0, 0, 255),                            # Warna MERAH BGR
        2
    )
    cv2.putText(canvas, "Diagonal", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # ==== CONTOH 4: Garis dengan ketebalan berbeda ====
    print("\n4. Garis dengan Ketebalan Berbeda")
    y_pos = 200
    for thickness in [1, 2, 4, 8]:
        cv2.line(canvas, (500, y_pos), (750, y_pos), (100, 200, 255), thickness)
        cv2.putText(canvas, f"{thickness}px", (760, y_pos+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_pos += 40
    
    # ==== CONTOH 5: Garis dengan LINE_AA (anti-aliased) ====
    print("\n5. Garis dengan Anti-Aliasing (LINE_AA)")
    print("   Parameter ke-6 dalam cv2.line() adalah lineType")
    print("   - cv2.LINE_8   : Default, standar")
    print("   - cv2.LINE_AA  : Anti-aliased (lebih smooth)")
    
    # Garis dengan anti-aliasing
    cv2.line(
        canvas,
        (550, 380),                             # Titik awal
        (750, 480),                             # Titik akhir
        (255, 255, 0),                          # Warna CYAN
        2,                                      # Ketebalan
        cv2.LINE_AA                             # Line type: Anti-Aliased (smooth)
    )
    cv2.putText(canvas, "LINE_AA", (580, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Garis normal
    cv2.line(
        canvas,
        (550, 500),
        (750, 600),
        (255, 255, 0),
        2,
        cv2.LINE_8                              # Line type: Standard 8-connected
    )
    cv2.putText(canvas, "LINE_8", (580, 560), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return canvas


# ============================================================================
# DEMO 2: MENGGAMBAR RECTANGLE (cv2.rectangle)
# ============================================================================

def demo_menggambar_rectangle():
    """
    Mendemonstrasikan cara menggambar rectangle/kotak dengan cv2.rectangle()
    
    Sintaks: cv2.rectangle(gambar, titik_kiri_atas, titik_kanan_bawah, warna, ketebalan)
    """
    print("\n" + "="*70)
    print("DEMO 2: MENGGAMBAR RECTANGLE (cv2.rectangle)")
    print("="*70)
    
    canvas = buat_canvas()
    
    # ==== CONTOH 1: Rectangle outline ====
    print("\n1. Rectangle Outline (Hanya Garis Tepi)")
    print("   Code: cv2.rectangle(canvas, (50, 50), (200, 150), (255, 0, 0), 2)")
    print("   Parameter:")
    print("      - (50, 50)       : Koordinat KIRI ATAS (top-left)")
    print("      - (200, 150)     : Koordinat KANAN BAWAH (bottom-right)")
    print("      - (255, 0, 0)    : Warna tepi = BIRU")
    print("      - 2              : Ketebalan garis (tidak -1, jadi outline saja)")
    print()
    # cv2.rectangle modifies canvas in-place
    cv2.rectangle(
        canvas,                                 # a) Gambar yang akan diubah
        (50, 50),                               # b) Titik KIRI ATAS (x1, y1)
        (200, 150),                             # c) Titik KANAN BAWAH (x2, y2)
        (255, 0, 0),                            # d) Warna BIRU BGR
        2                                       # e) Ketebalan 2 pixel (outline)
    )
    cv2.putText(canvas, "Outline", (90, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # ==== CONTOH 2: Rectangle filled (diisi warna) ====
    print("\n2. Rectangle Filled (Diisi Penuh)")
    print("   Ganti parameter thickness menjadi -1 untuk filled")
    cv2.rectangle(
        canvas,
        (250, 50),                              # Top-left
        (400, 150),                             # Bottom-right
        (0, 255, 0),                            # Warna HIJAU
        -1                                      # -1 = filled (diisi penuh)
    )
    cv2.putText(canvas, "Filled", (295, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # ==== CONTOH 3: Rectangle dengan berbagai ukuran ====
    print("\n3. Rectangle dengan Berbagai Ukuran")
    rects = [
        ((50, 200), (120, 270), (0, 0, 255), 2, "Small"),
        ((150, 200), (300, 270), (0, 165, 255), 2, "Medium"),
        ((350, 200), (550, 270), (255, 0, 255), 2, "Large"),
    ]
    
    for (x1, y1), (x2, y2), color, thick, label in rects:
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, thick)
        text_x = x1 + (x2 - x1) // 2 - 20
        text_y = y1 + (y2 - y1) // 2
        cv2.putText(canvas, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # ==== CONTOH 4: Rectangle dengan ketebalan berbeda ====
    print("\n4. Rectangle dengan Ketebalan Garis Berbeda")
    y_pos = 300
    for thickness in [1, 2, 4, 8]:
        cv2.rectangle(canvas, (50, y_pos), (200, y_pos + 50), (100, 100, 255), thickness)
        cv2.putText(canvas, f"T={thickness}", (220, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        y_pos += 80
    
    # ==== CONTOH 5: Persegi (Square) ====
    print("\n5. Persegi (Kotak dengan sisi sama)")
    side_length = 100
    cv2.rectangle(
        canvas,
        (500, 100),                             # Top-left
        (500 + side_length, 100 + side_length), # Bottom-right (square)
        (128, 0, 128),                          # Warna UNGU
        -1
    )
    cv2.putText(canvas, "Square\n100x100", (515, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return canvas


# ============================================================================
# DEMO 3: MENGGAMBAR CIRCLE (cv2.circle)
# ============================================================================

def demo_menggambar_circle():
    """
    Mendemonstrasikan cara menggambar lingkaran dengan cv2.circle()
    
    Sintaks: cv2.circle(gambar, pusat, radius, warna, ketebalan)
    """
    print("\n" + "="*70)
    print("DEMO 3: MENGGAMBAR CIRCLE (cv2.circle)")
    print("="*70)
    
    canvas = buat_canvas()
    
    # ==== CONTOH 1: Circle outline ====
    print("\n1. Circle Outline (Hanya Garis Tepi)")
    print("   Code: cv2.circle(canvas, (100, 100), 50, (255, 0, 0), 2)")
    print("   Parameter:")
    print("      - (100, 100)     : Koordinat PUSAT lingkaran (x, y)")
    print("      - 50             : Radius (jari-jari) dalam pixel")
    print("      - (255, 0, 0)    : Warna = BIRU")
    print("      - 2              : Ketebalan garis outline")
    print()
    cv2.circle(
        canvas,                                 # a) Gambar
        (100, 100),                             # b) Pusat lingkaran (x, y)
        50,                                     # c) Radius dalam pixel
        (255, 0, 0),                            # d) Warna BIRU BGR
        2                                       # e) Ketebalan (tidak -1, jadi outline)
    )
    cv2.putText(canvas, "Outline", (70, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # ==== CONTOH 2: Circle filled ====
    print("\n2. Circle Filled (Diisi Penuh)")
    cv2.circle(
        canvas,
        (250, 100),                             # Pusat di (250, 100)
        50,                                     # Radius 50 pixel
        (0, 255, 0),                            # Warna HIJAU
        -1                                      # -1 = filled
    )
    cv2.putText(canvas, "Filled", (225, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    # ==== CONTOH 3: Lingkaran dengan radius berbeda ====
    print("\n3. Lingkaran dengan Radius Berbeda")
    center_x, center_y = 450, 100
    for i, radius in enumerate([15, 30, 45, 60]):
        cv2.circle(canvas, (center_x, center_y), radius, (100, 150, 255), 1)
        cv2.putText(canvas, f"r={radius}", (center_x + 70, center_y - 60 + i*30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    
    # ==== CONTOH 4: Konsentrik lingkaran ====
    print("\n4. Konsentrik Lingkaran (Lingkaran dalam lingkaran)")
    center = (100, 350)
    for i, (radius, color) in enumerate([(80, (255, 0, 0)), (60, (0, 255, 0)), 
                                          (40, (0, 0, 255)), (20, (255, 255, 0))]):
        cv2.circle(canvas, center, radius, color, -1)
    cv2.putText(canvas, "Konsentrik", (140, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    # ==== CONTOH 5: Target (bullseye) ====
    print("\n5. Target Pattern (Bullseye)")
    center = (400, 350)
    colors = [(255, 0, 0), (255, 255, 255), (0, 0, 255)]
    for i, (radius, color) in enumerate([(60, colors[0]), (40, colors[1]), (20, colors[2])]):
        cv2.circle(canvas, center, radius, color, -1)
    cv2.putText(canvas, "Target", (360, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    return canvas


# ============================================================================
# DEMO 4: MENULIS TEKS (cv2.putText) - FOKUS UTAMA
# ============================================================================

def demo_menulis_teks():
    """
    Mendemonstrasikan cara menulis teks dengan cv2.putText()
    DOKUMENTASI DETAIL untuk semua parameter!
    
    Sintaks: cv2.putText(gambar, teks, posisi, font, ukuran, warna, ketebalan)
    """
    print("\n" + "="*70)
    print("DEMO 4: MENULIS TEKS (cv2.putText) - DOKUMENTASI LENGKAP")
    print("="*70)
    
    canvas = buat_canvas()
    
    # ==== CONTOH 1: Teks sederhana ====
    print("\n1. Teks Sederhana")
    print("   Code: cv2.putText(canvas, 'Hello', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)")
    print("\n   PARAMETER PENJELASAN:")
    print("   a) canvas                      = Gambar yang akan ditulis (akan dimodifikasi in-place!)")
    print("   b) 'Hello'                     = String teks yang ditampilkan")
    print("   c) (50, 50)                    = Koordinat (x, y) BAWAH KIRI teks")
    print("   d) cv2.FONT_HERSHEY_SIMPLEX   = Jenis font yang digunakan")
    print("   e) 1.0                         = Font scale (1.0=normal, 0.5=kecil, 2.0=besar)")
    print("   f) (255, 255, 255)             = Warna teks BGR = PUTIH")
    print("   g) 2                           = Ketebalan teks dalam pixel")
    print()
    # Tulis teks
    cv2.putText(
        canvas,                                 # a) Gambar
        "Hello OpenCV!",                        # b) Teks
        (50, 70),                               # c) Posisi (x=50 dari kiri, y=70 dari atas)
        cv2.FONT_HERSHEY_SIMPLEX,              # d) Font jenis
        1.0,                                    # e) Ukuran font (1.0 = normal)
        (255, 255, 255),                       # f) Warna PUTIH
        2                                       # g) Ketebalan
    )
    
    # ==== CONTOH 2: Font berbeda ====
    print("\n2. Font Jenis Berbeda")
    print("   Parameter d) fontFace bisa menjadi:")
    print("   - cv2.FONT_HERSHEY_SIMPLEX  (paling umum)")
    print("   - cv2.FONT_HERSHEY_PLAIN")
    print("   - cv2.FONT_HERSHEY_DUPLEX")
    print("   - cv2.FONT_HERSHEY_COMPLEX")
    
    fonts = [
        (cv2.FONT_HERSHEY_SIMPLEX, "SIMPLEX"),
        (cv2.FONT_HERSHEY_PLAIN, "PLAIN"),
        (cv2.FONT_HERSHEY_DUPLEX, "DUPLEX"),
        (cv2.FONT_HERSHEY_COMPLEX, "COMPLEX"),
    ]
    
    y_pos = 150
    for font_id, font_name in fonts:
        cv2.putText(canvas, f"Font: {font_name}", (50, y_pos), font_id, 0.7, (100, 200, 255), 1)
        y_pos += 50
    
    # ==== CONTOH 3: Font scale berbeda ====
    print("\n3. Font Scale (Ukuran) Berbeda")
    print("   Parameter e) fontScale:")
    print("   - 0.5: Setengah dari normal (kecil)")
    print("   - 1.0: Normal (default)")
    print("   - 2.0: Dua kali normal (besar)")
    
    scales = [0.5, 1.0, 1.5, 2.0]
    y_pos = 420
    for scale in scales:
        cv2.putText(canvas, f"Scale {scale}", (50, y_pos), cv2.FONT_HERSHEY_SIMPLEX, scale, (200, 100, 255), 1)
        y_pos += 45
    
    # ==== CONTOH 4: Ketebalan teks berbeda ====
    print("\n4. Ketebalan Teks Berbeda")
    print("   Parameter g) thickness:")
    print("   - 1: Tipis")
    print("   - 2: Normal")
    print("   - 3: Tebal")
    print("   - 4+: Sangat tebal")
    
    thickness_list = [1, 2, 3, 4]
    y_pos = 150
    for thickness in thickness_list:
        cv2.putText(canvas, f"Thickness {thickness}", (350, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (150, 255, 100), thickness)
        y_pos += 50
    
    # ==== CONTOH 5: Warna teks berbeda (BGR) ====
    print("\n5. Warna Teks Berbeda (Format BGR)")
    print("   Parameter f) color adalah tuple (B, G, R)")
    print("   - (255, 0, 0)    = BIRU")
    print("   - (0, 255, 0)    = HIJAU")
    print("   - (0, 0, 255)    = MERAH")
    print("   - (255, 255, 0)  = CYAN")
    print("   - (255, 0, 255)  = MAGENTA")
    print("   - (0, 255, 255)  = KUNING")
    
    colors_text = [
        ((255, 0, 0), "BIRU"),
        ((0, 255, 0), "HIJAU"),
        ((0, 0, 255), "MERAH"),
        ((255, 255, 0), "CYAN"),
    ]
    
    y_pos = 150
    for color, color_name in colors_text:
        cv2.putText(canvas, color_name, (350, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y_pos += 50
    
    # ==== CONTOH 6: Informasi teks ====
    print("\n6. Menampilkan Informasi (Kombinasi Parameter)")
    info_text = "CV Vision 2024"
    # Tulis dengan background
    cv2.putText(canvas, info_text, (150, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    return canvas


# ============================================================================
# PROGRAM UTAMA
# ============================================================================

def main():
    """Fungsi utama program"""
    
    print("\n" + "="*70)
    print("PRAKTIKUM 6: MENGGAMBAR SHAPES - ENHANCED VERSION")
    print("Dengan Dokumentasi Lengkap untuk Setiap Parameter cv2")
    print("="*70)
    
    # Jalankan semua demo
    demos = [
        ("Menggambar Garis", demo_menggambar_garis()),
        ("Menggambar Rectangle", demo_menggambar_rectangle()),
        ("Menggambar Circle", demo_menggambar_circle()),
        ("Menulis Teks", demo_menulis_teks()),
    ]
    
    # Tampilkan setiap demo
    for title, canvas in demos:
        print(f"\n\nMenampilkan hasil: {title}")
        print("Tekan tombol apapun untuk lanjut ke demo berikutnya...")
        cv2.imshow(title, canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Simpan hasil
        filename = f"06_shapes_{title.lower().replace(' ', '_')}.png"
        simpan_gambar(canvas, filename)
    
    print("\n" + "="*70)
    print("PRAKTIKUM SELESAI!")
    print("="*70)
    print("\nKESIMPULAN:")
    print("1. cv2.line()      : Menggambar garis dengan parameter (gambar, titik_awal, titik_akhir, warna, ketebalan)")
    print("2. cv2.rectangle() : Menggambar kotak dengan parameter (gambar, kiri_atas, kanan_bawah, warna, ketebalan)")
    print("3. cv2.circle()    : Menggambar lingkaran dengan parameter (gambar, pusat, radius, warna, ketebalan)")
    print("4. cv2.putText()   : Menulis teks dengan parameter (gambar, teks, posisi, font, scale, warna, ketebalan)")
    print("\nCAT PENTING:")
    print("- Semua koordinat (x, y) menggunakan sistem: x=horizontal, y=vertical")
    print("- Warna menggunakan format BGR (bukan RGB!)")
    print("- Ketebalan -1 untuk shape yang diisi (filled)")
    print("- cv2.putText() menggunakan posisi BAWAH KIRI teks")


if __name__ == "__main__":
    main()

