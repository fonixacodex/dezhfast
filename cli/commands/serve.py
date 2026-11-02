import typer
import uvicorn
from rich.console import Console

app = typer.Typer(help="Development server.")
console = Console()


@app.command()
def run(
    host: str = typer.Option("127.0.0.1", "--host", "-h"),
    port: int = typer.Option(8000, "--port", "-p"),
    reload: bool = typer.Option(True, "--reload/--no-reload"),
    workers: int = typer.Option(1, "--workers", "-w"),
) -> None:
    """Start the FastAPI development server."""
    console.print(
        f"[bold cyan]🏰 Dezh[/bold cyan] → "
        f"[green]http://{host}:{port}[/green] (reload={reload}, workers={workers})"
    )
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
    )
