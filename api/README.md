# api

Spring Boot + Kotlin backend (Gradle Kotlin DSL).

This is the brain of the app. It receives photos from the Android app, asks the measurement service to analyse them, saves the result in a database, and hands back a share code. The tailor's web page also talks to this service to look up a customer's measurements.

---

## How the pieces fit together

```
Android app  ──POST /scans──▶  api (this service)  ──POST /measure──▶  measure (Python)
                                       │
                                  PostgreSQL DB
                                       │
Tailor web  ──GET /profiles/CODE──▶  api (this service)
```

Before you can run the API you need **two other things running**:
1. A PostgreSQL database (we use Docker to start one with a single command)
2. The Python measurement service (`measure/`)

---

## Prerequisites — install these first

### 1. Java (JDK 17 or newer)

**Check if you already have it:**
```bash
java -version
# Should print something like: java version "19.0.1"
```

**If not installed:**
- Mac: `brew install openjdk@19`
- Windows/Linux: download from https://adoptium.net

> You do **not** need to install Gradle. The `gradlew` script in this folder downloads the right version automatically.

### 2. Docker Desktop

Docker is used to run a PostgreSQL database locally without installing Postgres directly on your machine.

- Download from https://www.docker.com/products/docker-desktop
- Install it, then **open Docker Desktop** and wait until it says "Docker is running" in the menu bar

---

## Step-by-step: run the full API locally

### Step 1 — Start the database

Open a terminal and run this from the **root of the repo** (not inside `api/`):

```bash
docker compose up -d
```

- `-d` means "run in the background"
- This downloads a small Postgres image the first time (~70 MB), then starts it
- The database is now available at `localhost:5433`

When it works you'll see:

![Docker compose up](../docs/screenshots/docker-compose-up.png)

**To stop the database later:**
```bash
docker compose down
```

### Step 2 — Start the Python measurement service

Open a **second terminal** and follow the setup steps in [`measure/README.md`](../measure/README.md). In short:

```bash
cd measure
source .venv/bin/activate
uvicorn main:app --port 8001
```

### Step 3 — Start the API

Open a **third terminal**:

```bash
cd api
./gradlew bootRun
```

You'll know it's ready when you see:
```
Started Application in 2.3 seconds
```

![API started](../docs/screenshots/api-started.png)

---

## How to test it

### Health check
```bash
curl http://localhost:8080/health
# {"status":"ok"}
```

### Submit a scan (requires the Python service running)
```bash
curl -X POST http://localhost:8080/scans \
  -F "frontImage=@/path/to/front.jpg" \
  -F "sideImage=@/path/to/side.jpg" \
  -F "heightCm=175"
```

Expected response:
```json
{
  "shareCode": "PF-AB3K-XY7Q",
  "measurements": {
    "shoulderWidthCm": 42.3,
    "armLengthCm": 58.1,
    "insideLegCm": 77.4,
    "waistCircCm": 74.2,
    "chestCircCm": 91.8
  }
}
```

![Successful scan response](../docs/screenshots/scan-success.png)

### Look up a profile by share code
```bash
curl http://localhost:8080/profiles/PF-AB3K-XY7Q
```

> `GET /profiles/{shareCode}` is implemented in issue #11.

---

## How to stop everything

- API: `Ctrl+C` in the terminal running `./gradlew bootRun`
- Python service: `Ctrl+C` in the terminal running `uvicorn`
- Database: `docker compose down` from the repo root

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status":"ok"}` |
| `POST` | `/scans` | Submit photos + height → get share code + measurements |
| `GET` | `/profiles/{shareCode}` | Retrieve a profile by share code _(issue #11)_ |

---

## What each file does

```
api/
├── gradlew                  # Script to run Gradle (use this to build/run — Mac/Linux)
├── gradlew.bat              # Same, for Windows
├── build.gradle.kts         # Project config: dependencies, Java version, plugins
├── settings.gradle.kts      # Project name
├── docker-compose.yml       # (at repo root) Starts a local PostgreSQL database
└── src/main/kotlin/com/perfectfit/api/
    ├── Application.kt           # Entry point — starts the server
    ├── HealthController.kt      # GET /health
    ├── ScanController.kt        # POST /scans — receives photos, returns share code
    ├── MeasurementClient.kt     # Talks to the Python measurement service over HTTP
    ├── Profile.kt               # Database table definition (one row = one scan)
    ├── ProfileRepository.kt     # Database queries (Spring writes the SQL for you)
    └── ShareCodeGenerator.kt    # Generates PF-XXXX-XXXX codes
```

---

## Key concepts (if you're new to Spring Boot)

- **Spring Boot** — handles the boring parts of a web server: routing requests, parsing JSON, connecting to databases.
- **Kotlin** — the language. Cleaner than Java, runs on the same JVM.
- **Gradle** — the build tool. Compiles the code and manages libraries.
- **JPA / Hibernate** — translates between Kotlin objects and database rows. You write `Profile.kt`, Spring creates the `profile` table automatically.
- **`@RestController`** — marks a class as an HTTP handler. Spring routes requests to the right function.
- **`@PostMapping("/scans")`** — "when someone sends a POST request to /scans, run this function."
- **`RestClient`** — Spring's built-in HTTP client, used to call the Python service.

---

## Useful Gradle commands

```bash
./gradlew bootRun        # Start the server
./gradlew build          # Compile + run tests
./gradlew build -x test  # Compile only, skip tests
./gradlew test           # Run tests only
```
