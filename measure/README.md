# measure

Python FastAPI service that wraps the body measurement logic.

Accepts two photos (front + side, A-pose) and a height in cm. Uses MediaPipe pose landmarks and the Ramanujan ellipse approximation to estimate body measurements. Returns JSON.

---

## Prerequisites — install these first

### Python 3.10 or 3.11

MediaPipe does not yet support Python 3.12+, so you need 3.10 or 3.11 specifically.

**Check what you have:**
```bash
python3 --version
# Should print: Python 3.10.x or Python 3.11.x
```

**If you don't have the right version:**
- Mac: `brew install python@3.11`
- Windows/Linux: download from https://www.python.org/downloads/release/python-3119/

---

## Step-by-step: run the service locally

### Step 1 — Open a terminal and go to the measure folder

```bash
cd ~/perfectfit/measure
```

### Step 2 — Create a virtual environment

A virtual environment is an isolated box for Python packages. It keeps the dependencies for this project separate from everything else on your computer.

```bash
python3.11 -m venv .venv
```

This creates a hidden folder called `.venv` inside `measure/`. You only do this **once**.

### Step 3 — Activate the virtual environment

**Mac / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You'll know it worked because your terminal prompt will change to show `(.venv)` at the start, like this:
```
(.venv) yourmac:measure yourname$
```

> Every time you open a new terminal to work on this service, you need to run the `activate` command again. The virtual environment is only active for the current terminal session.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

This downloads all the required libraries (MediaPipe, FastAPI, OpenCV, etc.) into the `.venv` folder. The first time takes a few minutes — MediaPipe is large (~100 MB).

### Step 5 — Start the service

```bash
uvicorn main:app --reload --port 8001
```

You'll see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The service is now running at http://localhost:8001.

`--reload` means the server automatically restarts when you edit the code — useful during development.

### Step 6 — Verify it's working

Open a **new terminal tab** (keep the service running in the first one) and run:

```bash
curl http://localhost:8001/health
# {"status":"ok"}
```

Or just open http://localhost:8001/health in your browser.

You can also see the interactive API docs at http://localhost:8001/docs — this lets you test the `/measure` endpoint directly in your browser.

---

## How to stop the service

Press `Ctrl+C` in the terminal where `uvicorn` is running.

---

## Next time you want to run it

You don't need to repeat Steps 1–4. Just do:

```bash
cd ~/perfectfit/measure
source .venv/bin/activate      # Windows: .venv\Scripts\activate
uvicorn main:app --reload --port 8001
```

---

## Test with curl (requires two photos)

```bash
curl -X POST http://localhost:8001/measure \
  -F "front_image=@/path/to/front.jpg" \
  -F "side_image=@/path/to/side.jpg" \
  -F "height_cm=175"
```

Replace `/path/to/front.jpg` and `/path/to/side.jpg` with actual photo paths. The person should be in A-pose (arms slightly out), plain background, full body visible.

Expected response:
```json
{
  "shoulder_width_cm": 42.3,
  "arm_length_cm": 58.1,
  "inside_leg_cm": 77.4,
  "waist_circ_cm": 74.2,
  "chest_circ_cm": 91.8
}
```

---

## Endpoint

```
POST /measure
Content-Type: multipart/form-data

Fields:
  front_image  (file)   Front-view photo, A-pose, JPEG or PNG
  side_image   (file)   Side-view photo, A-pose, JPEG or PNG
  height_cm    (float)  Person's real height in centimetres

GET /health
  Returns: {"status": "ok"}
```

---

## Accuracy (v1)

| Measurement | Typical error |
|-------------|--------------|
| Shoulder width, arm length, inside leg | ±2–3 cm |
| Waist circumference, chest circumference | ±2–4 cm |

Circumferences are estimated with the Ramanujan ellipse approximation (front width + side depth). Real bodies aren't perfect ellipses — this is a known v1 limitation.

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app — HTTP endpoint, request validation, error handling |
| `measure_core.py` | Pure measurement logic (no HTTP) — easy to test independently |
| `requirements.txt` | Pinned dependencies |
| `.venv/` | Your local virtual environment (created by you, not committed to git) |
