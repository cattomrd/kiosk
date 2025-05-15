from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Union
import os

from models.database import get_db
from models.models import Slide, User
from models.schemas import SlideCreate, SlideUpdate, SlideInDB
from models.dependencies import get_admin_user, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

# Configurar plantillas
templates = Jinja2Templates(directory="templates/")

# Rutas para panel admin
@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    # Obtener slides
    slides = db.query(Slide).all()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "slides": slides, "user": current_user}
    )

@router.get("/slides/new", response_class=HTMLResponse)
async def create_slide_form(
    request: Request,
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    return templates.TemplateResponse(
        "admin/slide_form.html",
        {"request": request, "user": current_user}
    )

@router.post("/slides/new", response_class=HTMLResponse)
async def create_slide(
    request: Request,
    url: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    duration: int = Form(60),
    is_active: bool = Form(True),
    expiry_days: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    # Crear objeto de slide
    slide_data = SlideCreate(
        url=url,
        title=title,
        description=description,
        duration=duration,
        is_active=is_active,
        expiry_date=datetime.utcnow() + timedelta(days=expiry_days) if expiry_days else None
    )
    
    # Guardar en la base de datos
    db_slide = Slide(**slide_data.dict())
    db.add(db_slide)
    db.commit()
    db.refresh(db_slide)
    
    # Redireccionar al dashboard
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/slides/{slide_id}/edit", response_class=HTMLResponse)
async def edit_slide_form(
    request: Request,
    slide_id: int,
    db: Session = Depends(get_db),
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Calcular días restantes si hay fecha de expiración
    expiry_days = None
    if slide.expiry_date:
        delta = slide.expiry_date - datetime.utcnow()
        expiry_days = max(0, delta.days)
    
    return templates.TemplateResponse(
        "admin/slide_form.html",
        {"request": request, "slide": slide, "expiry_days": expiry_days, "user": current_user}
    )

@router.post("/slides/{slide_id}/edit", response_class=HTMLResponse)
async def update_slide(
    request: Request,
    slide_id: int,
    url: str = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    duration: int = Form(60),
    is_active: bool = Form(True),
    expiry_days: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Actualizar datos
    slide.url = url
    slide.title = title
    slide.description = description
    slide.duration = duration
    slide.is_active = is_active
    slide.expiry_date = datetime.utcnow() + timedelta(days=expiry_days) if expiry_days else None
    
    # Guardar cambios
    db.commit()
    db.refresh(slide)
    
    # Redireccionar al dashboard
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/slides/{slide_id}/delete", response_class=HTMLResponse)
async def delete_slide(
    request: Request,
    slide_id: int,
    db: Session = Depends(get_db),
    current_user: Union[User, RedirectResponse] = Depends(get_admin_user)
):
    # Si current_user es una respuesta de redirección, devolverla
    if isinstance(current_user, RedirectResponse):
        return current_user
        
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    db.delete(slide)
    db.commit()
    
    # Redireccionar al dashboard
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)