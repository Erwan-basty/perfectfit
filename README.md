# perfectfit

Body measurement app: customer scans with phone, tailor reads measurements via share code.

## How it works

1. **Customer** opens the Android app, takes two photos (front + side, A-pose), enters their height.
2. The app sends the photos to the API, which calls the Python measurement service.
3. A **share code** (e.g. `PF-AB12-CD34`) is returned along with the measurements.
4. The customer sends the code to their tailor.
5. **Tailor** opens the web page, enters the share code, and reads the measurements — no in-person meeting needed.

## Monorepo structure

| Folder | What lives here |
|--------|----------------|
| `android/` | Kotlin Android app (customer-facing) |
| `api/` | Spring Boot + Kotlin backend |
| `measure/` | Python FastAPI measurement service (MediaPipe) |
| `web/` | Tailor-facing single-page web app |
| `docs/` | Architecture, decisions, and roadmap |

## Docs

- [Architecture](docs/ARCHITECTURE.md)
- [Decisions](docs/DECISIONS.md)
- [Roadmap](docs/ROADMAP.md)

## Development

See each subfolder's `README.md` for local run instructions.
