# api

Spring Boot + Kotlin backend (Gradle Kotlin DSL).

This is the brain of the app. It receives photos from the Android app, asks the measurement service to analyse them, saves the result in a database, and hands back a share code. The tailor's web page also talks to this service to look up a customer's measurements.

---

## Prerequisites — install these first

### 1. Java (JDK 17 or newer)

The API is written in Kotlin, which runs on the Java Virtual Machine. You need the JDK (Java Development Kit) installed, not just the JRE.

**Check if you already have it:**
```bash
java -version
```
If it prints a version number (e.g. `java version "19.0.1"`), you're good.

**If not installed:**
- Mac: `brew install openjdk@19`
- Windows/Linux: download from https://adoptium.net

> You do **not** need to install Gradle separately. This project includes a wrapper script (`gradlew`) that downloads the right version automatically the first time you run it.

---

## How to run the API locally

```bash
# 1. Open a terminal and go to the api folder
cd ~/perfectfit/api

# 2. Start the server
./gradlew bootRun
```

On Windows, use `gradlew.bat bootRun` instead.

The first run will take a minute or two — Gradle is downloading dependencies. Subsequent runs are much faster.

You'll know it's ready when you see a line like:
```
Started Application in 2.3 seconds
```

---

## How to test it

Open a **new terminal tab** (keep the server running in the first one) and run:

```bash
curl http://localhost:8080/health
```

You should see:
```json
{"status":"ok"}
```

You can also open http://localhost:8080/health in your browser — it will show the same thing.

> **Important:** the root URL http://localhost:8080 returns a 404 — that's normal. Only the paths listed in the endpoints table below are defined.

---

## How to stop the server

Press `Ctrl+C` in the terminal where `./gradlew bootRun` is running.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status":"ok"}` |
| `POST` | `/scans` | Submit photos + height, get share code + measurements _(coming in issue #10)_ |
| `GET` | `/profiles/{shareCode}` | Retrieve a profile by share code _(coming in issue #11)_ |

---

## What each file does

```
api/
├── gradlew                  # Script that runs Gradle (use this to build/run)
├── gradlew.bat              # Same, for Windows
├── build.gradle.kts         # Project config: dependencies, Java version, plugins
├── settings.gradle.kts      # Project name
├── gradle/wrapper/
│   └── gradle-wrapper.properties  # Which Gradle version to download
└── src/
    └── main/
        ├── kotlin/com/perfectfit/api/
        │   ├── Application.kt       # Entry point — starts the Spring Boot server
        │   └── HealthController.kt  # Handles GET /health
        └── resources/
            └── application.yml      # Config: port number, database settings, etc.
```

### Key concepts (if you're new to Spring Boot)

- **Spring Boot** is a framework that handles the boring parts of building a web server (routing HTTP requests, serialising JSON, connecting to databases) so you can focus on the business logic.
- **Kotlin** is the language. It runs on the JVM just like Java, but has a cleaner syntax.
- **Gradle** is the build tool — it compiles the code, manages dependencies, and packages the app.
- **`@RestController`** — a Spring annotation that marks a class as an HTTP handler. Spring automatically routes incoming requests to the right function.
- **`@GetMapping("/health")`** — tells Spring: "when someone sends a GET request to /health, run this function."

---

## Useful Gradle commands

```bash
./gradlew bootRun        # Start the server (for development)
./gradlew build          # Compile + run tests
./gradlew build -x test  # Compile only, skip tests
./gradlew test           # Run tests only
```
