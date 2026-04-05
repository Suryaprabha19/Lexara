# ── Stage 1: Base image ────────────────────────────────────────────────────────
FROM python:3.11-slim

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project files ─────────────────────────────────────────────────────────
COPY . .

# ── Environment variables (overridden at runtime) ──────────────────────────────
ENV API_KEY=sk_track2_987654321
ENV GROQ_API_KEY=""
ENV PYTHONUNBUFFERED=1
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# ── Expose port ────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Start FastAPI server ───────────────────────────────────────────────────────
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
