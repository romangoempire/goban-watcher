import cv2
import numpy as np
from cv2.typing import MatLike


def percentage_change(
    last_img: MatLike,
    current_img: MatLike,
    threshold: int = 50,
    round_digits: int = 4,
) -> float:
    """Compare two images and calculate the percentage of pixel that changed (0-100%)"""
    diff = cv2.absdiff(last_img, current_img)
    diff_magnitude = np.linalg.norm(diff.astype(np.float32), axis=2)
    mask_above_threshold = diff_magnitude > threshold

    return round(np.mean(mask_above_threshold) * 100, round_digits)
