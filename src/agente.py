"""Agente con LangGraph: router de intención + RAG."""
from typing import Literal, List, Optional, TypedDict

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langgraph.graph import START, END, StateGraph

from src import config
from src.rag import buscar_respuesta

# --- 1. Clasificador de intención (salida estructurada) ---
PROMPT_ROUTER = """
Eres un clasificador para el asistente interno de la cafetería 'Maruchino'.
Clasifica la pregunta del usuario en una de estas categorías y devuelve SOLO JSON:
{
  "categoria": "CONSULTA" | "PEDIR_INFO",
  "tema": "SALUBRIDAD" | "SEGURIDAD" | "PROMOCIONES" | "RECETAS" | "OTRO"
}
Reglas:
- CONSULTA: pregunta clara sobre salubridad, seguridad, promociones o recetas.
- PEDIR_INFO: mensaje vago o sin tema identificable (ej. "necesito ayuda").
"""


class RouterOut(BaseModel):
    categoria: Literal["CONSULTA", "PEDIR_INFO"]
    tema: Literal["SALUBRIDAD", "SEGURIDAD", "PROMOCIONES", "RECETAS", "OTRO"]


_llm = config.get_llm()
_chain_router = _llm.with_structured_output(RouterOut)


def clasificar(pregunta: str) -> dict:
    salida: RouterOut = _chain_router.invoke([
        SystemMessage(content=PROMPT_ROUTER),
        HumanMessage(content=pregunta),
    ])
    return salida.model_dump()


# --- 2. Estado del grafo ---
class EstadoAgente(TypedDict, total=False):
    pregunta: str
    router: dict
    respuesta: Optional[str]
    citaciones: Optional[List]
    tema: Optional[str]


# --- 3. Nodos ---
def nodo_router(state: EstadoAgente) -> EstadoAgente:
    return {"router": clasificar(state["pregunta"])}


def nodo_rag(state: EstadoAgente) -> EstadoAgente:
    r = buscar_respuesta(state["pregunta"])
    return {
        "respuesta": r["respuesta"],
        "citaciones": r["citaciones"],
        "tema": state["router"].get("tema"),
    }


def nodo_pedir_info(state: EstadoAgente) -> EstadoAgente:
    return {
        "respuesta": "¿Podrías darme más detalles? Puedo ayudarte con "
                     "salubridad, seguridad, promociones del mes o recetas.",
        "citaciones": [],
    }


# --- 4. Arista condicional ---
def decidir(state: EstadoAgente) -> str:
    return "rag" if state["router"]["categoria"] == "CONSULTA" else "info"


# --- 5. Construcción del grafo ---
def _construir_grafo():
    wf = StateGraph(EstadoAgente)
    wf.add_node("router", nodo_router)
    wf.add_node("rag", nodo_rag)
    wf.add_node("pedir_info", nodo_pedir_info)
    wf.add_edge(START, "router")
    wf.add_conditional_edges("router", decidir, {"rag": "rag", "info": "pedir_info"})
    wf.add_edge("rag", END)
    wf.add_edge("pedir_info", END)
    return wf.compile()


grafo = _construir_grafo()


def preguntar(pregunta: str) -> dict:
    """Punto de entrada: ejecuta el grafo completo."""
    resultado = grafo.invoke({"pregunta": pregunta})
    return {
        "respuesta": resultado.get("respuesta", "No lo sé"),
        "citaciones": resultado.get("citaciones", []),
        "tema": resultado.get("tema"),
    }