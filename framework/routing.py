# framework/routing.py
"""کمکی برای پیمایش درخت routeهای FastAPI (سازگار با >= 0.137)."""

from collections.abc import Iterable, Iterator


def iter_routes(routes: Iterable, prefix: str = "") -> Iterator[tuple[str, object]]:
    """به صورت بازگشتی همه‌ی (path, route) را تولید می‌کند."""
    for route in routes:
        original = getattr(route, "original_router", None)
        if original is not None:
            ctx = getattr(route, "include_context", None)
            sub_prefix = getattr(ctx, "prefix", "") or ""
            yield from iter_routes(original.routes, prefix + sub_prefix)
        else:
            path = getattr(route, "path", None)
            if path is not None:
                yield prefix + path, route


def collect_paths(routes: Iterable) -> list[str]:
    """فقط لیست pathها."""
    return [p for p, _ in iter_routes(routes)]