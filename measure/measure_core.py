"""
measure_core.py
---------------
Pure measurement logic using the MediaPipe Tasks API (mediapipe 0.10+).
Takes numpy images and height, returns a dict of measurements.

The algorithm is unchanged from the validated script:
  - MediaPipe PoseLandmarker (heavy model) + segmentation mask
  - cm-per-pixel ruler derived from the person's known height
  - Ramanujan ellipse approximation for circumferences
"""

import math
import os
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# BlazePose landmark indices (same topology as the old solutions API)
_NOSE          = 0
_LEFT_SHOULDER = 11
_RIGHT_SHOULDER = 12
_LEFT_WRIST    = 15
_RIGHT_WRIST   = 16
_LEFT_HIP      = 23
_RIGHT_HIP     = 24
_LEFT_ANKLE    = 27
_RIGHT_ANKLE   = 28

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "pose_landmarker.task")


def _make_landmarker():
    base_options = mp_python.BaseOptions(model_asset_path=_MODEL_PATH)
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        output_segmentation_masks=True,
        num_poses=1,
    )
    return mp_vision.PoseLandmarker.create_from_options(options)


def _analyze_image(bgr_image: np.ndarray):
    """Run MediaPipe PoseLandmarker on a BGR numpy image.
    Returns (landmarks, silhouette_mask, img_h, img_w).
    Raises ValueError if no body is detected.
    """
    h, w = bgr_image.shape[:2]
    rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    with _make_landmarker() as landmarker:
        result = landmarker.detect(mp_image)

    if not result.pose_landmarks:
        raise ValueError(
            "No body detected. Check that the person is fully in frame, "
            "background is plain, and lighting is good."
        )

    landmarks = result.pose_landmarks[0]  # list of NormalizedLandmark

    if not result.segmentation_masks:
        raise ValueError("Segmentation mask not available.")

    mask_array = result.segmentation_masks[0].numpy_view()
    silhouette = (mask_array > 0.5).astype(np.uint8)

    return landmarks, silhouette, h, w


def _cm_per_pixel(landmarks, img_h: int, height_cm: float) -> float:
    ys = [lm.y for lm in landmarks]
    top_y = min(ys) * img_h
    ankle_y = max(
        landmarks[_LEFT_ANKLE].y,
        landmarks[_RIGHT_ANKLE].y,
    ) * img_h
    height_px = ankle_y - top_y
    if height_px <= 0:
        raise ValueError("Could not measure pixel height — check photo framing.")
    return height_cm / height_px


def _body_width_px(silhouette: np.ndarray, y_level: float) -> float:
    row = silhouette[int(y_level), :]
    body_pixels = np.where(row > 0)[0]
    if len(body_pixels) < 2:
        return 0.0
    return float(body_pixels[-1] - body_pixels[0])


def _ellipse_circumference(width_cm: float, depth_cm: float) -> float:
    a = width_cm / 2.0
    b = depth_cm / 2.0
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


def measure(front_bgr: np.ndarray, side_bgr: np.ndarray, height_cm: float) -> dict:
    """Compute body measurements from two photos and a known height."""
    f_lm, f_sil, f_h, f_w = _analyze_image(front_bgr)
    s_lm, s_sil, s_h, s_w = _analyze_image(side_bgr)

    f_cmpp = _cm_per_pixel(f_lm, f_h, height_cm)
    s_cmpp = _cm_per_pixel(s_lm, s_h, height_cm)

    results = {}

    # Linear measurements (front photo)
    lsh = f_lm[_LEFT_SHOULDER]
    rsh = f_lm[_RIGHT_SHOULDER]
    shoulder_px = abs(lsh.x - rsh.x) * f_w
    results["shoulder_width_cm"] = round(shoulder_px * f_cmpp, 1)

    lwr = f_lm[_LEFT_WRIST]
    arm_px = math.hypot((lsh.x - lwr.x) * f_w, (lsh.y - lwr.y) * f_h)
    results["arm_length_cm"] = round(arm_px * f_cmpp, 1)

    lhip = f_lm[_LEFT_HIP]
    lank = f_lm[_LEFT_ANKLE]
    leg_px = math.hypot((lhip.x - lank.x) * f_w, (lhip.y - lank.y) * f_h)
    results["inside_leg_cm"] = round(leg_px * f_cmpp, 1)

    # Circumferences (front width + side depth → ellipse)
    def _level(lm_a, lm_b, img_h):
        return (lm_a.y + lm_b.y) / 2.0 * img_h

    waist_y_f = _level(f_lm[_LEFT_HIP], f_lm[_RIGHT_HIP], f_h)
    waist_y_s = _level(s_lm[_LEFT_HIP], s_lm[_RIGHT_HIP], s_h)
    waist_w = _body_width_px(f_sil, waist_y_f) * f_cmpp
    waist_d = _body_width_px(s_sil, waist_y_s) * s_cmpp
    if waist_w and waist_d:
        results["waist_circ_cm"] = round(_ellipse_circumference(waist_w, waist_d), 1)

    chest_y_f = _level(f_lm[_LEFT_SHOULDER], f_lm[_LEFT_HIP], f_h)
    chest_y_s = _level(s_lm[_LEFT_SHOULDER], s_lm[_LEFT_HIP], s_h)
    chest_w = _body_width_px(f_sil, chest_y_f) * f_cmpp
    chest_d = _body_width_px(s_sil, chest_y_s) * s_cmpp
    if chest_w and chest_d:
        results["chest_circ_cm"] = round(_ellipse_circumference(chest_w, chest_d), 1)

    return results
