# 🌿 Multimodal Emotional Support Chatbot (RAG-Powered)

An empathetic, secure multimodal conversational companion designed for emotional support, mindful grounding, and evidence-based self-care techniques.

Built with **Python**, **FastAPI**, **Streamlit**, **MySQL**, and **Google Gemini Multimodal AI**.

---

## 🚀 Key Features

1. **Multimodal Inputs & Outputs**:
   - **Inputs**: User text messages, image uploads (drawings, photos, journaling), and audio voice recordings.
   - **Outputs**: Compassionate markdown text responses, synthesized spoken voice playback (TTS), and visual calming cards.
2. **Strict Emotional Support Guardrails**:
   - **Crisis & Self-Harm Interceptor**: Instantly detects acute distress or self-harm ideation, immediately deflecting to emergency resources (988 Suicide & Crisis Lifeline, Crisis Text Line 741741, International Helplines).
   - **Medical Disclaimer**: Prevents psychiatric diagnosis and medication recommendations, reinforcing the AI's role as a supportive companion rather than a clinical doctor.
   - **PII Masking**: Automatically redacts sensitive phone numbers, emails, credit cards, and SSNs before storage.
   - **Jailbreak Defense**: Mitigates prompt injection and guideline override attempts.
3. **Multimodal RAG Architecture**:
   - Built-in evidence-based knowledge base covering **5-4-3-2-1 Sensory Grounding**, **Box Breathing**, **Progressive Muscle Relaxation (PMR)**, and **CBT Cognitive Reframing**.
   - Dynamic document ingestion: Users can upload or paste new wellness guides into the system via API or UI.
4. **Resilient Database Persistence**:
   - Structured for **MySQL** (tables: `sessions`, `messages`, `documents`, `document_chunks`).
   - Seamless local SQLite fallback if the MySQL server is offline during development or testing.

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **Backend API** | FastAPI (Uvicorn ASGI) |
| **Multimodal LLM** | Google Gemini (via `google-genai` SDK) |
| **Database** | MySQL (with automatic SQLite fallback) & SQLAlchemy ORM |
| **Voice Synthesis** | gTTS (Google Text-to-Speech) / Gemini Audio |
| **RAG Retrieval** | Semantic & Trigger-Weighted Vector/Lexical Index |

---

## 📁 Project Structure

```
ai-multimodal-chatbot/
│
├── core/
│   ├── config.py             # Central environment & path settings
│   ├── guardrails.py         # Crisis detection, PII redaction, jailbreak filters
│   └── gemini_client.py      # Google Gemini multimodal client & TTS engine
│
├── database/
│   ├── connection.py         # MySQL connection manager & SQLite fallback
│   ├── models.py             # SQLAlchemy schema models
│   └── repository.py         # Session, message, and document CRUD queries
│
├── rag/
│   ├── knowledge_base/       # Grounding, CBT, and mindfulness knowledge files
│   │   ├── grounding_techniques.json
│   │   ├── cbt_coping_strategies.json
│   │   └── mindfulness_exercises.json
│   └── retriever.py          # Semantic similarity & context formatter
│
├── api/
│   ├── schemas.py            # Pydantic models for requests & responses
│   └── routes.py             # FastAPI endpoints (/chat, /sessions, /rag/upload)
│
├── frontend/
│   └── app.py                # Streamlit multimodal conversational UI
│
├── tests/                    # Automated test suites for guardrails, DB, RAG, and API
├── main.py                   # FastAPI server entrypoint
├── run_tests.py              # Test runner
└── requirements.txt          # Python dependencies
```

---

## ⚡ Quickstart Guide

### 1. Environment Setup
Copy `.env.example` to `.env` and set your credentials:
```bash
cp .env.example .env
```
Inside `.env`, configure:
- `GEMINI_API_KEY`: Your Google Gemini API Key.
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`: Your MySQL credentials. (If MySQL is not running, the application will automatically fall back to local `chatbot.db`).

### 2. Run Verification Tests
Verify all guardrails, RAG retrievers, database models, and API endpoints:
```bash
python run_tests.py
```

### 3. Start the FastAPI Backend
```bash
python main.py
```
*API Swagger Documentation is available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### 4. Start the Streamlit Frontend
In a new terminal:
```bash
streamlit run frontend/app.py
```
*Access the chat interface in your browser at: [http://localhost:8501](http://localhost:8501)*
