# app/database/base.py
"""Base و auto-import همه‌ی مدل‌ها."""
import importlib
import pkgutil

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def import_all_models() -> None:
    """همه‌ی models.py ماژول‌ها را import می‌کند تا در metadata ثبت شوند."""
    import app.modules as modules_pkg

    for _, name, _ in pkgutil.iter_modules(modules_pkg.__path__):
        for mod_name in (f"app.modules.{name}.model", f"app.modules.{name}.models"):
            try:
                importlib.import_module(mod_name)
            except ModuleNotFoundError:
                continue