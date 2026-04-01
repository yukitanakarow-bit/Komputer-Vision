"""
detector_benchmark.py
Fase 1: Perbandingan berbagai detektor fitur lokal.

Detektor yang dibandingkan:
  Harris, Shi-Tomasi, SIFT, ORB, AKAZE, FAST, BRISK
"""

import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
from utils.io_utils import load_image
from utils.visualization import show_side_by_side, plot_bar_chart
import os


class DetectorBenchmark:
    """
    Kelas untuk membandingkan berbagai detektor fitur secara sistematis.

    Contoh penggunaan:
        bench = DetectorBenchmark()
        results = bench.compare_all(image)
        bench.print_table(results)
        bench.visualize_all(image, results)
    """

    def __init__(self, detectors=None):
        """
        Args:
            detectors: List nama detektor yang ingin digunakan.
                       Default: semua detektor yang tersedia.
        """
        np.random.seed(42)
        cv2.setRNGSeed(42)

        self.available = ['Harris', 'Shi-Tomasi', 'SIFT', 'ORB', 'AKAZE', 'FAST', 'BRISK']
        self.detectors = detectors if detectors else self.available

    def _to_gray(self, image):
        """Konversi gambar ke grayscale jika perlu."""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def run_detector(self, name, image):
        """
        Jalankan satu detektor dan ukur waktu eksekusinya.

        Args:
            name: Nama detektor (str)
            image: Gambar input (BGR atau grayscale)

        Returns:
            dict berisi: keypoints, descriptors, time_ms, descriptor_info
        """
        gray = self._to_gray(image)
        kps, desc, desc_info = [], None, '-'

        try:
            t0 = time.perf_counter()

            if name == 'Harris':
                dst = cv2.cornerHarris(gray.astype(np.float32), blockSize=2, ksize=3, k=0.04)
                dst_norm = cv2.normalize(dst, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                threshold = 0.01 * dst_norm.max()
                coords = np.argwhere(dst_norm > threshold)
                kps = [cv2.KeyPoint(float(c[1]), float(c[0]), 3) for c in coords]

            elif name == 'Shi-Tomasi':
                corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)
                if corners is not None:
                    kps = [cv2.KeyPoint(float(c[0][0]), float(c[0][1]), 3) for c in corners]

            elif name == 'SIFT':
                sift = cv2.SIFT_create()
                kps, desc = sift.detectAndCompute(gray, None)
                desc_info = '128-D float'

            elif name == 'ORB':
                orb = cv2.ORB_create(nfeatures=500)
                kps, desc = orb.detectAndCompute(gray, None)
                desc_info = '32-B binary'

            elif name == 'AKAZE':
                akaze = cv2.AKAZE_create()
                kps, desc = akaze.detectAndCompute(gray, None)
                desc_info = '61-B binary'

            elif name == 'FAST':
                fast = cv2.FastFeatureDetector_create(threshold=20)
                kps = fast.detect(gray, None)

            elif name == 'BRISK':
                brisk = cv2.BRISK_create()
                kps, desc = brisk.detectAndCompute(gray, None)
                desc_info = '64-B binary'

            elapsed_ms = (time.perf_counter() - t0) * 1000

        except Exception as e:
            print(f"[ERROR] Detektor {name} gagal: {e}")
            return None

        # Hitung rata-rata response strength jika tersedia
        avg_resp = np.mean([kp.response for kp in kps]) if kps else 0.0

        return {
            'name': name,
            'keypoints': kps,
            'descriptors': desc,
            'n_keypoints': len(kps),
            'time_ms': elapsed_ms,
            'avg_response': avg_resp,
            'descriptor_info': desc_info,
        }

    def compare_all(self, image):
        """
        Jalankan semua detektor pada gambar yang sama.

        Args:
            image: Gambar input

        Returns:
            List dict hasil tiap detektor
        """
        results = []
        print("\n[INFO] Menjalankan benchmark detektor...\n")
        for name in self.detectors:
            res = self.run_detector(name, image)
            if res:
                results.append(res)
                print(f"  {name:12s}: {res['n_keypoints']:5d} keypoints  |  {res['time_ms']:7.2f} ms")
        return results

    def print_table(self, results):
        """Cetak tabel perbandingan ke konsol."""
        print("\n" + "=" * 65)
        print(f"{'Detektor':<12} | {'N Keypoints':>11} | {'Waktu (ms)':>10} | {'Deskriptor'}")
        print("-" * 65)
        for r in results:
            print(f"{r['name']:<12} | {r['n_keypoints']:>11} | {r['time_ms']:>10.2f} | {r['descriptor_info']}")
        print("=" * 65 + "\n")

    def visualize_all(self, image, results, save_dir=None):
        """
        Tampilkan keypoint dari semua detektor secara berdampingan.

        Args:
            image: Gambar asli
            results: Output dari compare_all()
            save_dir: Folder untuk menyimpan hasil (opsional)
        """
        imgs, titles = [], []
        for r in results:
            img_kp = cv2.drawKeypoints(
                image, r['keypoints'], None,
                color=(0, 200, 50),
                flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
            )
            imgs.append(img_kp)
            titles.append(f"{r['name']}\n({r['n_keypoints']} kp, {r['time_ms']:.1f}ms)")

        save_path = os.path.join(save_dir, 'benchmark_keypoints.png') if save_dir else None
        show_side_by_side(imgs, titles, save_path=save_path, figsize=(20, 4))

    def plot_comparison(self, results, save_dir=None):
        """
        Tampilkan bar chart perbandingan jumlah keypoint dan waktu.

        Args:
            results: Output dari compare_all()
            save_dir: Folder untuk menyimpan hasil (opsional)
        """
        names = [r['name'] for r in results]
        n_kps = [r['n_keypoints'] for r in results]
        times = [r['time_ms'] for r in results]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Chart jumlah keypoint
        axes[0].bar(names, n_kps, color='steelblue', edgecolor='navy', alpha=0.85)
        axes[0].set_title('Jumlah Keypoint per Detektor')
        axes[0].set_ylabel('Jumlah Keypoint')
        axes[0].set_xlabel('Detektor')
        for i, v in enumerate(n_kps):
            axes[0].text(i, v + max(n_kps) * 0.01, str(v), ha='center', fontsize=9)

        # Chart waktu eksekusi
        axes[1].bar(names, times, color='coral', edgecolor='darkred', alpha=0.85)
        axes[1].set_title('Waktu Eksekusi per Detektor')
        axes[1].set_ylabel('Waktu (ms)')
        axes[1].set_xlabel('Detektor')
        for i, v in enumerate(times):
            axes[1].text(i, v + max(times) * 0.01, f'{v:.1f}', ha='center', fontsize=9)

        plt.suptitle('Benchmark Detektor Fitur', fontsize=14, fontweight='bold')
        plt.tight_layout()

        if save_dir:
            path = os.path.join(save_dir, 'benchmark_chart.png')
            os.makedirs(save_dir, exist_ok=True)
            plt.savefig(path, dpi=100, bbox_inches='tight')
            print(f"[INFO] Chart disimpan: {path}")
        plt.show()


# ─── Demo standalone ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    img_path = sys.argv[1] if len(sys.argv) > 1 else None

    if img_path:
        image = load_image(img_path)
    else:
        # Buat gambar sintetis jika tidak ada input
        print("[INFO] Tidak ada gambar input. Menggunakan gambar sintetis.")
        image = np.zeros((400, 600, 3), dtype=np.uint8)
        for _ in range(30):
            x, y = np.random.randint(20, 580), np.random.randint(20, 380)
            cv2.circle(image, (x, y), np.random.randint(5, 30), tuple(np.random.randint(100, 255, 3).tolist()), -1)

    if image is None:
        print("[ERROR] Gambar tidak dapat dimuat.")
        exit(1)

    bench = DetectorBenchmark()
    results = bench.compare_all(image)
    bench.print_table(results)
    bench.visualize_all(image, results, save_dir='results')
    bench.plot_comparison(results, save_dir='results')
