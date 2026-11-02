# cli/commands/tinker.py
import asyncio

import typer
from rich.console import Console

app = typer.Typer(help="Interactive REPL for the project.")
console = Console()


@app.callback(invoke_without_command=True)
def run() -> None:
    """Start an interactive Python shell with app context loaded."""
    try:
        import IPython
    except ImportError:
        console.print(
            "[bold red]✗ IPython not installed.[/bold red]\n"
            "Install it: [cyan]py -m pip install ipython[/cyan]"
        )
        raise typer.Exit(1) from None

    from app.core.config import settings
    from app.main import app as fastapi_app

    console.print("[bold cyan]🏰 Dezh Tinker[/bold cyan]")
    console.print("[dim]Available: app, settings[/dim]\n")

    IPython.start_ipython(argv=[], user_ns={
        "app": fastapi_app,
        "settings": settings,
        "asyncio": asyncio,
    })