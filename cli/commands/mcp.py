import typer
from rich.console import Console

app = typer.Typer(help="MCP server helpers.")
console = Console()


@app.command()
def inspect() -> None:
    """Open MCP Inspector against app/modules/mcp/server.py."""
    console.print("[cyan]→ launching MCP Inspector...[/cyan]")
    try:
        import subprocess
        subprocess.run(["mcp", "dev", "app/modules/mcp/server.py"], check=True)
    except FileNotFoundError:
        console.print("[bold red]✗ mcp CLI not found. Run `pip install mcp[cli]`.[/bold red]")
        raise typer.Exit(1) from None
    except subprocess.CalledProcessError:
        raise typer.Exit(1) from None


@app.command()
def ping() -> None:
    """Sanity check: import the MCP server and call ping()."""
    try:
        from app.modules.mcp.server import mcp  # noqa: F401
        console.print("[bold green]✓ MCP server imports cleanly.[/bold green]")
    except Exception as e:  # noqa: BLE001
        console.print(f"[bold red]✗ import failed:[/bold red] {e}")
        raise typer.Exit(1) from None   # ← این خط تغییر کرد