# cli/commands/new.py
import shutil
import subprocess
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Create a new Dezh project.")
console = Console()

FRAMEWORK_ROOT = Path(__file__).resolve().parents[2]

COPY_ITEMS = [
    "app", "framework", "cli", "tests",
    "pyproject.toml", ".env.example", ".gitignore", "README.md",
]


def _copy_tree(src: Path, dst: Path) -> None:
    ignore = shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".pytest_cache", ".ruff_cache",
        "*.db", "*.log", ".venv", ".git", "storage",
    )
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)


@app.callback(invoke_without_command=True)
def create(
    name: str = typer.Argument(..., help="Project name, e.g. myapp"),
    template: str = typer.Option("default", "--template", "-t",
                                 help="default | minimal | full"),
    with_git: bool = typer.Option(True, "--git/--no-git"),
    install: bool = typer.Option(False, "--install/--no-install"),
) -> None:
    """Create a new Dezh project."""
    target = Path.cwd() / name

    if target.exists():
        console.print(f"[bold red]✗ directory already exists:[/bold red] {target}")
        raise typer.Exit(1)

    console.print(f"[bold cyan]🏰 Creating Dezh project:[/bold cyan] {name} (template={template})")
    target.mkdir(parents=True)

    # ۱. کپی
    for item in COPY_ITEMS:
        src = FRAMEWORK_ROOT / item
        dst = target / item
        if not src.exists():
            console.print(f"  [yellow]⚠ skip (not found):[/yellow] {item}")
            continue
        if src.is_dir():
            _copy_tree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        console.print(f"  [green]✓[/green] {item}")

    # ۲. storage
    (target / "storage" / "db").mkdir(parents=True, exist_ok=True)
    (target / "storage" / "logs").mkdir(parents=True, exist_ok=True)
    (target / "storage" / "uploads").mkdir(parents=True, exist_ok=True)
    console.print("  [green]✓[/green] storage/")

    # ۳. pyproject: نام پروژه
    pp = target / "pyproject.toml"
    if pp.exists():
        text = pp.read_text(encoding="utf-8")
        text = text.replace('name = "dezh"', f'name = "{name}"', 1)
        pp.write_text(text, encoding="utf-8")
        console.print("  [green]✓[/green] pyproject.toml (name updated)")

    # ۴. git init
    if with_git:
        try:
            subprocess.run(["git", "init"], cwd=target, check=True, capture_output=True)
            console.print("  [green]✓[/green] git repository initialized")
        except (FileNotFoundError, subprocess.CalledProcessError):
            console.print("  [yellow]⚠[/yellow] git not available, skipped")

    # ۵. نصب
    if install:
        console.print("\n[cyan]Installing dependencies...[/cyan]")
        try:
            subprocess.run(["py", "-m", "pip", "install", "-e", ".[dev]"], cwd=target, check=True)
            console.print("  [green]✓[/green] dependencies installed")
        except subprocess.CalledProcessError:
            console.print("  [red]✗[/red] install failed")
            raise typer.Exit(1) from None

    # ۶. پیام راهنما
    console.print(f"\n[bold green]✅ Project created:[/bold green] {target}\n")
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  cd {name}")
    if not install:
        console.print('  py -m pip install -e ".[dev]"')   # ← اصلاح شد
    console.print("  Copy-Item .env.example .env")
    console.print("  dezh serve run")