"""
object_recognizer.py
Fase 3: Deteksi dan lokalisasi objek dalam scene menggunakan feature-based matching.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from utils.io_utils import load_image, load_images_from_folder


class ObjectRecognizer:
    """
    Mendeteksi objek template dalam gambar scene menggunakan SIFT + FLANN + RANSAC.

    Contoh penggunaan:
        rec = ObjectRecognizer(min_inliers=10, confidence_threshold=0.3)
        rec.add_template('buku', 'data/templates/buku.jpg')
        detections = rec.recognize(scene_image)
    """

    def __init__(self, min_inliers=10, confidence_threshold=0.30, ratio=0.75):
        """
        Args:
            min_inliers:            Minimal inlier agar objek dianggap terdeteksi
            confidence_threshold:   Minimal confidence score (0.0 – 1.0)
            ratio:                  Threshold ratio test Lowe
        """
        np.random.seed(42)
        cv2.setRNGSeed(42)

        self.min_inliers = min_inliers
        self.confidence_threshold = confidence_threshold
        self.ratio = ratio

        self.sift = cv2.SIFT_create()
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # Database template: {nama: {'image': img, 'kp': kp, 'des': des, 'shape': (h,w)}}
        self.templates = {}

    def add_template(self, name, image_or_path):
        """
        Tambahkan template ke database.

        Args:
            name:          Nama/identifer objek
            image_or_path: Path file gambar atau numpy array
        """
        if isinstance(image_or_path, str):
            img = load_image(image_or_path)
            if img is None:
                return False
        else:
            img = image_or_path

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = self.sift.detectAndCompute(gray, None)

        if des is None or len(des) < 5:
            print(f"[WARN] Template '{name}' terlalu sedikit fitur, dilewati.")
            return False

        self.templates[name] = {
            'image': img,
            'kp': kp,
            'des': des.astype(np.float32),
            'shape': gray.shape,  # (h, w)
        }
        print(f"[INFO] Template '{name}' ditambahkan ({len(kp)} keypoints)")
        return True

    def load_templates_from_folder(self, folder):
        """Muat semua gambar dari folder sebagai template."""
        images = load_images_from_folder(folder)
        for fname, img in images.items():
            name = os.path.splitext(fname)[0]
            self.add_template(name, img)

    def _match_template(self, scene_kp, scene_des, template_name):
        """
        Cocokkan satu template ke scene.

        Returns:
            dict hasil matching atau None
        """
        tmpl = self.templates[template_name]
        tmpl_des = tmpl['des']
        tmpl_kp = tmpl['kp']

        if scene_des is None or len(scene_des) < 2 or len(tmpl_des) < 2:
            return None

        try:
            raw = self.flann.knnMatch(tmpl_des, scene_des.astype(np.float32), k=2)
        except cv2.error:
            return None

        good = []
        for pair in raw:
            if len(pair) == 2:
                m, n = pair
                if m.distance < self.ratio * n.distance:
                    good.append(m)

        if len(good) < 4:
            return None

        pts_tmpl  = np.float32([tmpl_kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        pts_scene = np.float32([scene_kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(pts_tmpl, pts_scene, cv2.RANSAC, 5.0)
        if H is None:
            return None

        n_inliers = int(np.sum(mask))
        confidence = n_inliers / len(good) if good else 0.0

        return {
            'name': template_name,
            'H': H,
            'n_inliers': n_inliers,
            'n_matches': len(good),
            'confidence': confidence,
            'matches': good,
            'mask': mask,
        }

    def recognize(self, scene_image):
        """
        Deteksi semua template yang ada di gambar scene.

        Args:
            scene_image: Gambar scene (BGR)

        Returns:
            List dict objek terdeteksi, sudah difilter dan diurutkan
        """
        gray_scene = cv2.cvtColor(scene_image, cv2.COLOR_BGR2GRAY)
        scene_kp, scene_des = self.sift.detectAndCompute(gray_scene, None)

        detections = []
        for name in self.templates:
            result = self._match_template(scene_kp, scene_des, name)
            if result is None:
                continue

            accepted = (result['n_inliers'] >= self.min_inliers and
                        result['confidence'] >= self.confidence_threshold)
            result['accepted'] = accepted
            detections.append(result)

        # Urutkan berdasarkan confidence descending
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        return detections

    def print_results(self, detections):
        """Cetak hasil deteksi ke konsol."""
        print("\n[Objek Terdeteksi]")
        print("-" * 55)
        if not detections:
            print("  Tidak ada objek yang terdeteksi.")
            return
        for i, d in enumerate(detections, 1):
            status = "" if d['accepted'] else "(REJECTED)"
            print(f"  [{i}] {d['name']:<25} Score: {d['confidence']:.2f}  "
                  f"Inliers: {d['n_inliers']}/{d['n_matches']}  {status}")
        print()

    def visualize(self, scene_image, detections, save_path=None):
        """
        Gambar bounding polygon objek terdeteksi pada scene.

        Args:
            scene_image: Gambar scene asli
            detections:  Output dari recognize()
            save_path:   Path simpan (opsional)
        """
        result = scene_image.copy()
        colors = [(0, 255, 0), (255, 128, 0), (0, 200, 255), (255, 0, 200)]

        for i, d in enumerate(detections):
            if not d['accepted']:
                continue

            tmpl_shape = self.templates[d['name']]['shape']
            h, w = tmpl_shape
            corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
            transformed = cv2.perspectiveTransform(corners, d['H'])

            color = colors[i % len(colors)]
            cv2.polylines(result, [np.int32(transformed)], True, color, 3)

            # Label
            label_pt = (int(transformed[0][0][0]), int(transformed[0][0][1]) - 8)
            cv2.putText(result, f"{d['name']} ({d['confidence']:.2f})",
                        label_pt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        ax.set_title('Object Recognition — Hasil Deteksi', fontsize=13)
        ax.axis('off')
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"[INFO] Visualisasi disimpan: {save_path}")
        plt.show()


# ─── Demo standalone ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    def make_synthetic(label='obj', size=(150, 200)):
        """Buat gambar sintetis sederhana."""
        img = np.ones((size[0], size[1], 3), dtype=np.uint8) * 200
        np.random.seed(hash(label) % 100)
        for _ in range(15):
            x, y = np.random.randint(10, size[1]-10), np.random.randint(10, size[0]-10)
            cv2.circle(img, (x, y), np.random.randint(5, 20),
                       tuple(np.random.randint(50, 200, 3).tolist()), -1)
        cv2.putText(img, label, (5, size[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        return img

    rec = ObjectRecognizer(min_inliers=8)

    if len(sys.argv) >= 2:
        # Mode file: python object_recognizer.py <scene> [template1] [template2] ...
        scene = load_image(sys.argv[1])
        for tpath in sys.argv[2:]:
            name = os.path.splitext(os.path.basename(tpath))[0]
            rec.add_template(name, tpath)
    else:
        print("[INFO] Demo sintetis. Gunakan: python object_recognizer.py scene.jpg template1.jpg ...")
        # Buat template sintetis dan embed ke scene
        tmpl1 = make_synthetic('kotak_A')
        tmpl2 = make_synthetic('kotak_B')
        rec.add_template('kotak_A', tmpl1)
        rec.add_template('kotak_B', tmpl2)

        # Buat scene yang mengandung kedua template
        scene = np.ones((500, 700, 3), dtype=np.uint8) * 180
        scene[30:180, 50:250]  = tmpl1
        scene[200:350, 400:600] = tmpl2
        # Tambah noise
        noise = np.random.randint(0, 30, scene.shape, dtype=np.uint8)
        scene = cv2.add(scene, noise)

    detections = rec.recognize(scene)
    rec.print_results(detections)
    rec.visualize(scene, detections, save_path='results/recognition_result.png')
