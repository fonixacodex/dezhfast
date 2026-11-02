# 🏰 Dezh

A modular FastAPI framework with an Artisan-style CLI, built-in auth, exception handling, request tracing, and optional MCP support.

## Features

- **Modular architecture** — `app/` for your code, `framework/` for the reusable core, `cli/` for tooling
- **Artisan-style CLI** — `dezh make module posts`, `dezh migrate up`, `dezh route list`, `dezh new myapp`
- **Structured exceptions** — 12 domain exception classes with a unified JSON error format
- **Request ID + JSON logging** — every request gets an `X-Request-ID`, logs are parseable in production
- **Rate limiting** — built-in with `slowapi`, applied to auth endpoints by default
- **Multi-database** — SQLite, PostgreSQL, MySQL via `DB_CONNECTION`
- **Optional MCP** — expose tools to LLMs via `pip install -e ".[mcp]"`

## Requirements

- Python 3.11+ (3.12 recommended)
- Redis (optional, for background jobs via ARQ)

## Installation

```bash
# Create a new project
pip install dezh
dezh new myapp
cd myapp

# Or install into an existing project
pip install -e ".[dev]"