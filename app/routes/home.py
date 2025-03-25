import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, FileResponse
from app.core.templates import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    return templates.TemplateResponse("form_submission.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def serve_admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
