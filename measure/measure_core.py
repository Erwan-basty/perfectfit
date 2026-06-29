"""
measure_core.py
---------------
Pure measurement logic extracted from the validated measure_v2 script.
No FastAPI, no file I/O — takes numpy images and height, returns a dict.

The algorithm is intentionally unchanged from the validated script:
  - MediaPipe pose landmarks (model_complexity=2) + segmentation mask
  - cm-per-pixel ruler derived from the person's known height
  - Ramanujan ellipse approximation for circumferences
"""

import math
import cv2
import mediapipe as mp
import numpy as np


# ------------------------------------------------------------------ #
#  Internal helpers (same logic as the original script)
# ------------------------------------------------------------------ #

def _analyze_image(bgr_image: np.ndarray):
    """Run MediaPipe on a BGR numpy image.
    Returns (landmarks, silhouette_mask, img_h, img_w).
    Raises ValueError if no body is detected.
    """
    h, w = bgr_image.shape[:2]
    rgb = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
    ) as pose:
        result = pose.process(rgb)

    if not result.pose_landmarks:
        raise ValueError(
            "No body detected. Check that the person is fully in frame, "
            "background is plain, and lighting is good."
        )

    silhouette = (result.segmentation_mask > 0.5).astype(np.uint8)
    return result.pose_landmarks.landmark, silhouette, h, w


def _cm_per_pixel(landmarks, img_h: int, height_cm: float) -> float:
    """Derive the cm-per-pixel scale factor from the known real height."""
    mp_lm = mp.solutions.pose.PoseLandmark
    ys = [lm.y for lm in landmarks]
    top_y = min(ys) * img_h
    ankle_y = max(
        landmarks[mp_lm.LEFT_ANKLE.value].y,
        landmarks[mp_lm.RIGHT_ANKLE.value].y,
    ) * img_h
    height_px = ankle_y - top_y
    if height_px <= 0:
        raise ValueError("Could not measure pixel height — check photo framing.")
    return height_cm / height_px


def _body_width_px(silhouette: np.ndarray, y_level: float) -> float:
    """Width of the body silhouette (in pixels) at a given y coordinate."""
    row = silhouette[int(y_level), :]
    body_pixels = np.where(row > 0)[0]
    if len(body_pixels) < 2:
        return 0.0
    return float(body_pixels[-1] - body_pixels[0])


def _ellipse_circumference(width_cm: float, depth_cm: float) -> float:
    """Ramanujan approximation of an ellipse perimeter.
    width  = front-view body width at this level
    depth  = side-view body width at this level
    """
    a = width_cm / 2.0
    b = depth_cm / 2.0
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))


# ------------------------------------------------------------------ #
#  Public API
# ------------------------------------------------------------------ #

def measure(
    front_bgr: np.ndarray,
    side_bgr: np.ndarray,
    height_cm: float,
) -> dict:
    """Compute body measurements from two photos and a known height.

    Args:
        front_bgr:  Front photo as a BGR numpy array (from cv2.imdecode).
        side_bgr:   Side photo as a BGR numpy array.
        height_cm:  Real height of the person in centimetres.

    Returns:
        Dict with measurement names as keys and cm values as floats.
        Circumference keys end in '_circ_cm'; linear keys end in '_cm'.
    """
    mp_lm = mp.solutions.pose.PoseLandmark

    f_lm, f_sil, f_h, f_w = _analyze_image(front_bgr)
    s_lm, s_sil, s_h, s_w = _analyze_image(side_bgr)

    f_cmpp = _cm_per_pixel(f_lm, f_h, height_cm)
    s_cmpp = _cm_per_pixel(s_lm, s_h, height_cm)

    results = {}

    # --- Linear measurements (front photo only) ---
    lsh = f_lm[mp_lm.LEFT_SHOULDER.value]
    rsh = f_lm[mp_lm.RIGHT_SHOULDER.value]
    shoulder_px = abs(lsh.x - rsh.x) * f_w
    results["shoulder_width_cm"] = round(shoulder_px * f_cmpp, 1)

    lwr = f_lm[mp_lm.LEFT_WRIST.value]
    arm_px = math.hypot((lsh.x - lwr.x) * f_w, (lsh.y - lwr.y) * f_h)
    results["arm_length_cm"] = round(arm_px * f_cmpp, 1)

    lhip = f_lm[mp_lm.LEFT_HIP.value]
    lank = f_lm[mp_lm.LEFT_ANKLE.value]
    leg_px = math.hypot((lhip.x - lank.x) * f_w, (lhip.y - lank.y) * f_h)
    results["inside_leg_cm"] = round(leg_px * f_cmpp, 1)

    # --- Circumferences (front width + side depth → ellipse) ---
    def _level(lm_a, lm_b, img_h):
        return (lm_a.y + lm_b.y) / 2.0 * img_h

    # Waist
    waist_y_f = _level(f_lm[mp_lm.LEFT_HIP.value], f_lm[mp_lm.RIGHT_HIP.value], f_h)
    waist_y_s = _level(s_lm[mp_lm.LEFT_HIP.value], s_lm[mp_lm.RIGHT_HIP.value], s_h)
    waist_w = _body_width_px(f_sil, waist_y_f) * f_cmpp
    waist_d = _body_width_px(s_sil, waist_y_s) * s_cmpp
    if waist_w and waist_d:
        results["waist_circ_cm"] = round(_ellipse_circumference(waist_w, waist_d), 1)

    # Chest
    chest_y_f = _level(f_lm[mp_lm.LEFT_SHOULDER.value], f_lm[mp_lm.LEFT_HIP.value], f_h)
    chest_y_s = _level(s_lm[mp_lm.LEFT_SHOULDER.value], s_lm[mp_lm.LEFT_HIP.value], s_h)
    chest_w = _body_width_px(f_sil, chest_y_f) * f_cmpp
    chest_d = _body_width_px(s_sil, chest_y_s) * s_cmpp
    if chest_w and chest_d:
        results["chest_circ_cm"] = round(_ellipse_circumference(chest_w, chest_d), 1)

    return results
