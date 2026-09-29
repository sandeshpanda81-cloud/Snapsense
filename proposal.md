# SnapSense AI — Proposal

## One-line pitch
SnapSense AI is a privacy-first on-device productivity and accessibility assistant for Snapdragon-powered HP Windows PCs.

## Problem
Everyday PC workflows such as summarizing documents, extracting text from screenshots, processing voice notes and asking AI questions often depend on cloud services. This can introduce latency, internet dependency and unnecessary transfer of user data.

## Solution
SnapSense combines multiple AI workflows into a single desktop-oriented interface. It is designed around local inference, with optional cloud-free components and a model adapter layer that can be mapped to Snapdragon acceleration.

## Core features
1. Local AI Chat
2. Document summarization
3. Smart OCR
4. Voice-to-action workflow
5. Privacy/local processing indicator

## Technical architecture
Input → preprocessing → AI model → Snapdragon CPU/GPU/NPU target → result → UI

The prototype uses Python/Flask for orchestration and can use a local LLM through Ollama. Document summarization also has a lightweight extractive fallback. OCR uses Tesseract locally. The architecture is intentionally modular so Qualcomm AI Hub models can replace or supplement individual inference components on supported Snapdragon hardware.

## Innovation
Instead of building one isolated AI feature, SnapSense creates a unified local AI workspace for common PC tasks. The design emphasizes local processing, modular models, accessibility and low-friction workflows.

## Deployment
Target: Snapdragon-powered HP Windows PC.

The final submission should include measured benchmarks on the target device:
- first-token latency
- total response latency
- CPU/NPU/GPU utilization where available
- memory use
- performance with and without acceleration
- behavior when offline

Only measured values should be reported.

## Accessibility
The interface uses high-contrast dark surfaces, large controls, keyboard-friendly forms and voice interaction.

## Future work
- Qualcomm AI Hub model integration
- Verified NPU execution
- Local speech model
- Offline semantic search over personal documents
- On-device embeddings and retrieval
- Battery-aware model selection
