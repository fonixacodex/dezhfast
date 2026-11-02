# main.py
from pathlib import Path

from fastapi.staticfiles import StaticFiles

from app.api.web import router as web_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import register_middleware
from app.core.paths import CSS_DIR, IMAGES_DIR, JS_DIR
from app.database.base import Base, import_all_models
from app.database.connection import engine
from app.modules.auth import AuthModule
from framework import Application

# --- MCP (فعلاً کامنت) ---
# from app.modules.mcp import MCPModule
# from app.modules.mcp.server import mcp
# -------------------------


setup_logging()

# ۱. اپ
factory = Application(title=settings.APP_NAME, debug=settings.DEBUG)

# ۲. ماژول‌ها
factory.register_module(AuthModule())
# factory.register_module(MCPModule())  # MCP کامنت


# ۳. hook خودکار ساخت جدول‌ها (فقط در dev/staging)
async def _auto_create_tables() -> None:
    if settings.APP_ENV == "prod":
        return

    if settings.DB_CONNECTION == "sqlite":
        db_path = Path(settings.DB_DATABASE)
        db_path.parent.mkdir(parents=True, exist_ok=True)

    import_all_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    tables = list(Base.metadata.tables.keys())
    print(f"✅ Auto-created {len(tables)} table(s): {tables}")


factory.lifecycle.add_startup(_auto_create_tables)

# ۴. boot
app = factory.boot()

# ۵. middleware
register_middleware(app)

# ۶. exception handlers
register_exception_handlers(app)

# ۷. static
app.mount("/css", StaticFiles(directory=str(CSS_DIR)), name="css")
app.mount("/js", StaticFiles(directory=str(JS_DIR)), name="js")
app.mount("/images", StaticFiles(directory=str(IMAGES_DIR)), name="images")

# ۸. web router
app.include_router(web_router)

# --- MCP (فعلاً کامنت) ---
# register_tools()
# app.mount("/mcp", mcp.streamable_http_app())
# -------------------------


# ۹. health & ready
@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/ready", tags=["system"])
async def ready():
    from sqlalchemy import text
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "db": "ok"}
    except Exception as e:
        return {"status": "not_ready", "db": str(e)}