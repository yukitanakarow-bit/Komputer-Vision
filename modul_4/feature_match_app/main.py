"""
main.py
Entry point utama — FeatureMatch Vision App
Modul 4: Deteksi Fitur dan Pencocokan

Cara pakai:
  python main.py                        # jalankan semua fase (demo sintetis)
  python main.py --fase 1               # hanya Fase 1: Benchmark
  python main.py --fase 2               # hanya Fase 2: Robust Matcher
  python main.py --fase 3               # hanya Fase 3: Object Recognition
  python main.py --fase 4               # hanya Fase 4: Image Retrieval
  python main.py --fase 1 --img foto.jpg  # dengan gambar sendiri
"""

import cv2
import numpy as np
import os
import sys
import argparse
from pathlib import Path

# ─── Impor modul-modul aplikasi ───────────────────────────────────────────────
from detector_benchmark import DetectorBenchmark
from robust_matcher import RobustMatcher
from object_recognizer import ObjectRecognizer
from image_retriever import ImageRetriever
from utils.io_utils import load_image, load_images_from_folder, ensure_dir

# ─── KONFIGURASI GLOBAL ───────────────────────────────────────────────────────
# Ubah parameter di sini tanpa menyentuh kode modul.
CONFIG = {
    # --- Umum ---
    'results_dir': 'results',
    'seed': 42,

    # --- Fase 1: Benchmark ---
    'benchmark': {
        'detectors': ['Harris', 'Shi-Tomasi', 'SIFT', 'ORB', 'AKAZE', 'FAST', 'BRISK'],
    },

    # --- Fase 2: Robust Matcher ---
    'matcher': {
        'combinations': [
            ('SIFT',  'FLANN'),
            ('ORB',   'BF'),
            ('AKAZE', 'FLANN'),
        ],
        'ratio': 0.75,
        'ransac_thresh': 5.0,
    },

    # --- Fase 3: Object Recognition ---
    'recognizer': {
        'templates_dir': 'data/templates',
        'min_inliers': 10,
        'confidence_threshold': 0.25,
    },

    # --- Fase 4: Image Retrieval ---
    'retrieval': {
        'database_dir': 'data/database',
        'top_k': 5,
        'index_path': 'results/retrieval_index.pkl',
    },
}

# ─── Fungsi pembuat gambar sintetis ──────────────────────────────────────────
def _make_synthetic_image(seed=0, size=(400, 600)):
    """Buat gambar sintetis dengan bentuk geometris acak."""
    np.random.seed(seed)
    cv2.setRNGSeed(seed)
    img = np.ones((*size, 3), dtype=np.uint8) * 50
    for _ in range(40):
        x, y = np.random.randint(20, size[1]-20), np.random.randint(20, size[0]-20)
        color = tuple(int(c) for c in np.random.randint(80, 255, 3))
        shape = np.random.choice(['circle', 'rect', 'line'])
        if shape == 'circle':
            cv2.circle(img, (x, y), np.random.randint(5, 35), color, -1)
        elif shape == 'rect':
            w, h = np.random.randint(10, 60), np.random.randint(10, 60)
            cv2.rectangle(img, (x, y), (x+w, y+h), color, -1)
        else:
            x2, y2 = np.random.randint(20, size[1]-20), np.random.randint(20, size[0]-20)
            cv2.line(img, (x, y), (x2, y2), color, np.random.randint(1, 4))
    return img


def _rotate_image(img, angle=15):
    """Rotasi gambar sebesar angle derajat (untuk membuat pasangan test)."""
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 0.95)
    return cv2.warpAffine(img, M, (w, h))


