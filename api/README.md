# api

Spring Boot + Kotlin backend (Gradle Kotlin DSL).

Accepts scan requests from the Android app, calls the measurement service, stores profiles, and serves them by share code.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status":"ok"}` |
| `POST` | `/scans` | Submit photos + height, get share code + measurements _(issue #10)_ |
| `GET` | `/profiles/{shareCode}` | Retrieve a profile by share code _(issue #11)_ |

## Local setup

**Prerequisites:** Java 17+ installed.

```bash
cd api
./gradlew bootRun
```

The API runs at http://localhost:8080.

```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

## Project structure

```
api/
├── build.gradle.kts                  # Gradle build config
├── settings.gradle.kts
└── src/main/kotlin/com/perfectfit/api/
    ├── Application.kt                # Spring Boot entry point
    └── HealthController.kt           # GET /health
```
