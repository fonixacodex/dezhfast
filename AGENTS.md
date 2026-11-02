# Dezh Framework — Agent Guidelines

This repository contains **Dezh**, a modular FastAPI framework with an Artisan-style CLI. Follow these guidelines when working on this project.

## Project Overview

Dezh provides a structured layer on top of FastAPI with:
- A reusable `framework/` core (DI Container, Lifecycle, BaseModule)
- An Artisan-style CLI (`dezh make`, `dezh migrate`, `dezh new`, etc.)
- Built-in exception handling, request tracing, and rate limiting
- Multi-database support (SQLite, PostgreSQL, MySQL)
- Optional MCP integration (currently commented out)

## Prerequisites

- Python 3.11+ (3.12 strongly recommended; 3.14 has `uvicorn --reload` issues on Windows)
- Git
- Docker (optional)

## Build & Run

```bash
# Install dependencies (with dev tools)
py -m pip install -e ".[dev]"

# Initialize database (auto-created on startup in dev)
# Just run the server:

# Start development server (always use --no-reload on Python 3.14+)
dezh serve run --no-reload