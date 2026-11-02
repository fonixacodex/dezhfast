import importlib
import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Diagnose the project environment.")
console = Console()


def _check(name: str, ok: bool, detail: str = "") -> tuple[str, str, str]:
    status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
    return name, status, detail


@app.callback(invoke_without_command=True)
def run() -> None:
    """Run basic environment checks."""
    rows: list[tuple[str, str, str]] = []

    rows.append(_check("python", sys.version_info >= (3, 11), sys.version.split()[0]))

    for pkg in ("fastapi", "sqlalchemy", "pydantic", "typer", "rich"):
        try:
            importlib.import_module(pkg)
            rows.append(_check(pkg, True, "importable"))
        except Exception as e:  # noqa: BLE001
            rows.append(_check(pkg, False, str(e)))

    # --- MCP (فعلاً کامنت) ---
    # try:
    #     importlib.import_module("mcp")
    #     rows.append(_check("mcp", True, "importable"))
    # except Exception:
    #     rows.append(_check("mcp", False, "not installed (optional)"))
    # -------------------------

    rows.append(_check(".env", Path(".env").exists(), str(Path(".env").resolve())))
    rows.append(_check("pyproject.toml", Path("pyproject.toml").exists()))
    rows.append(_check("uvicorn", shutil.which("uvicorn") is not None))

    table = Table(title="Dezh Doctor", show_lines=False)
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status")
    table.add_column("Detail", style="dim")

    for r in rows:
        table.add_row(*r)

    console.print(table)