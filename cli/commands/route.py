# cli/commands/route.py
import typer
from rich.console import Console
from rich.table import Table

from framework.routing import iter_routes

app = typer.Typer(help="Inspect application routes.")
console = Console()


@app.command("list")
def route_list() -> None:
    """List all registered routes (like `php artisan route:list`)."""
    from app.main import app as fastapi_app

    table = Table(title="Dezh Routes", show_lines=False)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Path", style="green")
    table.add_column("Name", style="dim")
    table.add_column("Tags", style="magenta")

    rows = 0
    for path, route in iter_routes(fastapi_app.routes):
        methods = getattr(route, "methods", None) or {"-"}
        table.add_row(
            ",".join(sorted(methods)),
            path,
            getattr(route, "name", "") or "",
            ",".join(getattr(route, "tags", []) or []),
        )
        rows += 1

    console.print(table)
    console.print(f"\n[dim]Total: {rows} route(s)[/dim]")