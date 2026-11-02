# app/api/web.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.paths import TEMPLATES_DIR

router = APIRouter(tags=["web"])
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "DEZH",
            "message": "Build better backends.",
        },
    )


@router.get("/guide", response_class=HTMLResponse, include_in_schema=False)
async def docs_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="docs.html",
        context={
            "title": "Documentation",
        },
    )