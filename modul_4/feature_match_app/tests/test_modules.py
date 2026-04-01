"""
tests/test_modules.py
Unit test sederhana untuk keempat modul utama.

Jalankan dengan:
  python -m pytest tests/ -v
atau:
  python tests/test_modules.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2


def make_image(seed=0, size=(300, 400)):
    """Buat gambar sintetis untuk testing."""
    np.random.seed(seed)
    img = np.zeros((*size, 3), dtype=np.uint8)
    for _ in range(25):
        x, y = np.random.randint(10, size[1]-10), np.random.randint(10, size[0]-10)
        cv2.circle(img, (x, y), np.random.randint(5, 30),
                   tuple(int(c) for c in np.random.randint(80, 255, 3)), -1)
    return img


# ─── Fase 1 ───────────────────────────────────────────────────────────────────
def test_benchmark_returns_results():
    from detector_benchmark import DetectorBenchmark
    bench = DetectorBenchmark(detectors=['SIFT', 'ORB', 'FAST'])
    img = make_image()
    results = bench.compare_all(img)
    assert len(results) == 3, "Harus ada 3 hasil benchmark"
    for r in results:
        assert 'n_keypoints' in r
        assert 'time_ms' in r
        assert r['n_keypoints'] >= 0
    print("[PASS] test_benchmark_returns_results")


def test_benchmark_all_detectors():
    from detector_benchmark import DetectorBenchmark
    bench = DetectorBenchmark()
    img = make_image()
    results = bench.compare_all(img)
    assert len(results) == 7, "Semua 7 detektor harus berhasil"
    print("[PASS] test_benchmark_all_detectors")


# ─── Fase 2 ───────────────────────────────────────────────────────────────────
def test_robust_matcher_sift_flann():
    from robust_matcher import RobustMatcher
    img1 = make_image(seed=0)
    M = cv2.getRotationMatrix2D((200, 150), 10, 1.0)
    img2 = cv2.warpAffine(img1, M, (400, 300))

    rm = RobustMatcher(detector='SIFT', matcher='FLANN')
    kp1, des1 = rm.detect_and_compute(img1)
    kp2, des2 = rm.detect_and_compute(img2)
    matches = rm.match(des1, des2)
    assert isinstance(matches, list), "Match harus berupa list"
    print(f"[PASS] test_robust_matcher_sift_flann ({len(matches)} matches)")


def test_robust_matcher_orb_bf():
    from robust_matcher import RobustMatcher
    img1 = make_image(seed=1)
    img2 = make_image(seed=1)  # Gambar sama → banyak match

    rm = RobustMatcher(detector='ORB', matcher='BF')
    kp1, des1 = rm.detect_and_compute(img1)
    kp2, des2 = rm.detect_and_compute(img2)
    matches = rm.match(des1, des2)
    assert len(matches) > 0, "Gambar identik harus menghasilkan match"
    print(f"[PASS] test_robust_matcher_orb_bf ({len(matches)} matches)")


def test_verify_geometry():
    from robust_matcher import RobustMatcher
    img1 = make_image(seed=2)
    M = cv2.getRotationMatrix2D((200, 150), 5, 1.0)
    img2 = cv2.warpAffine(img1, M, (400, 300))

    rm = RobustMatcher(detector='SIFT', matcher='FLANN')
    kp1, des1 = rm.detect_and_compute(img1)
    kp2, des2 = rm.detect_and_compute(img2)
    matches = rm.match(des1, des2)
    H, mask, n_inliers = rm.verify_geometry(kp1, kp2, matches)
    assert n_inliers >= 0
    print(f"[PASS] test_verify_geometry (inliers={n_inliers})")


# ─── Fase 3 ───────────────────────────────────────────────────────────────────
def test_object_recognizer_add_template():
    from object_recognizer import ObjectRecognizer
    rec = ObjectRecognizer()
    tmpl = make_image(seed=5, size=(200, 200))
    result = rec.add_template('test_obj', tmpl)
    assert result is True, "Harus berhasil menambahkan template"
    assert 'test_obj' in rec.templates
    print("[PASS] test_object_recognizer_add_template")


def test_object_recognizer_recognize():
    from object_recognizer import ObjectRecognizer
    rec = ObjectRecognizer(min_inliers=4)
    tmpl = make_image(seed=10, size=(150, 200))
    rec.add_template('obj_test', tmpl)

    # Scene berisi template + latar
    scene = np.ones((500, 700, 3), dtype=np.uint8) * 150
    scene[50:200, 100:300] = tmpl

    detections = rec.recognize(scene)
    assert isinstance(detections, list)
    print(f"[PASS] test_object_recognizer_recognize ({len(detections)} detections)")


# ─── Fase 4 ───────────────────────────────────────────────────────────────────
def test_image_retriever_build_and_query(tmp_path=None):
    from image_retriever import ImageRetriever

    # Buat folder database sementara
    import tempfile
    tmpdir = tempfile.mkdtemp()
    labels = ['alpha', 'beta', 'gamma', 'delta']
    for i, label in enumerate(labels):
        img = make_image(seed=i * 5, size=(150, 150))
        cv2.imwrite(os.path.join(tmpdir, f'{label}.jpg'), img)

    ir = ImageRetriever()
    n = ir.build_index(tmpdir)
    assert n == 4, f"Harus memuat 4 gambar, tapi {n}"

    query = make_image(seed=0, size=(150, 150))  # mirip 'alpha'
    results = ir.query(query, top_k=3)
    assert len(results) <= 3
    assert all('name' in r and 'score' in r for r in results)
    print(f"[PASS] test_image_retriever_build_and_query ({len(results)} results)")

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_image_retriever_save_load(tmp_path=None):
    from image_retriever import ImageRetriever
    import tempfile, shutil

    tmpdir = tempfile.mkdtemp()
    for i in range(3):
        img = make_image(seed=i * 3, size=(100, 100))
        cv2.imwrite(os.path.join(tmpdir, f'img_{i}.jpg'), img)

    ir = ImageRetriever()
    ir.build_index(tmpdir)

    idx_path = os.path.join(tmpdir, 'test_index.pkl')
    ir.save_index(idx_path)
    assert os.path.exists(idx_path), "File index harus ada"

    ir2 = ImageRetriever()
    success = ir2.load_index(idx_path)
    assert success is True
    assert len(ir2.index) == len(ir.index)
    print("[PASS] test_image_retriever_save_load")

    shutil.rmtree(tmpdir)


# ─── Runner ───────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Menjalankan Unit Tests...")
    print("=" * 50 + "\n")

    tests = [
        test_benchmark_returns_results,
        test_benchmark_all_detectors,
        test_robust_matcher_sift_flann,
        test_robust_matcher_orb_bf,
        test_verify_geometry,
        test_object_recognizer_add_template,
        test_object_recognizer_recognize,
        test_image_retriever_build_and_query,
        test_image_retriever_save_load,
    ]

    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  Hasil: {passed} PASSED, {failed} FAILED")
    print("=" * 50 + "\n")
