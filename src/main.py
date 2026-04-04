import os
import base64
import io
import re
import json
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# --- Document parsers ---
import pdfplumber
import docx
from PIL import Image
import pytesseract

load_dotenv()

app = FastAPI(title="Lexara — Document Analysis API", version="1.0.0")

# Serve static frontend
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
async def root():
    return FileResponse(static_dir / "index.html")


@app.get("/tester", include_in_schema=False)
async def tester():
    return FileResponse(static_dir / "tester.html")

API_KEY = os.getenv("API_KEY", "sk_track2_987654321")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


# ---------- Request / Response Models ----------

class DocumentRequest(BaseModel):
    fileName: str
    fileType: str   # pdf | docx | image
    fileBase64: str


class EntitiesModel(BaseModel):
    names: list[str]
    dates: list[str]
    organizations: list[str]
    amounts: list[str]


class DocumentResponse(BaseModel):
    status: str
    fileName: str
    summary: str
    entities: EntitiesModel
    sentiment: str


# ---------- Text Extraction ----------

def extract_text_from_pdf(data: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n".join(text_parts)


def extract_text_from_docx(data: bytes) -> str:
    doc = docx.Document(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def extract_text_from_image(data: bytes) -> str:
    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image)


def extract_text(file_type: str, data: bytes) -> str:
    ft = file_type.lower()
    if ft == "pdf":
        return extract_text_from_pdf(data)
    elif ft == "docx":
        return extract_text_from_docx(data)
    elif ft in ("image", "png", "jpg", "jpeg"):
        return extract_text_from_image(data)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


# ---------- AI Analysis ----------

SYSTEM_PROMPT = """You are a document analysis expert. Given extracted document text, return ONLY a valid JSON object (no markdown, no backticks, no explanation) with exactly these fields:
{
  "summary": "<concise 1-3 sentence summary>",
  "entities": {
    "names": ["<person name>", ...],
    "dates": ["<date>", ...],
    "organizations": ["<org name>", ...],
    "amounts": ["<monetary amount>", ...]
  },
  "sentiment": "<Positive|Neutral|Negative>"
}
Rules:
- summary: concise factual summary of the document.
- entities: extract only what is actually present; use empty lists if none found.
- sentiment: classify the overall tone as exactly one of Positive, Neutral, or Negative.
- Return ONLY the raw JSON object, nothing else."""


def analyse_with_groq(text: str) -> dict:
    truncated = text[:8000]  # stay within context limits
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Document text:\n\n{truncated}"}
        ],
        temperature=0.1,
        max_tokens=1000,
    )
    raw = response.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return json.loads(raw)


# ---------- API ----------

@app.post("/api/document-analyze", response_model=DocumentResponse)
async def analyze_document(
    request: DocumentRequest,
    x_api_key: str = Header(default=None)
):
    # Auth
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing API key")

    # Decode base64
    try:
        file_bytes = base64.b64decode(request.fileBase64)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 encoded file")

    # Extract text
    try:
        text = extract_text(request.fileType, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text found in document")

    # AI analysis
    try:
        result = analyse_with_groq(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

    return DocumentResponse(
        status="success",
        fileName=request.fileName,
        summary=result.get("summary", ""),
        entities=EntitiesModel(**result.get("entities", {"names": [], "dates": [], "organizations": [], "amounts": []})),
        sentiment=result.get("sentiment", "Neutral")
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
