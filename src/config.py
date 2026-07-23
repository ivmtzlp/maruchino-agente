"""Configuración central: carga variables de entorno."""
import os
from dotenv import load_dotenv

load_dotenv()  # En local lee .env; en OCI usar las variables reales del sistema.

# --- Claves y modelos ---
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]  
MODELO_LLM = os.getenv("MODELO_LLM", "gemini-2.5-flash")
MODELO_EMBEDDINGS = os.getenv("MODELO_EMBEDDINGS", "models/gemini-embedding-001")

# --- Rutas ---
RUTA_DOCUMENTOS = os.getenv("RUTA_DOCUMENTOS", "documentos")
RUTA_INDICE = os.getenv("RUTA_INDICE", "indice_faiss")

# --- Parámetros RAG ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "4"))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "0.3"))
TEMPERATURA = float(os.getenv("TEMPERATURA", "0"))


def get_embeddings():
    """Instancia el modelo de embeddings de Gemini."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    return GoogleGenerativeAIEmbeddings(
        model=MODELO_EMBEDDINGS,
        google_api_key=GEMINI_API_KEY,
    )


def get_llm():
    """Instancia el LLM de Gemini."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=MODELO_LLM,
        temperature=TEMPERATURA,
        google_api_key=GEMINI_API_KEY,
    )