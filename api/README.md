# api

Spring Boot + Kotlin backend (Gradle Kotlin DSL).

Accepts scan requests from the Android app, calls the measurement service, stores profiles, and serves them by share code.

## Endpoints (planned)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/scans` | Submit photos, get share code + measurements |
| `GET` | `/profiles/{shareCode}` | Retrieve a profile by share code |

## Status

Not yet scaffolded — see issue [#9](https://github.com/Erwan-basty/perfectfit/issues/9).
