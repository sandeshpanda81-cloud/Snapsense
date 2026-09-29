from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import os, re, json, requests
from pypdf import PdfReader

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

ALLOWED = {".pdf", ".txt", ".png", ".jpg", ".jpeg", ".webp"}

def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()

def extractive_summary(text, max_sentences=6):
    text = clean_text(text)
    if not text:
        return "No readable text was found."
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    if not sentences:
        return text[:900]
    # Simple local scoring: sentence position + word frequency
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    scored = []
    for i, s in enumerate(sentences):
        sw = re.findall(r"[A-Za-z][A-Za-z0-9'-]{2,}", s.lower())
        score = sum(freq.get(w, 0) for w in sw) / max(len(sw), 1)
        score += max(0, 1.0 - i / max(len(sentences), 1))
        scored.append((score, i, s))
    chosen = sorted(scored, reverse=True)[:max_sentences]
    chosen = sorted(chosen, key=lambda x: x[1])
    return " ".join(s for _, _, s in chosen)

def keywords(text, n=8):
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]{3,}", text.lower())
    stop = set("""this that with from have will your about which their there what when where into also than then them they were been being for are and the you but not can has had was its our out use using user local ai ai-powered powered""".split())
    freq = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:n]]

def ollama_generate(prompt):
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=90
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception:
        return None

def read_pdf(path):
    reader = PdfReader(str(path))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pass
    return "\n".join(pages)

def read_text_file(path):
    return path.read_text(encoding="utf-8", errors="ignore")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    ollama = False
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        ollama = r.ok
    except Exception:
        pass
    return jsonify({
        "status": "online",
        "local_ai": ollama,
        "model": OLLAMA_MODEL if ollama else "Local extractive engine"
    })

@app.route("/api/summarize", methods=["POST"])
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "Please upload a PDF or TXT file."}), 400

    f = request.files["file"]
    ext = Path(f.filename).suffix.lower()
    if ext not in {".pdf", ".txt"}:
        return jsonify({"error": "Only PDF and TXT files are supported here."}), 400

    name = secure_filename(f.filename)
    path = UPLOAD_DIR / name
    f.save(path)

    try:
        text = read_pdf(path) if ext == ".pdf" else read_text_file(path)
        text = clean_text(text)
        if not text:
            return jsonify({"error": "The document contains no extractable text. For scanned PDFs, use the OCR tab."}), 400

        prompt = f"""You are a concise local productivity assistant.
Summarize the following document in 5-7 clear bullet points.
Then give a one-line takeaway.
Do not invent facts.

DOCUMENT:
{text[:18000]}
"""
        ai_summary = ollama_generate(prompt)
        summary = ai_summary if ai_summary else extractive_summary(text)
        return jsonify({
            "filename": f.filename,
            "summary": summary,
            "keywords": keywords(text),
            "characters": len(text),
            "mode": "Local LLM" if ai_summary else "Local extractive AI"
        })
    finally:
        try: path.unlink()
        except Exception: pass

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = clean_text(data.get("message", ""))
    if not message:
        return jsonify({"error": "Enter a message."}), 400

    prompt = f"""You are SnapSense AI, a private desktop productivity assistant.
Answer clearly and briefly. State uncertainty instead of inventing information.
User message: {message}
"""
    answer = ollama_generate(prompt)
    if not answer:
        answer = (
            "Local AI model is not connected yet. "
            "Install Ollama and pull a small local model such as llama3.2:3b, "
            "then restart this app. The dashboard itself is working."
        )
    return jsonify({"answer": answer, "mode": "Local LLM" if "not connected" not in answer else "Offline fallback"})

@app.route("/api/ocr", methods=["POST"])
def ocr():
    if "file" not in request.files:
        return jsonify({"error": "Please upload an image."}), 400

    f = request.files["file"]
    ext = Path(f.filename).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp"}:
        return jsonify({"error": "Please upload PNG, JPG, JPEG or WEBP."}), 400

    name = secure_filename(f.filename)
    path = UPLOAD_DIR / name
    f.save(path)

    try:
        try:
            import pytesseract
            from PIL import Image, ImageOps, ImageFilter
            img = Image.open(path).convert("L")
            img = ImageOps.autocontrast(img)
            img = img.filter(ImageFilter.SHARPEN)
            text = pytesseract.image_to_string(img)
            if not text.strip():
                text = "No text detected."
            return jsonify({"text": text.strip(), "mode": "Local OCR (Tesseract)"})
        except ImportError:
            return jsonify({
                "error": "OCR dependencies are missing. Run: pip install pillow pytesseract, then install Tesseract OCR on Windows.",
                "mode": "OCR unavailable"
            }), 500
        except Exception as e:
            return jsonify({
                "error": "OCR engine could not process this image. Make sure Tesseract OCR is installed and available in PATH.",
                "details": str(e)[:300]
            }), 500
    finally:
        try: path.unlink()
        except Exception: pass

@app.route("/api/voice", methods=["POST"])
def voice():
    data = request.get_json(silent=True) or {}
    transcript = clean_text(data.get("transcript", ""))
    if not transcript:
        return jsonify({"error": "No voice transcript received."}), 400
    prompt = f"""Convert this voice transcript into:
1. a short summary,
2. action items,
3. a concise title.
Transcript: {transcript}
"""
    answer = ollama_generate(prompt)
    if not answer:
        answer = f"Transcript captured successfully.\n\nSummary: {extractive_summary(transcript, 3)}"
    return jsonify({"answer": answer, "mode": "Local LLM" if "Transcript captured" not in answer else "Offline fallback"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
