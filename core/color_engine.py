import cv2
import numpy as np
import pandas as pd


def check_brightness(img_bgr, threshold=150):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    brightness = int(np.mean(hsv[:, :, 2]))
    return brightness >= threshold


def get_roi(img_bgr, resize=500, margin=100):
    img = cv2.resize(img_bgr, (resize, resize))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]
    roi = img[h // 2 - margin:h // 2 + margin, w // 2 - margin:w // 2 + margin]
    return img, roi


def _kmeans_numpy(pixels, n_clusters=3, max_iter=20, seed=42):
    """Minimal k-means on (N, 3) float32 array; returns (labels, centers)."""
    rng = np.random.default_rng(seed)
    centers = pixels[rng.choice(len(pixels), n_clusters, replace=False)].astype(np.float32)
    labels = np.zeros(len(pixels), dtype=np.int32)
    for _ in range(max_iter):
        dists = np.sum((pixels[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(dists, axis=1).astype(np.int32)
        new_centers = np.array([
            pixels[new_labels == i].mean(axis=0) if (new_labels == i).any() else centers[i]
            for i in range(n_clusters)
        ], dtype=np.float32)
        if np.array_equal(new_labels, labels) or np.allclose(centers, new_centers):
            labels = new_labels
            centers = new_centers
            break
        labels, centers = new_labels, new_centers
    return labels, centers


def get_dominant_color(roi, n_clusters=3):
    pixels = roi.reshape(-1, 3).astype(np.float32)
    labels, centers = _kmeans_numpy(pixels, n_clusters=n_clusters)
    counts = np.bincount(labels, minlength=n_clusters)
    return centers[np.argmax(counts)]


def rgb_to_hex(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))


def load_colors_csv(path):
    return pd.read_csv(path)


def recognize_color(csv_df, R, G, B):
    """Returns the name of the closest color in the CSV database (Manhattan distance)."""
    best, name = 10000, ""
    for _, row in csv_df.iterrows():
        d = abs(R - int(row["R"])) + abs(G - int(row["G"])) + abs(B - int(row["B"]))
        if d <= best:
            best, name = d, row["color_name"]
    return name
