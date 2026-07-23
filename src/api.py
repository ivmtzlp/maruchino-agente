"""API FastAPI: expone el agente de Maruchino vía HTTP y sirve el frontend."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agente import preguntar

app = FastAPI(title="Agente Maruchino", version="1.0")

# CORS (útil si algún día sirves el frontend desde otro origen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pregunta(BaseModel):
    texto: str


# --- Rutas de la API (SIEMPRE antes del mount de estáticos) ---
@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/preguntar")
def endpoint_preguntar(payload: Pregunta):
    try:
        return preguntar(payload.texto)
    except Exception as e:
        if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Límite de consultas alcanzado. Intenta de nuevo en unos minutos.",
            )
        raise HTTPException(status_code=500, detail="Error interno del agente.")


# --- Frontend estático (AL FINAL: monta "/" después de las rutas) ---
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")