# ─── FASE 1 ───────────────────────────────────────────────────────────────────
def run_fase1(image=None):
    """Benchmark semua detektor fitur."""
    print("\n" + "=" * 60)
    print("  FASE 1 — Benchmark Detektor Fitur")
    print("=" * 60)

    if image is None:
        print("[INFO] Membuat gambar sintetis untuk benchmark...")
        image = _make_synthetic_image(seed=CONFIG['seed'])

    bench = DetectorBenchmark(detectors=CONFIG['benchmark']['detectors'])
    results = bench.compare_all(image)
    bench.print_table(results)

    save_dir = CONFIG['results_dir']
    ensure_dir(save_dir)
    bench.visualize_all(image, results, save_dir=save_dir)
    bench.plot_comparison(results, save_dir=save_dir)

    print("[OK] Fase 1 selesai.\n")
    return results


# ─── FASE 2 ───────────────────────────────────────────────────────────────────
def run_fase2(img1=None, img2=None):
    """Robust matching dengan berbagai kombinasi detektor + matcher."""
    print("\n" + "=" * 60)
    print("  FASE 2 — Robust Matcher")
    print("=" * 60)

    if img1 is None:
        print("[INFO] Membuat pasangan gambar sintetis...")
        img1 = _make_synthetic_image(seed=CONFIG['seed'])
        img2 = _rotate_image(img1, angle=12)

    save_dir = CONFIG['results_dir']
    ensure_dir(save_dir)

    for det, mat in CONFIG['matcher']['combinations']:
        rm = RobustMatcher(
            detector=det,
            matcher=mat,
            ratio=CONFIG['matcher']['ratio'],
            ransac_thresh=CONFIG['matcher']['ransac_thresh'],
        )
        save_path = os.path.join(save_dir, f'match_{det}_{mat}.png')
        rm.full_pipeline(img1, img2, verbose=True, save_path=save_path)

    print("[OK] Fase 2 selesai.\n")


# ─── FASE 3 ───────────────────────────────────────────────────────────────────
def run_fase3(scene_image=None, templates_dir=None):
    """Object recognition: deteksi template di dalam scene."""
    print("\n" + "=" * 60)
    print("  FASE 3 — Object Recognition")
    print("=" * 60)

    templates_dir = templates_dir or CONFIG['recognizer']['templates_dir']
    save_dir = CONFIG['results_dir']
    ensure_dir(save_dir)

    rec = ObjectRecognizer(
        min_inliers=CONFIG['recognizer']['min_inliers'],
        confidence_threshold=CONFIG['recognizer']['confidence_threshold'],
    )

    # Coba muat dari folder; jika kosong, gunakan demo sintetis
    tmpl_images = load_images_from_folder(templates_dir)
    if tmpl_images:
        for fname, img in tmpl_images.items():
            name = os.path.splitext(fname)[0]
            rec.add_template(name, img)
    else:
        print("[INFO] Folder templates kosong. Membuat template sintetis...")
        for i, label in enumerate(['objek_A', 'objek_B', 'objek_C']):
            tmpl = _make_synthetic_image(seed=i * 10, size=(200, 300))
            rec.add_template(label, tmpl)

        if scene_image is None:
            print("[INFO] Membuat scene sintetis...")
            scene_image = np.ones((600, 900, 3), dtype=np.uint8) * 120
            for i, label in enumerate(['objek_A', 'objek_B', 'objek_C']):
                tmpl = rec.templates[label]['image']
                h, w = tmpl.shape[:2]
                y0, x0 = 50 + i * 180, 50 + i * 200
                rotated = _rotate_image(tmpl, angle=5 * i)
                rh, rw = rotated.shape[:2]
                y_end = min(y0 + rh, scene_image.shape[0])
                x_end = min(x0 + rw, scene_image.shape[1])
                scene_image[y0:y_end, x0:x_end] = rotated[:y_end-y0, :x_end-x0]
            noise = np.random.randint(0, 20, scene_image.shape, dtype=np.uint8)
            scene_image = cv2.add(scene_image, noise)

    if scene_image is None:
        scene_image = _make_synthetic_image(seed=99, size=(500, 700))

    detections = rec.recognize(scene_image)
    rec.print_results(detections)
    rec.visualize(scene_image, detections,
                  save_path=os.path.join(save_dir, 'recognition_result.png'))

    print("[OK] Fase 3 selesai.\n")


