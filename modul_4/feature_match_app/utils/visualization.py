"""
utils/visualization.py
Fungsi-fungsi bantu untuk visualisasi hasil deteksi fitur dan pencocokan.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os


def draw_keypoints(image, keypoints, color=(0, 255, 0)):
    """
    Gambar keypoint pada gambar.

    Args:
        image: Gambar input (BGR atau grayscale)
        keypoints: List keypoint OpenCV
        color: Warna keypoint (B, G, R)

    Returns:
        Gambar dengan keypoint tergambar
    """
    img_color = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
    return cv2.drawKeypoints(img_color, keypoints, None, color=color,
                             flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)


def show_side_by_side(images, titles, save_path=None, figsize=(16, 5)):
    """
    Tampilkan beberapa gambar secara berdampingan.

    Args:
        images: List gambar (BGR atau grayscale)
        titles: List judul untuk setiap gambar
        save_path: Path untuk menyimpan gambar (opsional)
        figsize: Ukuran figure matplotlib
    """
    n = len(images)
    fig, axes = plt.subplots(1, n, figsize=figsize)
    if n == 1:
        axes = [axes]

    for ax, img, title in zip(axes, images, titles):
        # Konversi BGR ke RGB untuk matplotlib
        if len(img.shape) == 3 and img.shape[2] == 3:
            display = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            display = img
        ax.imshow(display, cmap='gray' if len(img.shape) == 2 else None)
        ax.set_title(title, fontsize=10)
        ax.axis('off')

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"[INFO] Gambar disimpan: {save_path}")
    plt.show()


def plot_bar_chart(data_dict, xlabel, ylabel, title, save_path=None):
    """
    Buat bar chart dari dictionary data.

    Args:
        data_dict: Dict {label: nilai}
        xlabel, ylabel, title: Label sumbu dan judul
        save_path: Path untuk menyimpan (opsional)
    """
    labels = list(data_dict.keys())
    values = list(data_dict.values())

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color='steelblue', edgecolor='navy', alpha=0.8)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    # Tambahkan label nilai di atas bar
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01 * max(values),
                f'{val:.1f}', ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"[INFO] Chart disimpan: {save_path}")
    plt.show()
