# Development Rules & Technical Guidelines — AUDIVUE

---

## 1. Core Engineering Directives

- **Real Computer Vision Frameworks:** Strictly use real CV architectures (**Ultralytics YOLO11** in PyTorch & **TensorFlow.js COCO-SSD** in-browser).
- **Zero Black-Box APIs for Core Vision:** **DO NOT** use third-party multimodal LLM APIs (GPT-4V, Gemini Vision, Claude Multimodal) as the primary object detection engine.
- **Dual-Engine Fault Tolerance:** Maintain both a server-side PyTorch YOLO11 binary WebSocket stream (`/ws/detect`) AND an in-browser TensorFlow.js engine for offline fallback.
- **Quantifiable Output Validation:** Every detection payload must provide bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, spatial position (`Left`, `Center`, `Right`), and distance proximity (`Close`, `Medium`, `Far`).
- **Speech Cooldown & Loop Prevention:** Voice Assistant MUST enforce speech deduplication and an **8-second cooldown** to prevent repetitive speech loops on stationary objects.
- **Empty Frame Clearing:** When no objects are detected in frame, canvas overlays MUST be cleared immediately, and spoken telemetry MUST pause.
- **Firebase Authentication Integrity:** All user logins MUST use official Firebase Auth credentials for project `audivue-258930` and sync user records to Firestore collection `users`.

---

## 2. Technical Stack Constraints

- **Backend:** FastAPI + Uvicorn (ASGI) running Python 3.11+.
- **Frontend:** Glassmorphism UI hosted on Firebase Hosting (`https://audivue-258930.web.app`).
- **Cloud Backend:** Hosted on Render.com (`https://audivue-backend-kray.onrender.com`).
- **CV Models:** `yolo11n.pt` / `yolo11x.pt` (Ultralytics) + `@tensorflow-models/coco-ssd`.