# ─── FASE 4 ───────────────────────────────────────────────────────────────────
def run_fase4(query_image=None, db_folder=None):
    """Image retrieval: query gambar dan tampilkan top-k hasil."""
    print("\n" + "=" * 60)
    print("  FASE 4 — Image Retrieval")
    print("=" * 60)

    db_folder = db_folder or CONFIG['retrieval']['database_dir']
    save_dir = CONFIG['results_dir']
    ensure_dir(save_dir)

    ir = ImageRetriever(ratio=0.75)

    # Jika folder database ada dan berisi gambar, gunakan itu
    if os.path.exists(db_folder) and any(
            f.lower().endswith(('.jpg', '.jpeg', '.png'))
            for f in os.listdir(db_folder)):
        ir.build_index(db_folder)
    else:
        print("[INFO] Database kosong. Membuat gambar sintetis untuk demo...")
        ensure_dir(db_folder)
        labels = ['apel', 'buku', 'kursi', 'meja', 'botol', 'tas', 'sepatu', 'lampu', 'pulpen', 'kaca']
        for i, label in enumerate(labels):
            img = _make_synthetic_image(seed=i * 7, size=(200, 200))
            cv2.putText(img, label, (5, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv2.imwrite(os.path.join(db_folder, f'{label}.jpg'), img)
        ir.build_index(db_folder)

    if query_image is None:
        # Gunakan salah satu gambar database sebagai query (buku)
        q_path = os.path.join(db_folder, 'buku.jpg')
        if os.path.exists(q_path):
            query_image = load_image(q_path)
        else:
            query_image = _make_synthetic_image(seed=7, size=(200, 200))

    ir.save_index(CONFIG['retrieval']['index_path'])

    top_k = CONFIG['retrieval']['top_k']
    results = ir.query(query_image, top_k=top_k)
    ir.print_results(results)
    ir.visualize_results(query_image, results,
                         save_path=os.path.join(save_dir, 'retrieval_result.png'))

    print("[OK] Fase 4 selesai.\n")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='FeatureMatch Vision App — Modul 4'
    )
    parser.add_argument('--fase', type=int, choices=[1, 2, 3, 4],
                        help='Jalankan fase tertentu (1-4). Default: semua fase.')
    parser.add_argument('--img',  type=str, default=None,
                        help='Path gambar utama (untuk Fase 1 & 3 sebagai scene/query)')
    parser.add_argument('--img2', type=str, default=None,
                        help='Path gambar kedua (untuk Fase 2 sebagai pasangan matching)')
    parser.add_argument('--db',   type=str, default=None,
                        help='Path folder database (untuk Fase 4)')
    args = parser.parse_args()

    # Set seed untuk reproduksibilitas
    np.random.seed(CONFIG['seed'])
    cv2.setRNGSeed(CONFIG['seed'])

    # Pastikan folder output ada
    ensure_dir(CONFIG['results_dir'])

    # Muat gambar jika disediakan
    img_main = load_image(args.img) if args.img else None
    img2     = load_image(args.img2) if args.img2 else None

    if args.fase == 1:
        run_fase1(image=img_main)
    elif args.fase == 2:
        run_fase2(img1=img_main, img2=img2)
    elif args.fase == 3:
        run_fase3(scene_image=img_main)
    elif args.fase == 4:
        run_fase4(query_image=img_main, db_folder=args.db)
    else:
        # Jalankan semua fase
        print("\n╔══════════════════════════════════════════════╗")
        print("║   FeatureMatch Vision App — Semua Fase       ║")
        print("╚══════════════════════════════════════════════╝")
        run_fase1()
        run_fase2()
        run_fase3()
        run_fase4()
        print("\n✓ Semua fase selesai. Hasil disimpan di folder 'results/'.\n")


if __name__ == '__main__':
    main()
