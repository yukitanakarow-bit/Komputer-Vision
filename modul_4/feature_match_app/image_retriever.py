"""
image_retriever.py
Fase 4: Sistem pencarian gambar berbasis fitur (Image Retrieval).

Cara kerja:
  1. Build index: ekstrak SIFT dari semua gambar database.
  2. Query: cocokkan gambar query ke semua gambar di index.
  3. Return top-k gambar paling mirip berdasarkan jumlah match.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import pickle
import time
from utils.io_utils import load_image, load_images_from_folder


class ImageRetriever:
    """
    Sistem image retrieval sederhana berbasis SIFT matching.

    Contoh penggunaan:
        ir = ImageRetriever()
        ir.build_index('data/database')
        results = ir.query(query_image, top_k=5)
        ir.visualize_results(query_image, results)
    """

    def __init__(self, ratio=0.75):
        """
        Args:
            ratio: Threshold ratio test Lowe untuk matching
        """
        np.random.seed(42)
        cv2.setRNGSeed(42)

        self.ratio = ratio
        self.sift = cv2.SIFT_create()
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

        # index: list of {'name', 'path', 'image', 'kp', 'des'}
        self.index = []

    def build_index(self, database_folder):
        """
        Ekstrak fitur semua gambar di folder database dan simpan ke index.

        Args:
            database_folder: Path folder berisi gambar database

        Returns:
            Jumlah gambar yang berhasil diindeks
        """
        images = load_images_from_folder(database_folder)
        self.index = []

        print(f"\n[INFO] Membangun index dari {len(images)} gambar...")
        t0 = time.perf_counter()

        for fname, img in images.items():
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            kp, des = self.sift.detectAndCompute(gray, None)
            if des is None or len(des) < 5:
                print(f"  [SKIP] {fname} — terlalu sedikit fitur")
                continue
            self.index.append({
                'name': fname,
                'path': os.path.join(database_folder, fname),
                'image': img,
                'kp': kp,
                'des': des.astype(np.float32),
            })

        elapsed = (time.perf_counter() - t0) * 1000
        print(f"[INFO] Index selesai: {len(self.index)} gambar dalam {elapsed:.1f} ms\n")
        return len(self.index)

    def _score_pair(self, query_des, db_des):
        """
        Hitung skor kesamaan antara query dan satu entri database.

        Returns:
            Jumlah match yang lolos ratio test
        """
        if query_des is None or db_des is None:
            return 0
        if len(query_des) < 2 or len(db_des) < 2:
            return 0
        try:
            raw = self.flann.knnMatch(query_des, db_des, k=2)
        except cv2.error:
            return 0
        count = sum(1 for pair in raw if len(pair) == 2 and pair[0].distance < self.ratio * pair[1].distance)
        return count

    def query(self, query_image, top_k=5):
        """
        Cari gambar paling mirip di database.

        Args:
            query_image: Gambar query (BGR)
            top_k:       Jumlah hasil yang dikembalikan

        Returns:
            List dict {'name', 'image', 'score'}, sudah diurutkan descending
        """
        if not self.index:
            print("[WARN] Index kosong! Jalankan build_index() terlebih dahulu.")
            return []

        gray_q = cv2.cvtColor(query_image, cv2.COLOR_BGR2GRAY)
        kp_q, des_q = self.sift.detectAndCompute(gray_q, None)
        if des_q is None:
            print("[WARN] Query tidak memiliki fitur yang cukup.")
            return []

        des_q = des_q.astype(np.float32)

        t0 = time.perf_counter()
        scores = []
        for entry in self.index:
            score = self._score_pair(des_q, entry['des'])
            scores.append((score, entry))

        scores.sort(key=lambda x: x[0], reverse=True)
        elapsed = (time.perf_counter() - t0) * 1000

        print(f"[INFO] Query selesai dalam {elapsed:.1f} ms")
        results = [{'name': e['name'], 'image': e['image'], 'score': s}
                   for s, e in scores[:top_k]]
        return results

    def print_results(self, results):
        """Cetak hasil query ke konsol."""
        print("\n[Hasil Retrieval]")
        print("-" * 40)
        for i, r in enumerate(results, 1):
            print(f"  [{i}] {r['name']:<30}  Score: {r['score']}")
        print()

    def visualize_results(self, query_image, results, save_path=None):
        """
        Tampilkan query di atas dan top-k hasil di bawah.

        Args:
            query_image: Gambar query
            results:     Output dari query()
            save_path:   Path simpan (opsional)
        """
        n = len(results)
        if n == 0:
            print("[WARN] Tidak ada hasil untuk divisualisasikan.")
            return

        fig = plt.figure(figsize=(3 * (n + 1), 6))

        # Baris atas: gambar query (lebar penuh)
        ax_q = fig.add_subplot(2, n + 1, (1, n + 1))
        ax_q.imshow(cv2.cvtColor(query_image, cv2.COLOR_BGR2RGB))
        ax_q.set_title('QUERY', fontsize=12, fontweight='bold', color='red')
        ax_q.axis('off')

        # Baris bawah: top-k hasil
        for i, r in enumerate(results):
            ax = fig.add_subplot(2, n + 1, n + 2 + i)
            ax.imshow(cv2.cvtColor(r['image'], cv2.COLOR_BGR2RGB))
            ax.set_title(f"#{i+1} {r['name']}\nScore: {r['score']}", fontsize=9)
            ax.axis('off')

        plt.suptitle('Image Retrieval — Top-K Results', fontsize=13, fontweight='bold')
        plt.tight_layout()

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            print(f"[INFO] Visualisasi disimpan: {save_path}")
        plt.show()

    def evaluate(self, query_image, ground_truth_name, top_k=5):
        """
        Evaluasi Precision@k jika label ground truth diketahui.

        Args:
            query_image:       Gambar query
            ground_truth_name: Nama file yang seharusnya jadi hasil teratas
            top_k:             k untuk Precision@k

        Returns:
            dict {'precision@3', 'precision@5', 'rank'}
        """
        results = self.query(query_image, top_k=top_k)
        names = [r['name'] for r in results]

        rank = next((i + 1 for i, n in enumerate(names) if ground_truth_name in n), -1)
        p_at_3 = int(any(ground_truth_name in n for n in names[:3])) / 3
        p_at_5 = int(any(ground_truth_name in n for n in names[:5])) / 5

        print(f"[Evaluasi] Ground truth: {ground_truth_name}")
        print(f"  Rank       : {rank if rank > 0 else 'Tidak ditemukan'}")
        print(f"  Precision@3: {p_at_3:.2f}")
        print(f"  Precision@5: {p_at_5:.2f}")
        return {'precision@3': p_at_3, 'precision@5': p_at_5, 'rank': rank}

    def save_index(self, path='results/retrieval_index.pkl'):
        """Simpan index ke file menggunakan pickle."""
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        # Simpan tanpa objek gambar agar file lebih kecil; gambar dimuat ulang saat dibutuhkan
        save_data = [{'name': e['name'], 'path': e['path'],
                      'des': e['des']} for e in self.index]
        with open(path, 'wb') as f:
            pickle.dump(save_data, f)
        print(f"[INFO] Index disimpan: {path} ({len(self.index)} entri)")

    def load_index(self, path='results/retrieval_index.pkl'):
        """Muat index dari file pickle."""
        if not os.path.exists(path):
            print(f"[ERROR] File index tidak ditemukan: {path}")
            return False
        with open(path, 'rb') as f:
            save_data = pickle.load(f)
        self.index = []
        for entry in save_data:
            img = load_image(entry['path'])
            self.index.append({
                'name': entry['name'],
                'path': entry['path'],
                'image': img,
                'des': entry['des'],
                'kp': [],  # Tidak disimpan; hanya dibutuhkan saat scoring
            })
        print(f"[INFO] Index dimuat: {len(self.index)} entri dari {path}")
        return True


# ─── Demo standalone ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys

    def make_db_image(label, size=(200, 200)):
        """Buat gambar sintetis untuk database."""
        img = np.ones((size[0], size[1], 3), dtype=np.uint8) * 220
        seed = abs(hash(label)) % 9999
        np.random.seed(seed)
        for _ in range(20):
            x, y = np.random.randint(10, size[1]-10), np.random.randint(10, size[0]-10)
            cv2.circle(img, (x, y), np.random.randint(5, 25),
                       tuple(np.random.randint(30, 220, 3).tolist()), -1)
        cv2.putText(img, label, (5, size[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        return img

    if len(sys.argv) >= 3:
        db_folder = sys.argv[1]
        query_path = sys.argv[2]
        ir = ImageRetriever()
        ir.build_index(db_folder)
        query_img = load_image(query_path)
    else:
        print("[INFO] Demo sintetis. Gunakan: python image_retriever.py <db_folder> <query.jpg>")
        # Simpan gambar sintetis ke folder temp
        os.makedirs('data/database', exist_ok=True)
        labels = ['apel', 'buku', 'kursi', 'meja', 'botol', 'tas', 'sepatu', 'lampu']
        for label in labels:
            img = make_db_image(label)
            cv2.imwrite(f'data/database/{label}.jpg', img)

        ir = ImageRetriever()
        ir.build_index('data/database')
        query_img = make_db_image('buku')  # Query mirip dengan 'buku' di database

    results = ir.query(query_img, top_k=5)
    ir.print_results(results)
    ir.visualize_results(query_img, results, save_path='results/retrieval_result.png')
