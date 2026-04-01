"""
robust_matcher.py
Fase 2: Pipeline robust matching menggunakan FLANN/BF + Ratio Test + RANSAC.

Kombinasi yang didukung:
  SIFT+BF, SIFT+FLANN, ORB+BF, ORB+FLANN, AKAZE+BF, AKAZE+FLANN
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from utils.io_utils import load_image, save_image


class RobustMatcher:
    """
    Kelas robust matcher yang modular dengan ratio test dan RANSAC.

    Contoh penggunaan:
        rm = RobustMatcher(detector='SIFT', matcher='FLANN', ratio=0.75)
        kp1, des1 = rm.detect_and_compute(img1)
        kp2, des2 = rm.detect_and_compute(img2)
        good_matches = rm.match(des1, des2)
        H, mask, n_inliers = rm.verify_geometry(kp1, kp2, good_matches)
        rm.visualize(img1, img2, kp1, kp2, good_matches, mask)
    """

    BINARY_DETECTORS = {'ORB', 'AKAZE', 'BRISK'}

    def __init__(self, detector='SIFT', matcher='FLANN', ratio=0.75, ransac_thresh=5.0):
        """
        Args:
            detector: 'SIFT' | 'ORB' | 'AKAZE'
            matcher:  'FLANN' | 'BF'
            ratio:    Threshold Lowe's ratio test (0.0 – 1.0)
            ransac_thresh: Threshold RANSAC dalam piksel
        """
        self.detector_name = detector
        self.matcher_name = matcher
        self.ratio = ratio
        self.ransac_thresh = ransac_thresh
        self.is_binary = detector in self.BINARY_DETECTORS

        self._init_detector()
        self._init_matcher()

    def _init_detector(self):
        """Inisialisasi objek detektor sesuai nama."""
        name = self.detector_name
        try:
            if name == 'SIFT':
                self.detector = cv2.SIFT_create()
            elif name == 'ORB':
                self.detector = cv2.ORB_create(nfeatures=1000)
            elif name == 'AKAZE':
                self.detector = cv2.AKAZE_create()
            elif name == 'BRISK':
                self.detector = cv2.BRISK_create()
            else:
                raise ValueError(f"Detektor tidak dikenal: {name}")
        except Exception as e:
            raise RuntimeError(f"Gagal inisialisasi detektor {name}: {e}")

    def _init_matcher(self):
        """Inisialisasi matcher (FLANN atau BruteForce)."""
        name = self.matcher_name
        if name == 'FLANN':
            if self.is_binary:
                index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
            else:
                index_params = dict(algorithm=1, trees=5)
            search_params = dict(checks=50)
            self.matcher = cv2.FlannBasedMatcher(index_params, search_params)
        elif name == 'BF':
            norm = cv2.NORM_HAMMING if self.is_binary else cv2.NORM_L2
            self.matcher = cv2.BFMatcher(norm, crossCheck=False)
        else:
            raise ValueError(f"Matcher tidak dikenal: {name}")

    def detect_and_compute(self, img):
        """
        Deteksi keypoint dan hitung deskriptor.

        Args:
            img: Gambar input (BGR atau grayscale)

        Returns:
            (keypoints, descriptors)
        """
        if img is None:
            raise ValueError("Gambar tidak boleh None")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        kp, des = self.detector.detectAndCompute(gray, None)
        return kp, des

    def match(self, des1, des2):
        """
        Cocokkan deskriptor dengan ratio test Lowe.

        Args:
            des1, des2: Deskriptor gambar 1 dan 2

        Returns:
            List DMatch yang lolos ratio test
        """
        if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
            return []

        # Konversi tipe data jika perlu
        if not self.is_binary:
            des1 = des1.astype(np.float32)
            des2 = des2.astype(np.float32)

        raw_matches = self.matcher.knnMatch(des1, des2, k=2)
        good = []
        for pair in raw_matches:
            if len(pair) == 2:
                m, n = pair
                if m.distance < self.ratio * n.distance:
                    good.append(m)
        return good

    def verify_geometry(self, kp1, kp2, matches):
        """
        Verifikasi geometri menggunakan RANSAC untuk menghitung homography.

        Args:
            kp1, kp2: Keypoint gambar 1 dan 2
            matches: List DMatch dari ratio test

        Returns:
            (H, mask, n_inliers)
            H      : Matriks homography (atau None jika gagal)
            mask   : Array boolean inlier/outlier
            n_inliers: Jumlah inlier
        """
        MIN_MATCH = 4
        if len(matches) < MIN_MATCH:
            return None, None, 0

        pts1 = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        pts2 = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, self.ransac_thresh)
        n_inliers = int(np.sum(mask)) if mask is not None else 0
        return H, mask, n_inliers

    def visualize(self, img1, img2, kp1, kp2, matches, mask=None, save_path=None):
        """
        Visualisasi tiga panel: img1 kp | img2 kp | hasil match.

        Args:
            img1, img2: Gambar input
            kp1, kp2:   Keypoint
            matches:    List DMatch
            mask:       Mask inlier dari RANSAC (opsional)
            save_path:  Path untuk menyimpan (opsional)
        """
        # Gambar panel kiri & tengah: keypoint pada masing-masing gambar
        img1_kp = cv2.drawKeypoints(img1, kp1, None, color=(0, 200, 50))
        img2_kp = cv2.drawKeypoints(img2, kp2, None, color=(0, 200, 50))

        # Panel kanan: hasil matching dengan warna inlier/outlier
        if mask is not None:
            inlier_matches  = [m for i, m in enumerate(matches) if mask[i]]
            outlier_matches = [m for i, m in enumerate(matches) if not mask[i]]
            # Gambar outlier merah dulu, lalu inlier hijau di atas
            match_img = cv2.drawMatches(img1, kp1, img2, kp2, outlier_matches, None,
                                        matchColor=(0, 0, 255), singlePointColor=(200, 200, 200),
                                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
            match_img = cv2.drawMatches(img1, kp1, img2, kp2, inlier_matches, match_img,
                                        matchColor=(0, 255, 0), singlePointColor=(200, 200, 200),
                                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS |
                                              cv2.DrawMatchesFlags_DRAW_OVER_OUTIMG)
        else:
            match_img = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], None,
                                        matchColor=(0, 200, 200),
                                        flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        for ax, img, title in zip(axes,
                                   [img1_kp, img2_kp, match_img],
                                   ['Gambar 1 - Keypoint', 'Gambar 2 - Keypoint',
                                    f'Matching (hijau=inlier, merah=outlier)']):
            ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ax.set_title(title, fontsize=10)
            ax.axis('off')

        plt.suptitle(f'{self.detector_name} + {self.matcher_name}  |  ratio={self.ratio}',
                     fontsize=13, fontweight='bold')
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"[INFO] Visualisasi disimpan: {save_path}")
        plt.show()

    def full_pipeline(self, img1, img2, verbose=True, save_path=None):
        """
        Jalankan pipeline lengkap: detect → match → RANSAC → visualize.

        Args:
            img1, img2: Gambar input
            verbose:    Cetak log detail
            save_path:  Path simpan hasil (opsional)

        Returns:
            dict hasil pipeline
        """
        t0 = time.perf_counter()

        kp1, des1 = self.detect_and_compute(img1)
        kp2, des2 = self.detect_and_compute(img2)

        good_matches = self.match(des1, des2)
        H, mask, n_inliers = self.verify_geometry(kp1, kp2, good_matches)

        elapsed = (time.perf_counter() - t0) * 1000

        if verbose:
            print(f"\n[RobustMatcher] {self.detector_name}+{self.matcher_name}")
            print(f"  Keypoint gambar 1  : {len(kp1)}")
            print(f"  Keypoint gambar 2  : {len(kp2)}")
            print(f"  Setelah ratio test : {len(good_matches)}")
            print(f"  Inlier (RANSAC)    : {n_inliers}")
            print(f"  Waktu total        : {elapsed:.1f} ms")

        self.visualize(img1, img2, kp1, kp2, good_matches, mask, save_path=save_path)

        return {
            'kp1': kp1, 'kp2': kp2,
            'matches': good_matches,
            'H': H, 'mask': mask,
            'n_inliers': n_inliers,
            'time_ms': elapsed,
        }


# ─── Demo standalone ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    def make_test_pair():
        """Buat pasangan gambar sintetis untuk demo."""
        base = np.zeros((300, 400, 3), dtype=np.uint8)
        for _ in range(20):
            x, y = np.random.randint(20, 380), np.random.randint(20, 280)
            cv2.circle(base, (x, y), np.random.randint(5, 25),
                       tuple(np.random.randint(100, 255, 3).tolist()), -1)
        # Gambar kedua adalah versi dengan sedikit transformasi
        M = cv2.getRotationMatrix2D((200, 150), 10, 1.0)
        rotated = cv2.warpAffine(base, M, (400, 300))
        return base, rotated

    if len(sys.argv) >= 3:
        img1 = load_image(sys.argv[1])
        img2 = load_image(sys.argv[2])
    else:
        print("[INFO] Menggunakan gambar sintetis untuk demo.")
        img1, img2 = make_test_pair()

    for det, mat in [('SIFT', 'FLANN'), ('ORB', 'BF'), ('AKAZE', 'FLANN')]:
        print(f"\n{'='*50}")
        rm = RobustMatcher(detector=det, matcher=mat)
        rm.full_pipeline(img1, img2, save_path=f'results/match_{det}_{mat}.png')
