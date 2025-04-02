import face_recognition
import numpy as np
import json
from fastapi import UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from app.db import models, crud
from sqlalchemy.orm import Session

# Nivel mínimo de similitud (1 = exacto, 0 = nada)
UMBRAL_SIMILITUD = 0.45

async def reconocer_rostro(file: UploadFile, tipo: str = Form(...), db: Session = None):
    try:
        # 1. Leer y codificar rostro desde imagen
        imagen = face_recognition.load_image_file(file.file)
        codificaciones = face_recognition.face_encodings(imagen)

        if not codificaciones:
            raise HTTPException(status_code=400, detail="No se detectó rostro en la imagen")

        encoding_recibido = codificaciones[0]

        # 2. Obtener personal y comparar codificaciones
        personal = db.query(models.Personal).all()

        for persona in personal:
            encoding_guardado = np.array(json.loads(persona.encoding))
            distancia = face_recognition.face_distance([encoding_guardado], encoding_recibido)[0]

            if distancia <= UMBRAL_SIMILITUD:
                # 3. Registrar ingreso/salida
                crud.registrar_ingreso(id_personal=persona.id, tipo=tipo, db=db)
                
                return JSONResponse(content={
                    "mensaje": f"Persona reconocida como {persona.nombre}",
                    "tipo": tipo,
                    "similitud": round(1 - distancia, 4),
                    "documento": persona.documento,
                    "cargo": persona.cargo
                }, status_code=200)

        # 4. Si no se encontró coincidencia
        raise HTTPException(status_code=404, detail="Rostro no coincide con ningún personal registrado")

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")
