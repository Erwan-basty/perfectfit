# measure

Python FastAPI service that wraps the body measurement logic.

Accepts two photos (front + side) and a height in cm. Uses MediaPipe pose landmarks and the Ramanujan ellipse approximation to estimate body measurements. Returns JSON.

## Endpoint (planned)

```
POST /measure
  Content-Type: multipart/form-data
  Fields: front_image (file), side_image (file), height_cm (float)

Response: { "waist_cm": ..., "chest_cm": ..., "hips_cm": ..., ... }
```

## Status

Not yet scaffolded — see issue [#8](https://github.com/Erwan-basty/perfectfit/issues/8).
