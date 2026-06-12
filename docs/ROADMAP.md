# Roadmap

## v1 — End-to-end MVP

Goal: a working end-to-end flow. Customer scans on Android → API → Python measurement service → profile stored with share code → tailor opens share code on web page → sees measurements.

| Issue | Title | Status |
|-------|-------|--------|
| #7 | chore: set up monorepo skeleton | 🔄 in progress |
| #8 | chore: bootstrap Python measurement service | ⬜ todo |
| #9 | chore: bootstrap Spring Boot API | ⬜ todo |
| #10 | feat: POST /scans endpoint | ⬜ todo |
| #11 | feat: GET /profiles/{shareCode} endpoint | ⬜ todo |
| #12 | chore: bootstrap Android project | ⬜ todo |
| #13 | feat: camera capture screen | ⬜ todo |
| #14 | feat: two-photo capture flow | ⬜ todo |
| #15 | feat: A-pose silhouette overlay | ⬜ todo |
| #16 | feat: send photos to API, show results | ⬜ todo |
| #17 | feat: tailor web page — look up a profile | ⬜ todo |
| #18 | chore: deploy v1 to staging environment | ⬜ todo |

## v1.1 — First user feedback

Improvements from real user testing. Issues TBD after v1 ships.

## v2 — Better body finding

AI accuracy improvements: better pose models, SMPL 3D body fitting. The measurement engine is swappable by design.

## v3 — Fit-feedback learning

Learn from fit feedback to improve accuracy over time.

## v4 — Premium accuracy

Sub-centimeter accuracy for bespoke tailoring.
