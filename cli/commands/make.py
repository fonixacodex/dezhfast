# cli/commands/make.py
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Scaffold new components (like Laravel Artisan make:*).")
console = Console()


# ---------------------------------------------------------------- templates
MODEL_TEMPLATE = '''from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class {class_name}(Base):
    __tablename__ = "{table_name}"

    id: Mapped[int] = mapped_column(primary_key=True)
    # add your fields here
'''

ROUTER_TEMPLATE = '''from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_{plural}():
    return {{"message": "{plural} list"}}
'''

SERVICE_TEMPLATE = '''from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.{module}.repository import {class_name}Repository


class {class_name}Service:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = {class_name}Repository(db)

    # add business logic here
'''

REPOSITORY_TEMPLATE = '''from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.{module}.models import {class_name}


class {class_name}Repository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[{class_name}]:
        result = await self.db.execute(select({class_name}))
        return list(result.scalars().all())
'''

SCHEMA_TEMPLATE = '''from pydantic import BaseModel, ConfigDict


class {class_name}Base(BaseModel):
    pass


class {class_name}Create({class_name}Base):
    pass


class {class_name}Read({class_name}Base):
    model_config = ConfigDict(from_attributes=True)

    id: int
'''

MODULE_INIT_TEMPLATE = '''from app.modules.{module}.router import router  # noqa: F401
'''

REQUEST_TEMPLATE = '''from pydantic import BaseModel, Field


class {class_name}Request(BaseModel):
    """Schema برای ورودی {class_name}."""

    # مثال:
    # name: str = Field(..., min_length=1, max_length=200)
    # email: str
    pass
'''

TEST_TEMPLATE = '''"""تست‌های ماژول {module}."""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def test_{module}_list(client):
    r = await client.get("/{module}/")
    assert r.status_code in (200, 401, 403)


# add more tests here
'''


# ---------------------------------------------------------------- helpers
def _paths(module: str) -> Path:
    return Path("app/modules") / module


def _ensure_module_dir(module: str) -> Path:
    d = _paths(module)
    d.mkdir(parents=True, exist_ok=True)
    init = d / "__init__.py"
    if not init.exists():
        init.write_text(MODULE_INIT_TEMPLATE.format(module=module), encoding="utf-8")
        console.print(f"[bold green]✓[/bold green] {init}")
    return d


def _write(path: Path, content: str) -> None:
    if path.exists():
        console.print(f"[bold red]✗ already exists:[/bold red] {path}")
        raise typer.Exit(1)
    path.write_text(content, encoding="utf-8")
    console.print(f"[bold green]✓ created:[/bold green] {path}")


# ---------------------------------------------------------------- commands
@app.command("model")
def make_model(
    name: str = typer.Argument(..., help="Model name, e.g. Post"),
    module: str = typer.Option(..., "--module", "-m", help="Target module, e.g. posts"),
) -> None:
    """Create a new SQLAlchemy model."""
    class_name = name[:1].upper() + name[1:]
    table_name = name.lower() + "s"
    d = _ensure_module_dir(module)
    _write(d / "models.py", MODEL_TEMPLATE.format(class_name=class_name, table_name=table_name))


@app.command("router")
def make_router(
    name: str = typer.Argument(..., help="Resource name, e.g. posts"),
    module: str = typer.Option(None, "--module", "-m", help="Target module (defaults to name)"),
) -> None:
    """Create a new FastAPI router."""
    mod = module or name
    plural = name.lower() + "s" if not name.endswith("s") else name.lower()
    d = _ensure_module_dir(mod)
    _write(d / "router.py", ROUTER_TEMPLATE.format(plural=plural))


@app.command("service")
def make_service(
    name: str = typer.Argument(..., help="Model name, e.g. Post"),
    module: str = typer.Option(..., "--module", "-m"),
) -> None:
    """Create a service class."""
    class_name = name[:1].upper() + name[1:]
    d = _ensure_module_dir(module)
    _write(d / "service.py", SERVICE_TEMPLATE.format(module=module, class_name=class_name))


@app.command("repository")
def make_repository(
    name: str = typer.Argument(..., help="Model name, e.g. Post"),
    module: str = typer.Option(..., "--module", "-m"),
) -> None:
    """Create a repository class."""
    class_name = name[:1].upper() + name[1:]
    d = _ensure_module_dir(module)
    _write(d / "repository.py", REPOSITORY_TEMPLATE.format(module=module, class_name=class_name))


@app.command("schema")
def make_schema(
    name: str = typer.Argument(..., help="Model name, e.g. Post"),
    module: str = typer.Option(..., "--module", "-m"),
) -> None:
    """Create Pydantic schemas."""
    class_name = name[:1].upper() + name[1:]
    d = _ensure_module_dir(module)
    _write(d / "schemas.py", SCHEMA_TEMPLATE.format(class_name=class_name))


@app.command("module")
def make_module(
    module: str = typer.Argument(..., help="Module name, e.g. posts"),
) -> None:
    """Scaffold a full module (models, schemas, repo, service, router)."""
    d = _ensure_module_dir(module)
    class_name = module[:1].upper() + module[1:]
    plural = module.lower()
    _write(d / "models.py",     MODEL_TEMPLATE.format(class_name=class_name, table_name=plural))
    _write(d / "schemas.py",    SCHEMA_TEMPLATE.format(class_name=class_name))
    _write(d / "repository.py", REPOSITORY_TEMPLATE.format(module=module, class_name=class_name))
    _write(d / "service.py",    SERVICE_TEMPLATE.format(module=module, class_name=class_name))
    _write(d / "router.py",     ROUTER_TEMPLATE.format(plural=plural))


@app.command("request")
def make_request(
    name: str = typer.Argument(..., help="Request name, e.g. PostCreate"),
    module: str = typer.Option(..., "--module", "-m"),
) -> None:
    """Create a Pydantic request schema."""
    class_name = name[:1].upper() + name[1:]
    d = _ensure_module_dir(module)
    target = d / "schemas.py"
    if not target.exists():
        _write(target, REQUEST_TEMPLATE.format(class_name=class_name))
        return
    with target.open("a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(REQUEST_TEMPLATE.format(class_name=class_name))
    console.print(f"[bold green]✓ appended to:[/bold green] {target}")


@app.command("test")
def make_test(
    module: str = typer.Argument(..., help="Module name, e.g. posts"),
) -> None:
    """Create a pytest file for a module."""
    target = Path("tests") / f"test_{module}.py"
    if target.exists():
        console.print(f"[bold red]✗ already exists:[/bold red] {target}")
        raise typer.Exit(1)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(TEST_TEMPLATE.format(module=module), encoding="utf-8")
    console.print(f"[bold green]✓ created:[/bold green] {target}")