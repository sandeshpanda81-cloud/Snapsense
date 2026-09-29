# SnapSense AI

On-device AI productivity and accessibility assistant designed for Snapdragon-powered Windows PCs.

## Features
- Local AI chat through Ollama (optional)
- PDF/TXT document extraction and summarization
- Local extractive fallback summarizer
- Local OCR using Tesseract
- Browser speech capture + local processing
- Privacy-first architecture
- Snapdragon CPU/GPU/NPU-ready architecture for future/targeted acceleration

## 1. Requirements
- Windows 10/11
- Python 3.10+
- For the intended challenge deployment: Snapdragon-powered HP PC
- Optional: Ollama for local LLM inference
- Optional: Tesseract OCR for Smart OCR

## 2. Install
Open Command Prompt in this folder:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Run
```bash
python app.py
```

Open:
http://127.0.0.1:5000

## 4. Enable local LLM (recommended)
Install Ollama from the official Ollama website, then run:

```bash
ollama pull llama3.2:3b
```

Start the app again. SnapSense will automatically detect Ollama at:
http://localhost:11434

You can change the model:

```bash
set OLLAMA_MODEL=llama3.2:3b
```

## 5. OCR
Install Tesseract OCR for Windows and make sure `tesseract.exe` is in PATH.
Then restart the terminal and run the app.

## Snapdragon / Qualcomm AI Hub positioning
This prototype is structured as an on-device AI application. For the final Snapdragon demonstration, benchmark and integrate a Qualcomm AI Hub model supported by the target Snapdragon platform, and report measured latency/power/memory results. Do not claim NPU acceleration unless it has been verified on the target machine.

## Demo flow
1. Open Overview.
2. Show local AI status.
3. Open Local AI Chat and ask a short question.
4. Upload a PDF/TXT and generate a summary.
5. Upload a screenshot and run OCR.
6. Use Voice Assistant in Chrome/Edge.
7. Explain that local inference reduces unnecessary cloud dependency and is intended for Snapdragon CPU/GPU/NPU optimization.

## Project structure
- `app.py` — Flask backend and APIs
- `templates/index.html` — UI
- `static/style.css` — design
- `static/script.js` — frontend interactions
- `uploads/` — temporary uploaded files
