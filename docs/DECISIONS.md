# Decisions

A log of key technical and product decisions, in chronological order.

---

## 2026-06 — Initial architecture

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Android only for v1, no iOS | Solo developer, faster to ship one platform well |
| 2 | Measurement logic lives in an isolated Python FastAPI service | Makes the engine swappable in v2+ without touching the API or app |
| 3 | API talks to the measurement service over HTTP only | Enforces the service boundary; measurement logic never embedded in the API |
| 4 | v1 targets ±2–4 cm accuracy; no tape-measure calibration step | Calibration contradicts the product promise ("no tape measure needed") |
| 5 | Share code format: `PF-XXXX-XXXX` | Short enough to type or dictate; human-readable prefix identifies the app |
| 6 | PostgreSQL for profile storage | Reliable, well-supported in Spring Boot; no exotic requirements in v1 |
| 7 | Monorepo with four subfolders (`android/`, `api/`, `measure/`, `web/`) | All services in one place; easier for a solo developer to navigate |
