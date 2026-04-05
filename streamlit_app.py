import streamlit as st
import requests
import base64
import json
import time

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lexara · Document Analysis API",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Import fonts */
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  /* ── GLOBAL: force light theme, all text dark ── */
  html, body { background: #f7f5f0 !important; color: #1a1a2e !important; }
  .stApp { background: #f7f5f0 !important; color: #1a1a2e !important; }

  /* Nuke white text everywhere */
  .stApp p, .stApp span, .stApp div, .stApp label,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp li,
  [data-testid="stMarkdownContainer"],
  [data-testid="stMarkdownContainer"] *,
  .stMarkdown, .stMarkdown * { color: #1a1a2e !important; }

  /* Sidebar */
  section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #ddd9ce; }
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] *,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] div { color: #1a1a2e !important; }

  /* Hide header */
  header[data-testid="stHeader"] { background: transparent; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: #ffffff !important; border: 1px solid #ddd9ce !important;
    border-radius: 12px !important; padding: 16px !important;
    box-shadow: 0 2px 12px rgba(26,26,46,0.06);
  }
  [data-testid="metric-container"] * { color: #1a1a2e !important; }
  [data-testid="stMetricLabel"] * { color: #8888aa !important; font-size: 13px !important; }
  [data-testid="stMetricValue"] * { color: #1a1a2e !important; font-weight: 700 !important; }
  [data-testid="stMetricDelta"] { color: #3d3d5c !important; }
  [data-testid="stMetricDelta"] svg { display: none; }

  /* Inputs */
  .stTextInput > div > div > input,
  .stTextArea > div > div > textarea {
    background: #f7f5f0 !important; border: 1.5px solid #ddd9ce !important;
    border-radius: 8px !important; font-family: 'DM Mono', monospace !important;
    font-size: 13px !important; color: #1a1a2e !important;
  }
  .stTextInput > div > div > input:focus,
  .stTextArea > div > div > textarea:focus {
    border-color: #e8642a !important;
    box-shadow: 0 0 0 3px rgba(232,100,42,0.1) !important;
    background: #ffffff !important;
  }
  .stTextInput > div > div > input::placeholder,
  .stTextArea > div > div > textarea::placeholder { color: #8888aa !important; }
  .stTextInput label *, .stTextArea label * { color: #1a1a2e !important; }

  /* Buttons */
  .stButton > button {
    background: #1a1a2e !important; color: #ffffff !important;
    border: none !important; border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important;
    font-size: 15px !important; padding: 12px 28px !important;
    width: 100% !important; transition: all 0.2s !important;
  }
  .stButton > button:hover { background: #e8642a !important; }
  .stButton > button *, .stButton > button p { color: #ffffff !important; }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background: #ffffff; border: 2px dashed #ddd9ce;
    border-radius: 12px; padding: 8px;
  }
  [data-testid="stFileUploader"]:hover { border-color: #e8642a; }
  [data-testid="stFileUploader"] * { color: #1a1a2e !important; }
  [data-testid="stFileUploaderDropzoneInstructions"] * { color: #3d3d5c !important; }

  /* Alerts — keep their own foreground colour */
  .stAlert { border-radius: 10px !important; }

  /* Expander */
  .streamlit-expanderHeader,
  [data-testid="stExpander"] summary {
    background: #ffffff !important; border: 1px solid #ddd9ce !important;
    border-radius: 10px !important; font-weight: 600 !important; color: #1a1a2e !important;
  }
  [data-testid="stExpander"] summary * { color: #1a1a2e !important; }
  [data-testid="stExpander"] { border: 1px solid #ddd9ce !important; border-radius: 10px !important; }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    background: #ffffff; border-radius: 10px; padding: 4px;
    border: 1px solid #ddd9ce; gap: 4px;
  }
  .stTabs [data-baseweb="tab"] { border-radius: 8px !important; font-weight: 500 !important; color: #8888aa !important; }
  .stTabs [data-baseweb="tab"] * { color: #8888aa !important; }
  .stTabs [aria-selected="true"] { background: #1a1a2e !important; color: #ffffff !important; }
  .stTabs [aria-selected="true"] * { color: #ffffff !important; }

  /* Caption */
  .stCaption, [data-testid="stCaptionContainer"] * { color: #8888aa !important; }

  /* Code blocks */
  .stCodeBlock { border-radius: 10px !important; }

  /* Divider */
  hr { border-color: #ddd9ce !important; }

  /* Spinner */
  .stSpinner > div { border-top-color: #e8642a !important; }

  /* Custom badges */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.5px;
  }
  .badge-pass   { background: #e8faf3; color: #1db87a; border: 1px solid rgba(29,184,122,0.3); }
  .badge-fail   { background: #fde8e8; color: #e82a2a; border: 1px solid rgba(232,42,42,0.3); }
  .badge-warn   { background: #fdf5e8; color: #e8a22a; border: 1px solid rgba(232,162,42,0.3); }
  .badge-skip   { background: #eeeae0; color: #8888aa; border: 1px solid #ddd9ce; }
  .badge-post   { background: #fdf0e8; color: #e8642a; border: 1px solid rgba(232,100,42,0.2); }
  .badge-get    { background: #e8faf3; color: #1db87a; border: 1px solid rgba(29,184,122,0.2); }

  /* Check rows */
  .check-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px;
    background: #f7f5f0;
    border: 1px solid #ddd9ce;
    border-radius: 10px;
    margin-bottom: 8px;
  }
  .check-icon  { font-size: 18px; flex-shrink: 0; }
  .check-label { font-weight: 600; font-size: 14px; color: #1a1a2e; flex: 1; }
  .check-note  { font-size: 12px; color: #8888aa; margin-top: 2px; }

  /* Entity tags */
  .entity-tag {
    display: inline-block;
    background: #ffffff;
    border: 1px solid #ddd9ce;
    color: #1a1a2e;
    padding: 3px 9px;
    border-radius: 5px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    margin: 2px 3px 2px 0;
  }

  /* Result card header */
  .result-header {
    padding: 16px 0 12px;
    display: flex; align-items: center; gap: 12px;
  }
  .status-code-ok   { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 600; color: #1db87a; }
  .status-code-err  { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 600; color: #e82a2a; }
  .status-code-warn { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 600; color: #e8a22a; }

  /* Sentiment */
  .sent-positive { background:#e8faf3;color:#1db87a;padding:6px 18px;border-radius:20px;font-weight:600;font-size:14px;display:inline-block; }
  .sent-neutral  { background:#eeeae0;color:#3d3d5c;padding:6px 18px;border-radius:20px;font-weight:600;font-size:14px;display:inline-block; }
  .sent-negative { background:#fde8e8;color:#e82a2a;padding:6px 18px;border-radius:20px;font-weight:600;font-size:14px;display:inline-block; }

  /* Page title */
  .page-title {
    font-family: 'DM Serif Display', serif;
    font-size: 48px;
    letter-spacing: -2px;
    line-height: 1.05;
    color: #1a1a2e;
  }
  .page-title em { font-style: italic; color: #e8642a; }
  .eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #e8642a;
    margin-bottom: 12px;
  }
  .page-sub { font-size: 16px; color: #3d3d5c; font-weight: 300; line-height: 1.6; }

  /* History item */
  .hist-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px;
    background: #f7f5f0;
    border: 1px solid #ddd9ce;
    border-radius: 8px;
    margin-bottom: 6px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
  }
  .hist-ok  { color: #1db87a; font-weight: 600; min-width: 36px; }
  .hist-err { color: #e82a2a; font-weight: 600; min-width: 36px; }
  .hist-url { color: #8888aa; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .hist-ms  { color: #8888aa; }

  /* Note box */
  .note-box {
    background: #fdf5e8;
    border: 1px solid rgba(232,162,42,0.3);
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 13px;
    color: #3d3d5c;
    line-height: 1.5;
  }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def file_to_base64(file) -> str:
    return base64.b64encode(file.read()).decode("utf-8")

def get_file_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":   return "pdf"
    if ext == "docx":  return "docx"
    return "image"

def check_health(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False

def sentiment_html(sentiment: str) -> str:
    s = sentiment.lower()
    icon = "↑" if s == "positive" else "↓" if s == "negative" else "→"
    cls = f"sent-{s}" if s in ("positive","negative","neutral") else "sent-neutral"
    return f'<span class="{cls}">{icon} {sentiment}</span>'

def entity_tags_html(items: list) -> str:
    if not items:
        return '<span style="color:#8888aa;font-style:italic;font-size:12px;">None found</span>'
    return " ".join(f'<span class="entity-tag">{i}</span>' for i in items)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:8px 0 24px;">
      <div style="width:38px;height:38px;background:#1a1a2e;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px;">📄</div>
      <span style="font-family:'DM Serif Display',serif;font-size:22px;color:#1a1a2e;letter-spacing:-0.5px;">Lex<span style="color:#e8642a;">ara</span></span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["📊 Analyser", "🧪 Endpoint Tester"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Endpoint config
    st.markdown("**⚙️ API Configuration**")
    api_base = st.text_input("Base URL", value="https://lexaraa.onrender.com", label_visibility="collapsed", placeholder="https://lexaraa.onrender.com")
    api_key  = st.text_input("API Key", value="sk_track2_987654321", type="password", label_visibility="collapsed")

    # Health
    is_live = check_health(api_base)
    if is_live:
        st.markdown('<span class="badge badge-pass">● API LIVE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-fail">● API OFFLINE</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **🛠 Tech Stack**
    | | |
    |---|---|
    | Framework | FastAPI |
    | AI Model | LLaMA 3.3-70B |
    | Provider | Groq |
    | OCR | Tesseract |
    | Parser | pdfplumber |
    """)

    st.markdown("---")
    st.caption("GUVI Hackathon 2026 · Lexara")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — ANALYSER
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Analyser":

    st.markdown("""
    <div class="eyebrow">Document Intelligence API</div>
    <div class="page-title">Extract. Analyse.<br><em>Understand.</em></div>
    <div class="page-sub" style="margin-top:12px;margin-bottom:32px;">
      Upload any PDF, Word document, or image and get an AI-powered summary, entities, and sentiment.
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Supported Formats", "3", "PDF · DOCX · Image")
    m2.metric("AI Model", "LLaMA 3.3", "Groq · 70B")
    m3.metric("Endpoint", "POST", "/api/document-analyze")
    m4.metric("Auth", "Header", "x-api-key")

    st.markdown("---")

    col_form, col_result = st.columns([1, 1], gap="large")

    # ── FORM ──────────────────────────────────────────────────────────────────
    with col_form:
        st.markdown("### 📎 Upload Document")
        uploaded = st.file_uploader(
            "Drop your file here",
            type=["pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )

        if uploaded:
            st.success(f"✓ **{uploaded.name}** ({uploaded.size / 1024:.1f} KB)")

        st.markdown("### 🔗 Request Details")
        endpoint = st.text_input("Endpoint URL", value=f"{api_base}/api/document-analyze")

        with st.expander("📋 View Request Body Preview"):
            if uploaded:
                preview = {
                    "fileName": uploaded.name,
                    "fileType": get_file_type(uploaded.name),
                    "fileBase64": "<base64-encoded content>"
                }
                st.json(preview)
            else:
                st.caption("Upload a file to preview the request body.")

        analyze_clicked = st.button("✦ Analyse Document", use_container_width=True)

    # ── RESULT ────────────────────────────────────────────────────────────────
    with col_result:
        st.markdown("### 📋 Analysis Result")

        if analyze_clicked:
            if not uploaded:
                st.error("⚠️ Please upload a document first.")
            elif not api_key:
                st.error("⚠️ Please enter your API key in the sidebar.")
            else:
                with st.spinner("Analysing document... (first request may take ~30s to wake the server)"):
                    uploaded.seek(0)
                    b64 = file_to_base64(uploaded)
                    payload = {
                        "fileName": uploaded.name,
                        "fileType": get_file_type(uploaded.name),
                        "fileBase64": b64
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "x-api-key": api_key
                    }
                    try:
                        t0 = time.time()
                        resp = requests.post(endpoint, json=payload, headers=headers, timeout=120)
                        elapsed = round((time.time() - t0) * 1000)
                        data = resp.json()

                        if resp.status_code == 200:
                            st.session_state["last_result"] = data
                            st.session_state["last_elapsed"] = elapsed
                            st.success(f"✅ Success — {elapsed}ms")
                        else:
                            st.error(f"❌ Error {resp.status_code}: {data.get('detail','Request failed')}")
                            st.session_state.pop("last_result", None)
                    except Exception as e:
                        st.error(f"❌ Network error: {e}")
                        st.session_state.pop("last_result", None)

        if "last_result" in st.session_state:
            data = st.session_state["last_result"]
            elapsed = st.session_state.get("last_elapsed", "—")

            tab1, tab2 = st.tabs(["📄 Formatted", "{ } Raw JSON"])

            with tab1:
                # Summary
                st.markdown("**Summary**")
                st.markdown(f"""
                <div style="background:#f7f5f0;border:1px solid #ddd9ce;border-radius:10px;padding:14px 16px;font-size:14px;line-height:1.65;color:#3d3d5c;">
                  {data.get('summary','—')}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>**Sentiment**", unsafe_allow_html=True)
                st.markdown(sentiment_html(data.get("sentiment", "Neutral")), unsafe_allow_html=True)

                st.markdown("<br>**Named Entities**", unsafe_allow_html=True)
                e = data.get("entities", {})
                ec1, ec2 = st.columns(2)
                with ec1:
                    st.markdown("*People*")
                    st.markdown(entity_tags_html(e.get("names", [])), unsafe_allow_html=True)
                    st.markdown("<br>*Organisations*", unsafe_allow_html=True)
                    st.markdown(entity_tags_html(e.get("organizations", [])), unsafe_allow_html=True)
                with ec2:
                    st.markdown("*Dates*")
                    st.markdown(entity_tags_html(e.get("dates", [])), unsafe_allow_html=True)
                    st.markdown("<br>*Amounts*", unsafe_allow_html=True)
                    st.markdown(entity_tags_html(e.get("amounts", [])), unsafe_allow_html=True)

                st.markdown(f"<br><span style='font-size:12px;color:#8888aa;font-family:DM Mono,monospace;'>Response time: {elapsed}ms</span>", unsafe_allow_html=True)

            with tab2:
                st.code(json.dumps(data, indent=2), language="json")
        else:
            st.markdown("""
            <div style="background:#ffffff;border:1px solid #ddd9ce;border-radius:12px;padding:40px;text-align:center;color:#8888aa;">
              <div style="font-size:32px;margin-bottom:12px;">📭</div>
              <div style="font-size:14px;">Upload a document and click <strong>Analyse</strong> to see results here.</div>
            </div>
            """, unsafe_allow_html=True)

    # Response schema reference
    with st.expander("📐 Response Schema Reference"):
        st.code(json.dumps({
            "status": "success",
            "fileName": "document.pdf",
            "summary": "Concise 1-3 sentence summary of the document.",
            "entities": {
                "names": ["Person Name"],
                "dates": ["01 Jan 2026"],
                "organizations": ["Org Name"],
                "amounts": ["₹10,000"]
            },
            "sentiment": "Positive | Neutral | Negative"
        }, indent=2), language="json")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ENDPOINT TESTER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 Endpoint Tester":

    st.markdown("""
    <div class="eyebrow">GUVI Hackathon 2026 · Validation Tool</div>
    <div class="page-title">Endpoint <em>Tester</em></div>
    <div class="page-sub" style="margin-top:12px;margin-bottom:24px;">
      Verify your deployed Document Analysis API meets the hackathon requirements.
    </div>
    """, unsafe_allow_html=True)

    # Steps
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown("""<div style="background:#fff;border:1px solid #ddd9ce;border-radius:12px;padding:16px;text-align:center;">
          <div style="width:28px;height:28px;background:#1a1a2e;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-family:'DM Mono',monospace;margin:0 auto 8px;">1</div>
          <div style="font-weight:600;font-size:13px;">Enter Endpoint</div>
          <div style="font-size:11px;color:#8888aa;margin-top:3px;">Deployed API URL</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown("""<div style="background:#fff;border:1px solid #ddd9ce;border-radius:12px;padding:16px;text-align:center;">
          <div style="width:28px;height:28px;background:#1a1a2e;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-family:'DM Mono',monospace;margin:0 auto 8px;">2</div>
          <div style="font-weight:600;font-size:13px;">Set Headers</div>
          <div style="font-size:11px;color:#8888aa;margin-top:3px;">Auth / API key</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        st.markdown("""<div style="background:#fff;border:1px solid #ddd9ce;border-radius:12px;padding:16px;text-align:center;">
          <div style="width:28px;height:28px;background:#1a1a2e;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-family:'DM Mono',monospace;margin:0 auto 8px;">3</div>
          <div style="font-weight:600;font-size:13px;">Upload File</div>
          <div style="font-size:11px;color:#8888aa;margin-top:3px;">PDF / DOCX / Image</div>
        </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown("""<div style="background:#fff;border:1px solid #ddd9ce;border-radius:12px;padding:16px;text-align:center;">
          <div style="width:28px;height:28px;background:#e8642a;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-family:'DM Mono',monospace;margin:0 auto 8px;">4</div>
          <div style="font-weight:600;font-size:13px;">Test Endpoint</div>
          <div style="font-size:11px;color:#8888aa;margin-top:3px;">Validate response</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2], gap="large")

    # ── LEFT: REQUEST CONFIG ──────────────────────────────────────────────────
    with col_left:
        st.markdown("### 🌐 Request Configuration")

        test_endpoint = st.text_input(
            "API Endpoint URL",
            value=f"{api_base}/api/document-analyze",
            placeholder="https://your-api.example.com/api/document-analyze",
            help="Full URL of your deployed /api/document-analyze endpoint"
        )

        st.markdown("**HTTP Headers**")
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            h1_key = st.text_input("Header 1 Name", value="x-api-key", label_visibility="collapsed", placeholder="Header name")
        with hcol2:
            h1_val = st.text_input("Header 1 Value", value=api_key, label_visibility="collapsed", placeholder="Value")

        hcol3, hcol4 = st.columns(2)
        with hcol3:
            h2_key = st.text_input("Header 2 Name", value="Content-Type", label_visibility="collapsed", placeholder="Header name")
        with hcol4:
            h2_val = st.text_input("Header 2 Value", value="application/json", label_visibility="collapsed", placeholder="Value")

        extra_headers = st.text_area(
            "Additional headers (one per line, format: Key: Value)",
            placeholder="Authorization: Bearer token\nX-Custom-Header: value",
            height=80,
            label_visibility="collapsed"
        )

        st.markdown("**📁 Document File**")
        test_file = st.file_uploader(
            "Upload test document",
            type=["pdf", "docx", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
            key="tester_file"
        )

        if test_file:
            st.success(f"✓ **{test_file.name}** — {get_file_type(test_file.name).upper()} · {test_file.size/1024:.1f} KB")

        st.markdown("")
        run_test = st.button("▶ Test Endpoint", use_container_width=True)

    # ── RIGHT: WHAT THIS TESTS ────────────────────────────────────────────────
    with col_right:
        st.markdown("### 🎯 What This Tests")
        checks_spec = [
            ("🔐", "API Authentication", "x-api-key / Authorization header"),
            ("📄", "Document Processing", "PDF, DOCX, and image input handling"),
            ("✅", "Request Validation", "Correct parsing of request body"),
            ("📋", "JSON Response Format", "status, summary, entities, sentiment"),
            ("⚡", "API Stability", "Response time & reliability"),
        ]
        for icon, title, desc in checks_spec:
            st.markdown(f"""
            <div class="check-row">
              <span class="check-icon">{icon}</span>
              <div>
                <div class="check-label">{title}</div>
                <div class="check-note">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("""
        <div class="note-box">
          <strong>📌 Note:</strong> This tester is for <strong>validation purposes only</strong>.
          The final evaluation will use a separate automated system with official PDF/DOCX/image samples.
        </div>
        """, unsafe_allow_html=True)

        # History
        if "test_history" in st.session_state and st.session_state["test_history"]:
            st.markdown("<br>**🕓 Test History**", unsafe_allow_html=True)
            for h in st.session_state["test_history"][-5:][::-1]:
                ok = h["status"] == 200
                sc = f'<span class="hist-ok">{h["status"]}</span>' if ok else f'<span class="hist-err">{h["status"]}</span>'
                st.markdown(f"""
                <div class="hist-item">
                  {sc}
                  <span class="hist-url">{h["path"]}</span>
                  <span class="hist-ms">{h["ms"]}ms · {h["time"]}</span>
                </div>
                """, unsafe_allow_html=True)

    # ── TEST RESULTS ──────────────────────────────────────────────────────────
    if run_test:
        if not test_file:
            st.error("⚠️ Please upload a document file to test.")
        elif not test_endpoint:
            st.error("⚠️ Please enter an endpoint URL.")
        else:
            # Build headers
            headers = {}
            if h1_key: headers[h1_key] = h1_val
            if h2_key: headers[h2_key] = h2_val
            for line in extra_headers.strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip()] = v.strip()
            headers["Content-Type"] = "application/json"

            with st.spinner("Sending test request..."):
                test_file.seek(0)
                b64 = file_to_base64(test_file)
                payload = {
                    "fileName": test_file.name,
                    "fileType": get_file_type(test_file.name),
                    "fileBase64": b64
                }

                network_error = None
                resp = None
                data = None
                t0 = time.time()

                try:
                    resp = requests.post(test_endpoint, json=payload, headers=headers, timeout=120)
                    elapsed = round((time.time() - t0) * 1000)
                    try:
                        data = resp.json()
                    except Exception:
                        data = None
                    http_status = resp.status_code
                except Exception as e:
                    elapsed = round((time.time() - t0) * 1000)
                    network_error = str(e)
                    http_status = None

            # Save history
            if "test_history" not in st.session_state:
                st.session_state["test_history"] = []
            from datetime import datetime
            try:
                from urllib.parse import urlparse
                path = urlparse(test_endpoint).path
            except Exception:
                path = test_endpoint
            st.session_state["test_history"].append({
                "status": http_status or "ERR",
                "path": path,
                "ms": elapsed,
                "time": datetime.now().strftime("%H:%M:%S")
            })

            st.markdown("---")
            st.markdown("## 📊 Test Results")

            # Status banner
            if network_error:
                st.error(f"❌ **Network Error** — {network_error}")
            elif http_status == 200:
                st.success(f"✅ **{http_status} OK** — Request successful · {elapsed}ms")
            elif http_status == 401:
                st.error(f"🔒 **{http_status} Unauthorized** — Check your API key · {elapsed}ms")
            elif http_status and http_status >= 400:
                st.warning(f"⚠️ **{http_status}** — {data.get('detail','Error') if data else 'Error'} · {elapsed}ms")
            else:
                st.warning(f"⚠️ Status: {http_status} · {elapsed}ms")

            # Validation checks
            st.markdown("### ✔ Validation Checks")

            def render_check(icon, label, badge_cls, badge_text, note=""):
                badge_html = f'<span class="badge {badge_cls}">{badge_text}</span>'
                note_html = f'<div class="check-note">{note}</div>' if note else ""
                st.markdown(f"""
                <div class="check-row">
                  <span class="check-icon">{icon}</span>
                  <div style="flex:1;">
                    <div class="check-label">{label}</div>
                    {note_html}
                  </div>
                  {badge_html}
                </div>
                """, unsafe_allow_html=True)

            # 1. Connectivity
            if network_error:
                render_check("❌", "API Connectivity", "badge-fail", "FAIL", network_error)
            else:
                render_check("✅", "API Connectivity", "badge-pass", "PASS", "Endpoint reachable")

            if not network_error:
                # 2. Auth
                auth_ok = http_status not in (401, 403)
                render_check(
                    "✅" if auth_ok else "❌",
                    "API Authentication (x-api-key)",
                    "badge-pass" if auth_ok else "badge-fail",
                    "PASS" if auth_ok else "FAIL",
                    "Header accepted" if auth_ok else "Invalid or missing API key"
                )

                # 3. Request parsing
                parse_ok = http_status not in (400, 422)
                detail = data.get("detail","Validation failed") if data else "No response body"
                render_check(
                    "✅" if parse_ok else "⚠️",
                    "Request Parsing & Validation",
                    "badge-pass" if parse_ok else "badge-fail",
                    "PASS" if parse_ok else "FAIL",
                    "Request body accepted" if parse_ok else detail
                )

                # 4. JSON format
                if http_status == 200 and data:
                    has_status   = data.get("status") == "success"
                    has_summary  = bool(data.get("summary","").strip())
                    has_entities = isinstance(data.get("entities"), dict)
                    has_sent     = data.get("sentiment") in ("Positive","Neutral","Negative")
                    fmt_ok = all([has_status, has_summary, has_entities, has_sent])
                    missing = [f for f, v in [("status", has_status),("summary", has_summary),("entities", has_entities),("sentiment", has_sent)] if not v]
                    render_check(
                        "✅" if fmt_ok else "⚠️",
                        "JSON Response Format",
                        "badge-pass" if fmt_ok else "badge-warn",
                        "PASS" if fmt_ok else "WARN",
                        "All required fields present" if fmt_ok else f"Missing or invalid: {', '.join(missing)}"
                    )
                else:
                    render_check("⏭", "JSON Response Format", "badge-skip", "SKIPPED", "Skipped — non-200 response")

                # 5. Stability
                speed_ok = elapsed < 10000
                render_check(
                    "✅" if speed_ok else "⚠️",
                    "API Stability & Response Time",
                    "badge-pass" if speed_ok else "badge-warn",
                    "PASS" if speed_ok else "SLOW",
                    f"{elapsed}ms — {'within range' if speed_ok else 'consider optimizing'}"
                )

            # Response body
            if data:
                st.markdown("### 📦 Response Body")
                tab_fmt, tab_raw = st.tabs(["📄 Formatted", "{ } Raw JSON"])

                with tab_fmt:
                    if http_status == 200 and data.get("summary"):
                        st.markdown("**Summary**")
                        st.markdown(f"""
                        <div style="background:#f7f5f0;border:1px solid #ddd9ce;border-radius:10px;padding:14px 16px;font-size:14px;line-height:1.65;color:#3d3d5c;margin-bottom:16px;">
                          {data.get('summary','—')}
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("**Sentiment**")
                        st.markdown(sentiment_html(data.get("sentiment","Neutral")), unsafe_allow_html=True)

                        e = data.get("entities", {})
                        st.markdown("<br>**Named Entities**", unsafe_allow_html=True)
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            st.markdown("*People*")
                            st.markdown(entity_tags_html(e.get("names",[])), unsafe_allow_html=True)
                            st.markdown("<br>*Organisations*", unsafe_allow_html=True)
                            st.markdown(entity_tags_html(e.get("organizations",[])), unsafe_allow_html=True)
                        with ec2:
                            st.markdown("*Dates*")
                            st.markdown(entity_tags_html(e.get("dates",[])), unsafe_allow_html=True)
                            st.markdown("<br>*Amounts*", unsafe_allow_html=True)
                            st.markdown(entity_tags_html(e.get("amounts",[])), unsafe_allow_html=True)
                    else:
                        st.info("Response received. Check Raw JSON for details.")

                with tab_raw:
                    st.code(json.dumps(data, indent=2), language="json")
