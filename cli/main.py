# cli/main.py
import typer
from rich.console import Console
from rich.table import Table

from cli.commands import doctor, make, mcp, migrate, new, route, serve, tinker

app = typer.Typer(
    name="dezh",
    help="🏰 Dezh Framework CLI — The Artisan for your FastAPI fortress.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)

# --- command groups ---
app.add_typer(make.app,    name="make",    help="Scaffold models, routers, services, etc.")
app.add_typer(migrate.app, name="migrate", help="Database migrations.")
app.add_typer(route.app,   name="route",   help="Inspect application routes.")
app.add_typer(serve.app,   name="serve",   help="Start the development server.")
app.add_typer(mcp.app,     name="mcp",     help="MCP server helpers.")
app.add_typer(doctor.app,  name="doctor",  help="Diagnose the project.")
app.add_typer(tinker.app,  name="tinker",  help="Interactive REPL.")

app.add_typer(new.app, name="new", help="Create a new Dezh project.")

@app.command()
def info() -> None:
    """Show framework and environment info."""
    console = Console()
    table = Table(title="Dezh Framework", show_lines=False)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_row("Name", "Dezh")
    table.add_row("Stack", "FastAPI + SQLAlchemy + MCP")
    table.add_row("Python", "3.12+")
    table.add_row("Docs", "https://github.com/fonixacodex/dezhfast")
    console.print(table)


@app.command()
def version() -> None:
    """Print Dezh CLI version."""
    typer.echo("Dezh CLI 0.1.0")


if __name__ == "__main__":
    app()