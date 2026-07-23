"""Ingesta: lee documentos, fragmenta, genera embeddings y persiste FAISS."""
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src import config


def cargar_documentos(ruta: str) -> list:
    """Carga todos los PDF de la carpeta indicada."""
    docs = []
    for archivo in Path(ruta).glob("*.pdf"):
        try:
            loader = PyMuPDFLoader(str(archivo))
            docs.extend(loader.load())
            print(f"Cargado: {archivo.name}")
        except Exception as e:
            print(f"Error en {archivo.name}: {e}")
    print(f"Total de páginas cargadas: {len(docs)}")
    return docs


def construir_indice() -> None:
    """Pipeline completo: carga -> chunk -> embeddings -> FAISS.save_local."""
    docs = cargar_documentos(config.RUTA_DOCUMENTOS)
    if not docs:
        raise RuntimeError("No se encontraron documentos PDF para indexar.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"Fragmentos generados: {len(chunks)}")

    embeddings = config.get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(config.RUTA_INDICE)
    print(f"Índice guardado en: {config.RUTA_INDICE}")


if __name__ == "__main__":
    construir_indice()