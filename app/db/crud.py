import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from app.db import models
from fastapi import UploadFile, HTTPException
import face_recognition

# 🔹 Crear nuevo personal con su encoding facial
async def crear_personal(nombre, documento, cargo, email, hora_entrada, hora_salida, file: UploadFile, db: Session):
    imagen_bytes = await file.read()
    imagen = face_recognition.load_image_file(file.file)
    codificaciones = face_recognition.face_encodings(imagen)

    if len(codificaciones) == 0:
        raise HTTPException(status_code=400, detail="No se detectó rostro en la imagen.")

    encoding_json = json.dumps(codificaciones[0].tolist())

    nuevo = models.Personal(
        nombre=nombre,
        documento=documento,
        cargo=cargo,
        email=email,
        hora_entrada_establecida=hora_entrada,
        hora_salida_establecida=hora_salida,
        encoding=encoding_json
    )

    try:
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return {"mensaje": "Personal registrado correctamente", "id": nuevo.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El documento ya está registrado.")

# 🔹 Obtener todos los registros de personal
def obtener_personal(db: Session):
    return db.query(models.Personal).all()

# 🔹 Registrar entrada o salida
def registrar_ingreso(id_personal: int, tipo: str, db: Session):
    ahora = datetime.now()
    nuevo = models.RegistroIngreso(
        id_personal=id_personal,
        tipo=tipo,
        fecha=ahora.date(),
        hora=ahora.time()
    )
    db.add(nuevo)
    db.commit()
    return {
        "mensaje": f"{tipo.capitalize()} registrada",
        "hora": ahora.time(),
        "fecha": ahora.date()
    }

# 🔹 Obtener historial completo
def obtener_historial(db: Session):
    return db.query(models.RegistroIngreso).order_by(models.RegistroIngreso.fecha.desc()).all()


# 🔹 Obtener historial por documento
def obtener_historial_por_documento(documento: str, db: Session):
    registros = (
        db.query(
            models.RegistroIngreso.id,
            models.RegistroIngreso.tipo,
            models.RegistroIngreso.fecha,
            models.RegistroIngreso.hora,
            models.Personal.nombre,
            models.Personal.documento,
            models.Personal.cargo
        )
        .join(models.Personal, models.Personal.id == models.RegistroIngreso.id_personal)
        .filter(models.Personal.documento == documento)
        .order_by(models.RegistroIngreso.fecha.desc(), models.RegistroIngreso.hora.desc())
        .all()
    )

    return [dict(r._asdict()) for r in registros]
