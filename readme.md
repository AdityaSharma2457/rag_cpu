<div align="center">

# 🎧 RAG-CPU

### AI-Powered Counselling Call Intelligence Engine

**Transcribe → Diarize → Fact-Check → Score → Chat** — all running on CPU.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![WhisperX](https://img.shields.io/badge/WhisperX-CPU%20int8-orange)](https://github.com/m-bain/whisperX)
[![Chroma](https://img.shields.io/badge/VectorDB-Chroma-6E56CF)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Unspecified-lightgrey)]()

</div>

---

## 🧠 What is this?

**RAG-CPU** listens to a recorded **university admission counselling call**, turns it into a speaker-labelled transcript, pulls out every factual claim the counsellor made (fees, hostel, placements, scholarships, eligibility...), and **fact-checks each one against real university brochures** stored in a vector database.

On top of that, it grades the counsellor on professionalism, empathy, objection handling, and lead-conversion skills — and produces a rich, emoji-filled markdown report you can chat with afterwards.

Everything is designed to run **without a GPU** (Whisper runs in `int8` on CPU), making it easy to deploy on lightweight servers or containers.

```
   🎙️  Audio Call
        │
        ▼
┌───────────────────┐
│   WhisperX (CPU)   │  → Transcription + Alignment + Diarization
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Claim Extraction   │  → LLM pulls verifiable claims from the transcript
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Vector Retrieval   │  → Chroma + MiniLM embeddings fetch matching brochure facts
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  RAG Verdict Engine │  → Scores accuracy + professionalism, answers your question
└───────────────────┘
        │
        ▼
   📄 Markdown Report + 💬 Follow-up Chat
```

---

## ✨ Features

| Capability | Description |
|---|---|
| 🗣️ **Speech-to-Text + Diarization** | Uses [WhisperX](https://github.com/m-bain/whisperX) to transcribe, word-align, and label speakers (`SPEAKER_00`, `SPEAKER_01`, ...) — runs on CPU with `int8` quantization. |
| 🔍 **Automatic Claim Extraction** | An LLM scans the transcript and extracts only verifiable factual claims (fees, hostel, scholarships, placements, eligibility, admission process, and more) — ignoring small talk and sales pitch. |
| 📚 **RAG Fact-Checking** | Extracted claims are converted into semantic search queries and matched against a **Chroma** vector store of official university brochure data (`all-MiniLM-L6-v2` embeddings), then labelled `Correct` / `Incorrect` / `Partially Correct` / `Insufficient Information`. |
| 🎯 **Counsellor Performance Scoring** | Scores the call 0–10 across Professionalism, Communication, Objection Handling, Product Knowledge, Empathy, SOP Adherence, and more — each with reasoning + evidence. |
| ⚡ **Parallel Vector Search** | Batched, deduplicated, multi-threaded similarity search so dozens of claims are retrieved concurrently instead of one-by-one. |
| 💬 **Follow-up Chat on Reports** | Ask questions about a completed report; conversation history is persisted per session and used as context for follow-ups. |
| 🗂️ **Session Persistence** | Every call, transcript, and report is tracked in a SQL database with status (`processing` / `completed`) so a UI can poll progress. |
| 👥 **Live Contributor Sync** | A small endpoint pulls the repo's GitHub contributors for display in a UI. |
| 🐳 **Container-Ready** | Ships with a `Dockerfile` for a one-command, reproducible CPU deployment. |

---

## 🏗️ Architecture & Project Structure

```
rag_cpu/
├── app.py                # Flask app factory — wires up config, DB, blueprints, model loading
├── config.py              # Loads SQLAlchemy DB URI from .env
├── model_loader.py         # Loads WhisperX + diarization + alignment models, and the LLM client
├── db_init_.py             # SQLAlchemy() instance
├── db.py                  # ORM models: transcription_table, history_table
├── transcription.py         # /transcribe, /health, /sessions, /followup routes
├── full_execution.py        # Orchestrates claim extraction → batched retrieval → RAG pipeline → persistence
├── ragEngine.py            # The LangChain prompt/pipeline that verifies claims + scores the call
├── further_chat.py          # Follow-up Q&A over a previously generated report
├── vector_db.py            # Chroma vector store + HuggingFace embeddings config
├── vector_storage.py        # Reference scripts for bulk-loading brochure data (JSON/JSONL) into Chroma
├── contributors.py          # GitHub contributors endpoint
├── reports/                # Generated markdown reports (per-call)
├── requirements.txt
└── Dockerfile
```

### How a request flows

1. **`POST /transcribe/transcribe`** — audio + session_id + optional question come in.
2. Audio is saved, transcribed & translated to English, word-aligned, and diarized via **WhisperX**.
3. The transcript is saved as a `.toon` file (a compact `speaker: "text"` conversation format).
4. **`full_execution()`** asks the LLM to extract factual claims and turn them into semantic search queries.
5. Queries are deduplicated and run **in parallel** against the **Chroma** vector store of university brochures.
6. The **RAG engine** (`ragEngine.py`) verifies every claim, scores the counsellor's performance, and answers the optional user question — all in one richly formatted markdown response.
7. The report is saved to `reports/`, and session history is persisted to the database.
8. Later, **`POST /transcribe/followup`** lets you keep chatting about that report with full conversational context.

---

## 🔌 API Reference

All routes are mounted under the `/transcribe` prefix.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/transcribe/transcribe` | Upload an audio file (`multipart/form-data`: `session_id`, `audio`, optional `question`). Runs the full pipeline and returns the generated report. |
| `GET`  | `/transcribe/health` | Basic health check. |
| `GET`  | `/transcribe/sessions` | Lists all sessions with title, status, and last-updated time. |
| `GET`  | `/transcribe/sessions/<session_id>` | Full history + status for a single session. |
| `POST` | `/transcribe/followup` | Ask a follow-up question about a session's report. Body: `{"session_id": "...", "question": "..."}`. |

There's also a **`/contributors/avatar_sync`** endpoint (outside the `/transcribe` prefix) that returns the live list of GitHub contributors for this repo.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- `ffmpeg` installed and on your `PATH` (required by WhisperX/audio processing)
- A SQL database reachable via a SQLAlchemy connection string
- API keys for the LLM provider(s) you plan to use (see below)

### 1. Clone & set up a virtual environment

```bash
git clone https://github.com/AdityaSharma2457/rag_cpu.git
cd rag_cpu

python -m venv venv

# Windows
.\venv\Scripts\activate.ps1

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
# Database
SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@host:port/dbname

# Whisper / Diarization
WHISPER_MODEL=small
WHISPER_DEVICE=cpu
HF_TOKEN=your_huggingface_token          # required for pyannote diarization models

# LLM providers
NEMOTRON=your_nvidia_api_key             # used via NVIDIA's OpenAI-compatible endpoint
GEMINI_API_KEY=your_gemini_api_key

# GitHub contributors sync
GITHUB_TOKEN=your_github_token
```

> 💡 Accept the relevant model terms on Hugging Face for the `pyannote` diarization/segmentation models before running — otherwise diarization will fail with an auth error.

### 3. Run the app

```bash
python app.py
```

The API will be live at `http://localhost:5000`.

### 4. (Optional) Load your knowledge base

Before fact-checking will produce useful results, populate the Chroma vector store with your university brochure data. See the reference loaders in `vector_storage.py` for JSON/JSONL ingestion patterns — point them at your own data folders and run them once to build `./chroma_db`.

---

## 🐳 Run with Docker

```bash
docker build -t rag-cpu .
docker run -p 5000:5000 --env-file .env rag-cpu
```

The image is based on `python:3.11-slim` with `ffmpeg`, `gcc`, and `g++` preinstalled for audio processing and native package builds.

---

## 🛠️ Tech Stack

- **API:** Flask, Flask-CORS, Flask-SQLAlchemy
- **Speech:** WhisperX (CPU, `int8`), pyannote diarization & alignment
- **RAG / LLM Orchestration:** LangChain (`langchain-core`, `langchain-community`)
- **Vector Store:** ChromaDB with `sentence-transformers/all-MiniLM-L6-v2` embeddings
- **LLM Providers:** NVIDIA NIM (Nemotron, via OpenAI-compatible client), Google Gemini
- **Database:** SQLAlchemy (session/report/transcript tracking)
- **Deployment:** Docker

---

## 🗺️ Roadmap Ideas

- [ ] Pluggable embedding/vector-store backends
- [ ] Streaming transcription progress over WebSockets
- [ ] Multi-language claim extraction
- [ ] Admin dashboard for reviewing flagged incorrect claims

---

## 🤝 Contributing

Issues and pull requests are welcome! Live contributor avatars are available via the `/contributors/avatar_sync` endpoint for anyone building a UI on top of this API.

---

<div align="center">

Made with ☕ and a healthy respect for CPUs.

</div>
