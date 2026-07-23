"""API FastAPI: expone el agente de Maruchino vía HTTP."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.agente import preguntar

app = FastAPI(title="Agente Maruchino", version="1.0")

# CORS: permite que el frontend consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción, restringir al dominio del frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


class Pregunta(BaseModel):
    texto: str


@app.get("/salud")
def salud():
    return {"estado": "ok"}


@app.post("/preguntar")
def endpoint_preguntar(payload: Pregunta):
    return preguntar(payload.texto)