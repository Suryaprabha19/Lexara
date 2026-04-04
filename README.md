# DocLens — AI-Powered Document Analysis API

> **GUVI Hackathon 2026** · Track 2 Submission

An intelligent document processing system that extracts, analyses, and summarises content from **PDF**, **DOCX**, and **image** files. Powered by **Groq's LLaMA 3.3-70B**, it generates concise summaries, extracts named entities (people, dates, organisations, monetary amounts), and classifies document sentiment — all via a clean REST API with a Streamlit UI.

---

## Features

- 📄 **Multi-format support** — PDF, DOCX, PNG, JPG, JPEG
- 🤖 **AI Analysis** — Summary, named entity extraction, sentiment classification
- 🔐 **API Key Authentication** — Secure `x-api-key` header auth
- 🖥️ **Streamlit UI** — Professional light-themed interface with two pages:
  - **Analyser** — Upload & analyse documents visually
  - **Endpoint Tester** — Validate your deployed API (GUVI hackathon tool)
- ⚡ **FastAPI Backend** — High-performance async REST API
- 🔍 **OCR Support** — Tesseract OCR for image-based documents

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI + Uvicorn |
| UI | Streamlit |
| AI / LLM | Groq — LLaMA 3.3-70B Versatile |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| OCR (images) | pytesseract + Pillow |
| Config | python-dotenv |

---

## Project Structure

```
guvi-hackathon-2026/
├── src/
│   ├── main.py              # FastAPI app — extraction + AI analysis
│   └── static/
│       ├── index.html       # DocLens web UI (Analyser)
│       └── tester.html      # Endpoint Tester web UI
├── streamlit_app.py         # Streamlit UI (Analyser + Endpoint Tester)
├── .streamlit/
│   └── config.toml          # Streamlit light theme config
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/guvi-doc-analysis.git
cd guvi-doc-analysis
```

### 2. Get a FREE Groq API Key (no credit card needed)
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign in and navigate to **API Keys**
3. Click **"Create API Key"** — it's free

### 3. Install Tesseract OCR (system dependency)
| OS | Command |
|---|---|
| **Windows** | Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki), add to PATH |
| **Ubuntu/Debian** | `sudo apt-get install tesseract-ocr` |
| **macOS** | `brew install tesseract` |

### 4. Create a virtual environment & install dependencies
```bash
python -m venv .venv

# Activate
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

### 5. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
API_KEY=sk_track2_987654321
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the Application

### Start the FastAPI backend
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

| URL | Description |
|---|---|
| `http://localhost:8000` | Web UI (Analyser) |
| `http://localhost:8000/tester` | Web UI (Endpoint Tester) |
| `http://localhost:8000/docs` | Swagger interactive docs |
| `http://localhost:8000/health` | Health check |

### Start the Streamlit UI (separate terminal)
```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501` — includes both **Analyser** and **Endpoint Tester** pages.

---

## API Reference

### Analyse Document

```
POST /api/document-analyze
```

**Headers**
```
Content-Type: application/json
x-api-key: sk_track2_987654321
```

**Request Body**
```json
{
  "fileName": "invoice.pdf",
  "fileType": "pdf",
  "fileBase64": "<base64-encoded file content>"
}
```

> `fileType` must be one of: `pdf`, `docx`, `image`

**Success Response (200)**
```json
{
  "status": "success",
  "fileName": "invoice.pdf",
  "summary": "This document is an invoice issued by ABC Pvt Ltd to Ravi Kumar on 10 March 2026 for ₹10,000.",
  "entities": {
    "names": ["Ravi Kumar"],
    "dates": ["10 March 2026"],
    "organizations": ["ABC Pvt Ltd"],
    "amounts": ["₹10,000"]
  },
  "sentiment": "Neutral"
}
```

**Error Responses**
| Status | Meaning |
|---|---|
| `401` | Invalid or missing `x-api-key` |
| `400` | Invalid base64 or unsupported file type |
| `422` | No extractable text found in document |
| `500` | AI analysis or text extraction failed |

### Example cURL
```bash
curl -X POST http://localhost:8000/api/document-analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track2_987654321" \
  -d '{
    "fileName": "sample.pdf",
    "fileType": "pdf",
    "fileBase64": "JVBERi0xLjQ..."
  }'
```

---

## How It Works

### Text Extraction
| Format | Library | Method |
|---|---|---|
| PDF | pdfplumber | Page-by-page text extraction preserving layout |
| DOCX | python-docx | Iterates paragraphs to reconstruct plain text |
| Image | pytesseract + Pillow | Tesseract OCR on loaded image |

### AI Analysis (Groq — LLaMA 3.3-70B)
The extracted text (truncated to 8,000 characters for context efficiency) is sent to Groq with a strict JSON-only system prompt that returns:

- `summary` — 1–3 sentence factual summary
- `entities` — structured extraction of names, dates, organisations, and amounts
- `sentiment` — exactly one of `Positive`, `Neutral`, or `Negative`

### Authentication
All requests to `/api/document-analyze` require the `x-api-key` header matching the value in `.env`. Missing or invalid keys return `401 Unauthorized`.

---

## Deployment (Render — Free Tier)

1. Push repo to GitHub (public).
2. Create a new **Web Service** on [render.com](https://render.com) pointing to the repo.
3. **Build Command:**
   ```bash
   apt-get install -y tesseract-ocr && pip install -r requirements.txt
   ```
4. **Start Command:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```
5. Add environment variables `API_KEY` and `GROQ_API_KEY` in the Render dashboard.

---

## Known Limitations

- Scanned PDFs without an embedded text layer return no text (OCR only applies to image-type uploads).
- Documents are truncated to 8,000 characters before being sent to Groq.
- Tesseract accuracy depends on image quality — low-resolution scans may produce noisy output.
- The Streamlit UI and FastAPI server must be run as separate processes.

---

## AI Tools Used

- **Groq — LLaMA 3.3-70B Versatile** — used for summary generation, entity extraction, and sentiment classification via the `groq` Python SDK.
- **Claude (claude.ai)** — used to assist in scaffolding the project structure, code, and UI.
