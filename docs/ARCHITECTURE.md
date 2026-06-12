# Architecture

## Overview

perfectfit is a monorepo with four services:

```
┌─────────────────┐        ┌─────────────────┐
│  Android app    │──────▶ │   Spring Boot   │
│  (customer)     │  HTTP  │      API        │
└─────────────────┘        └────────┬────────┘
                                    │ HTTP
                           ┌────────▼────────┐
                           │  Python FastAPI  │
                           │  measure service │
                           └─────────────────┘

┌─────────────────┐        ┌─────────────────┐
│   Web page      │──────▶ │   Spring Boot   │
│   (tailor)      │  HTTP  │      API        │
└─────────────────┘        └─────────────────┘
```

## Services

### `android/` — Android app
- Language: Kotlin
- Min SDK: 26
- Captures two photos (front + side) from the customer
- Sends them to the API with the customer's height
- Displays the share code and measurements

### `api/` — Spring Boot API
- Language: Kotlin, Gradle Kotlin DSL
- Port: 8080
- Orchestrates the scan flow: receives photos, calls the measurement service, persists profiles, issues share codes
- Database: PostgreSQL
- The measurement logic lives entirely in the `measure/` service — the API never embeds it

### `measure/` — Python measurement service
- Language: Python, FastAPI
- Wraps MediaPipe pose estimation
- Single endpoint: `POST /measure`
- Intentionally isolated so the measurement engine can be swapped in v2+ without touching the API

### `web/` — Tailor web page
- Framework TBD (React or Angular)
- Single page: enter share code → see measurements table
- No login, no state

## Data flow — scan

1. Customer captures front + side photo on Android
2. Android POSTs photos + height to `POST /api/scans`
3. API forwards photos + height to `POST /measure`
4. Measurement service returns JSON measurements
5. API generates share code (`PF-XXXX-XXXX`), persists `Profile` in PostgreSQL
6. API returns `{ shareCode, measurements }` to Android
7. Customer shares the code with their tailor

## Data flow — tailor lookup

1. Tailor opens web page, enters share code
2. Web page calls `GET /api/profiles/{shareCode}`
3. API looks up profile, returns measurements
4. Web page renders measurements table

## Key design decisions

See [DECISIONS.md](DECISIONS.md) for the full log.
