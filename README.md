# ☕ Agente Maruchino

Asistente interno de IA para la cafetería **Maruchino**. Responde consultas del personal y los dueños sobre **salubridad, seguridad, promociones del mes y recetas**, usando RAG (Retrieval-Augmented Generation) sobre la documentación interna del negocio.

Proyecto desarrollado para el Challenge de Alura / Oracle Next Education (ONE).

Se puede ejecutar en: http://40.233.18.3:8000/

---

## 📋 Descripción

Maruchino es un agente conversacional que combina dos capacidades:

1. **RAG sobre documentos internos** — recupera información fundamentada de los manuales de la cafetería y responde en lenguaje natural, con control anti-alucinación (si no está en los documentos, responde *"No lo sé"*).
2. **Router de intención con LangGraph** — clasifica cada consulta antes de responder, decidiendo si ejecuta el RAG o solicita más información al usuario.

El agente se expone mediante una **API REST (FastAPI)** y se consume desde un **frontend web minimalista** (HTML/CSS/JS puro).

---

## 🏗️ Arquitectura

```text
                   ┌─────────────────┐
   Usuario ───────▶│    Frontend     │  (HTML/CSS/JS)
                   │  index.html     │
                   └────────┬────────┘
                            │ POST /preguntar
                            ▼
                   ┌─────────────────┐
                   │   API FastAPI   │  (api.py)
                   └────────┬────────┘
                            ▼
                   ┌─────────────────┐
                   │  Agente         │  (agente.py)
                   │  LangGraph      │
                   │                 │
                   │  ┌───────────┐  │
                   │  │  Router   │  │  clasifica intención
                   │  └─────┬─────┘  │
                   │        │        │
                   │   ┌────┴────┐   │
                   │   ▼         ▼   │
                   │ [RAG]  [Pedir   │
                   │  │      info]   │
                   └──┼──────────────┘
                      ▼
              ┌───────────────┐      ┌──────────────┐
              │  RAG (rag.py) │─────▶│  FAISS local │
              │  retriever +  │      │ indice_faiss │
              │  LLM Gemini   │      └──────────────┘
              └───────────────┘
```

**Flujo en dos fases:**
- **Fase A — Ingesta (una sola vez):** los documentos PDF se fragmentan, se generan embeddings y se persiste el índice FAISS en disco.
- **Fase B — Servir:** la API carga el índice ya construido y responde consultas. No re-indexa en cada arranque.

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Lenguaje | Python 3.12 |
| Orquestación del agente | LangGraph |
| Framework RAG | LangChain |
| Vector store | FAISS (local, persistente) |
| LLM y embeddings | Google Gemini |
| Carga de documentos | PyMuPDF |
| API | FastAPI + Uvicorn |
| Frontend | HTML5, CSS3, JavaScript (sin frameworks) |
| Despliegue | Oracle Cloud Infrastructure (OCI) |

---

## 📁 Estructura del proyecto

```text
maruchino-agente/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── documentos/              # Fuentes del RAG (PDF)
│   ├── salubridad.pdf
│   ├── seguridad.pdf
│   ├── promociones_mes.pdf
│   └── recetas.pdf
├── src/
│   ├── config.py            # Configuración y variables de entorno
│   ├── ingesta.py           # Construye y persiste el índice FAISS
│   ├── rag.py               # Recuperación + generación de respuestas
│   ├── agente.py            # Router de intención con LangGraph
│   └── api.py               # API REST (FastAPI)
├── indice_faiss/            # Índice persistido (generado, ignorado en git)
└── frontend/
    ├── index.html
    ├── config.js            # URL de la API
    ├── app.js
    └── style.css
```

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/ivmtzlp/maruchino-agente.git
cd maruchino-agente
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```
Edita `.env` y agrega tu clave de Google Gemini:
```bash
GEMINI_API_KEY=tu_clave_aqui
MODELO_LLM=gemini-2.5-flash
MODELO_EMBEDDINGS=models/gemini-embedding-001
```

### 4. Construir el índice (una sola vez)
Coloca los 4 PDF en `documentos/` y ejecuta:
```bash
python -m src.ingesta
```

### 5. Levantar la API
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000
```
Documentación interactiva disponible en: `http://localhost:8000/docs`

### 6. Abrir el frontend
En otra terminal:
```bash
cd frontend
python -m http.server 5500
```
Abre `http://localhost:5500` en tu navegador.

---

## 💬 Ejemplos de consultas (Q&A)

> Reemplaza las respuestas con las reales obtenidas en tus pruebas.

**Salubridad**
> **P:** ¿Cada cuánto se debe limpiar la máquina de café?
> **R:** [respuesta del agente]

**Seguridad**
> **P:** ¿Dónde se encuentran los extintores del establecimiento?
> **R:** [respuesta del agente]

**Promociones**
> **P:** ¿Qué promociones hay este mes?
> **R:** [respuesta del agente]

**Recetas**
> **P:** ¿Cómo se prepara la Maruchan de la casa?
> **R:** [respuesta del agente]

**Control anti-alucinación**
> **P:** ¿Quién ganó el mundial de 2022?
> **R:** No lo sé.

---

## 🔌 API

### `GET /salud`
Verifica que el servicio está activo.
```json
{ "estado": "ok" }
```

### `POST /preguntar`
Envía una consulta al agente.

**Request:**
```json
{ "texto": "¿Cómo se prepara la Maruchan de la casa?" }
```

**Response:**
```json
{
  "respuesta": "...",
  "citaciones": [
    { "fuente": "recetas.pdf", "contenido": "..." }
  ],
  "tema": "RECETAS"
}
```

---

## ☁️ Despliegue en OCI

El proyecto está diseñado para desplegarse en Oracle Cloud Infrastructure:

- **Backend (API + agente):** OCI Compute Instance. Las variables de entorno se configuran directamente en el sistema (no se usa `.env` en producción).
- **Frontend:** puede servirse desde un OCI Object Storage Bucket o desde la misma Compute vía FastAPI `StaticFiles`.
- Al desplegar, se actualiza `frontend/config.js` con la IP pública de la instancia y se abre el puerto correspondiente en la Security List.

---

## ⚠️ Notas

- El plan gratuito de Gemini tiene límites de cuota diarios. Para un uso sostenido se recomienda habilitar facturación en el proyecto de Google.
- El índice FAISS (`indice_faiss/`) y el archivo `.env` **no se versionan** (ver `.gitignore`).
- Cada consulta consume dos llamadas al LLM (router + RAG).

---

## 📄 Licencia

Proyecto educativo desarrollado para el Challenge de Alura / Oracle Next Education.
"# maruchino-agente" 
