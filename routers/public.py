from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from models.database import get_db
from models.models import Slide
from models.schemas import SlideInDB

router = APIRouter(tags=["public"])

# Configurar plantillas
templates = Jinja2Templates(directory="templates/")

@router.get("/", response_class=HTMLResponse)
async def show_slides(request: Request, db: Session = Depends(get_db)):
    """Página principal para mostrar los slides"""
    return templates.TemplateResponse(
        "public/slides.html",
        {"request": request}
    )

@router.get("/api/slides", response_model=List[SlideInDB])
async def get_active_slides(db: Session = Depends(get_db)):
    """API para obtener los slides activos"""
    # Obtener slides activos y no expirados
    now = datetime.utcnow()
    slides = db.query(Slide).filter(
        Slide.is_active == True,
        (Slide.expiry_date == None) | (Slide.expiry_date > now)
    ).order_by(Slide.id).all()
    
    if not slides:
        # Si no hay slides activos, podemos retornar un slide predeterminado informativo
        default_slide = {
            "id": 0,
            "url": "about:blank",
            "title": "No hay slides disponibles",
            "description": "Añada slides desde el panel de administración",
            "duration": 10,
            "is_active": True,
            "expiry_date": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return [Slide(**default_slide)]
    
    return slides

@router.get("/api/slides/{slide_id}", response_model=SlideInDB)
async def get_slide(slide_id: int, db: Session = Depends(get_db)):
    """API para obtener un slide específico"""
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    return slide