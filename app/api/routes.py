from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import crud
from app.core.reconocimiento import reconocer_rostro

router = APIRouter()

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🏁 Inicio
@router.get("/")
def index():
    return {"mensaje": "Microservicio control_ingreso activo"}

# ✅ Registrar nuevo personal
@router.post("/personal/registrar")
async def registrar_personal(
    nombre: str = Form(...),
    documento: str = Form(...),
    cargo: str = Form(...),
    email: str = Form(...),
    hora_entrada: str = Form(...),
    hora_salida: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    return await crud.crear_personal(nombre, documento, cargo, email, hora_entrada, hora_salida, file, db)

# 🔍 Listar personal
@router.get("/personal")
def listar_personal(db: Session = Depends(get_db)):
    return crud.obtener_personal(db)

# 🎯 Reconocer rostro (con ajuste solicitado)
@router.post("/reconocer")
async def reconocer(
    file: UploadFile = File(...),
    tipo: str = Form(...),  # Ahora se recibe explícitamente "entrada" o "salida"
    db: Session = Depends(get_db)
):
    return await reconocer_rostro(file, tipo, db)

# 🕓 Historial de registros
@router.get("/historial")
def historial(db: Session = Depends(get_db)):
    return crud.obtener_historial(db)


@router.get("/historial/{documento}")
def historial_por_documento(documento: str, db: Session = Depends(get_db)):
    return crud.obtener_historial_por_documento(documento, db)
