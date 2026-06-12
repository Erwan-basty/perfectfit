# measure

Python FastAPI service that wraps the body measurement logic.

Accepts two photos (front + side, A-pose) and a height in cm. Uses MediaPipe pose landmarks and the Ramanujan ellipse approximation to estimate body measurements. Returns JSON.

## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app — HTTP endpoint, request validation, error handling |
| `measure_core.py` | Pure measurement logic (no HTTP) — easy to test independently |
| `requirements.txt` | Pinned dependencies |

## Endpoint

```
POST /measure
Content-Type: multipart/form-data

Fields:
  front_image  (file)   Front-view photo, A-pose, JPEG or PNG
  side_image   (file)   Side-view photo, A-pose, JPEG or PNG
  height_cm    (float)  Person's real height in centimetres

Response 200:
{
  "shoulder_width_cm": 42.3,
  "arm_length_cm":     58.1,
  "inside_leg_cm":     77.4,
  "waist_circ_cm":     74.2,
  "chest_circ_cm":     91.8
}
```

## Accuracy (v1)

| Measurement | Typical error |
|-------------|--------------|
| Shoulder width, arm length, inside leg | ±2–3 cm |
| Waist circumference, chest circumference | ±2–4 cm |

Circumferences are estimated with the Ramanujan ellipse approximation (front width + side depth). Real bodies aren't perfect ellipses — this is a known v1 limitation.

## Local setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the service
uvicorn main:app --reload --port 8001
```

The service runs at http://localhost:8001.
Interactive API docs: http://localhost:8001/docs

## Test with curl

```bash
curl -X POST http://localhost:8001/measure \
  -F "front_image=@/path/to/front.jpg" \
  -F "side_image=@/path/to/side.jpg" \
  -F "height_cm=175"
```
