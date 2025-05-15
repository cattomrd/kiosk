from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from models.database import engine, get_db, Base
from models.models import User, Slide
from models.schemas import Token
from models.dependencies import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user_from_cookie 
from routers import admin, public
from datetime import timedelta

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Slider")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static/"), name="static")

# Configurar plantillas
templates = Jinja2Templates(directory="templates/")

# Incluir routers
app.include_router(admin.router)
app.include_router(public.router)

# Ruta para login
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, db: Session = Depends(get_db)):
    # Verificar si ya está autenticado
    user = get_current_user_from_cookie(request.cookies.get("access_token"), db)
    if user:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("admin/login.html", {"request": request})

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "admin/login.html", 
            {"request": request, "error": "Usuario o contraseña incorrectos"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convertir minutos a segundos
    )
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

# Crear usuario admin al iniciar si no existe
@app.on_event("startup")
async def startup_db_client():
    db = next(get_db())
    # Verificar si existe el usuario admin
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        # Importación absoluta en lugar de relativa
        from models.dependencies import get_password_hash
        # Crear usuario admin predeterminado
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("adminpassword"),  # Cambiar esta contraseña
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        print("Usuario admin creado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)