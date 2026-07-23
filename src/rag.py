"""RAG: carga el índice FAISS y responde preguntas sobre los documentos."""
from typing import Dict

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from src import config

# --- Carga del índice (una sola vez al importar el módulo) ---
_embeddings = config.get_embeddings()
_vectorstore = FAISS.load_local(
    config.RUTA_INDICE,
    _embeddings,
    allow_dangerous_deserialization=True,  # necesario para cargar FAISS local
)
_retriever = _vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": config.SCORE_THRESHOLD, "k": config.TOP_K},
)

# --- Prompt anti-alucinación ---
_prompt_rag = ChatPromptTemplate([
    ("system",
     """Eres el asistente interno de la cafetería 'Maruchino'.
     Respondes preguntas del personal y de los dueños sobre salubridad,
     seguridad, promociones del mes y recetas.
     Responde SIEMPRE utilizando únicamente el contexto proporcionado.
     Si la información no está en el contexto, responde exactamente 'No lo sé'.
     Sé claro, breve y práctico."""),
    ("human", "Contexto: {context}\nPregunta: {input}"),
])

_llm = config.get_llm()
_document_chain = create_stuff_documents_chain(_llm, prompt=_prompt_rag)


def buscar_respuesta(pregunta: str) -> Dict:
    """Recupera documentos relevantes y genera una respuesta fundamentada."""
    documentos = _retriever.invoke(pregunta)
    if not documentos:
        return {"respuesta": "No lo sé", "citaciones": [], "encontrado": False}

    respuesta = _document_chain.invoke({"input": pregunta, "context": documentos})

    if respuesta.strip().rstrip(".!?") == "No lo sé":
        return {"respuesta": "No lo sé", "citaciones": [], "encontrado": False}

    citas = [
        {
            "fuente": d.metadata.get("source", d.metadata.get("file_path", "desconocido")),
            "contenido": d.page_content.replace("\n", " ")[:200],
        }
        for d in documentos
    ]
    return {"respuesta": respuesta, "citaciones": citas, "encontrado": True}