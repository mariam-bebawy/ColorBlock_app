import cv2
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.cluster import KMeans


def check_brightness(img_bgr, threshold=150):
    """Returns True if the image is bright enough for reliable color extraction."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    brightness = int(np.mean(hsv[:, :, 2]))
    return brightness >= threshold


def get_roi(img_bgr, resize=500, margin=100):
    """
    Resizes image to resize×resize, converts to RGB, returns (full_img, center_roi).
    center_roi is a (2*margin)×(2*margin) crop from the center.
    """
    img = cv2.resize(img_bgr, (resize, resize))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]
    roi = img[h // 2 - margin:h // 2 + margin, w // 2 - margin:w // 2 + margin]
    return img, roi


def get_dominant_color(roi, n_clusters=3):
    """Runs KMeans on the ROI and returns the most common cluster center as RGB array."""
    pixels = roi.reshape(-1, 3)
    clf = KMeans(n_clusters=n_clusters, n_init=10)
    labels = clf.fit_predict(pixels)
    counts = dict(sorted(Counter(labels).items()))
    centers = clf.cluster_centers_
    ordered = [centers[i] for i in counts.keys()]
    return ordered[0]


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
