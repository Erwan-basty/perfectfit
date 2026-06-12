"""
main.py
-------
FastAPI entry point for the perfectfit measurement service.

Single endpoint: POST /measure
  - Accepts two photos (front + side) as multipart file uploads
  - Accepts height_cm as a form field
  - Returns JSON with body measurements
"""

import numpy as np
import cv2
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from measure_core import measure

app = FastAPI(
    title="perfectfit measurement service",
    description="Estimates body measurements from two photos using MediaPipe pose landmarks.",
    version="1.0.0",
)


async def _read_image(upload: UploadFile) -> np.ndarray:
    """Read an uploaded file into a BGR numpy array."""
    data = await upload.read()
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(
            status_code=400,
            detail=f"Could not decode image '{upload.filename}'. "
                   "Send a valid JPEG or PNG.",
        )
    return img


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/measure")
async def measure_endpoint(
    front_image: UploadFile = File(..., description="Front-view photo (A-pose)"),
    side_image: UploadFile = File(..., description="Side-view photo (A-pose)"),
    height_cm: float = Form(..., description="Person's real height in centimetres"),
):
    """Estimate body measurements from a front and side photo.

    Returns a JSON object with measurements in centimetres:
    - shoulder_width_cm
    - arm_length_cm
    - inside_leg_cm
    - waist_circ_cm
    - chest_circ_cm

    Accuracy note: linear measurements (shoulder, arm, leg) are typically
    within ±3 cm. Circumferences (waist, chest) are typically within ±2–4 cm.
    """
    if height_cm <= 0 or height_cm > 300:
        raise HTTPException(status_code=400, detail="height_cm must be between 1 and 300.")

    front_bgr = await _read_image(front_image)
    side_bgr = await _read_image(side_image)

    try:
        measurements = measure(front_bgr, side_bgr, height_cm)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return JSONResponse(content=measurements)
