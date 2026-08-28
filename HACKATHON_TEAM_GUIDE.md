# 🚀 Hackathon Master Guide: How to Build & Deploy AI Web Apps Step-by-Step with Antigravity

---

## 📌 Executive Summary

This guide provides your hackathon team with a complete, end-to-end roadmap for building and deploying a full-stack, production-grade AI web application (like **AUDIVUE**) using **Google Antigravity (AGY)**.

The PDF document has been generated and saved directly to your Desktop:
📄 **[`Hackathon_Building_and_Deployment_Guide.pdf`](file:///C:/Users/akhil/OneDrive/Desktop/AUDIVUE/Hackathon_Building_and_Deployment_Guide.pdf)**

---

## 🛠️ 1. Complete Tools & Apps Used Stack

| Domain | Tool / Technology | Purpose |
| :--- | :--- | :--- |
| **AI Assistant & IDE** | **Google Antigravity IDE / CLI (`agy`)** | Autonomous AI pair programmer, subagent orchestration, natural language code generation |
| **Frontend UI** | **HTML5, Glassmorphism CSS3, WebGL, JS ES6** | High-contrast accessible web user interface with smooth background shaders |
| **Client AI Engine** | **TensorFlow.js + COCO-SSD** | In-browser instant object detection fallback (zero downtime offline) |
| **Backend Server** | **FastAPI + Uvicorn (Python 3.11)** | High-performance asynchronous ASGI web server (`http://localhost:8000`) |
| **Computer Vision** | **PyTorch, Ultralytics YOLO11, OpenCV** | Server-side deep learning inference engine (`yolo11n.pt`) |
| **Transport Layer** | **Binary WebSockets + REST Fallback** | Low-latency binary JPEG frame streaming (`/ws/detect`) at 12–15 FPS |
| **Auth & Database** | **Firebase Auth + Firestore Console** | Google OAuth authentication & database collection (`users`) under project `audivue-258930` |
| **Voice Engine** | **Web Speech API (TTS & STT)** | Spoken audio guidance with 8-second speech cooldowns & voice command listener |
| **Version Control** | **Git & GitHub** | Distributed source code management (`https://github.com/akhilgandloji789/AUDIVUE.git`) |
| **Frontend Hosting** | **Firebase Hosting** | Free global CDN static hosting (`https://audivue-258930.web.app`) |
| **Backend Hosting** | **Render.com Cloud Python Service** | Automated cloud Python web service (`https://audivue-backend-kray.onrender.com`) |

---

## 📊 2. Step-by-Step Hackathon Development Flowchart

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STEP-BY-STEP HACKATHON DEVELOPMENT FLOW                         │
└────────────────────────────────────────────────────────────────────────────────────────┘

  [1. USER PROMPT / GOAL] ──► [2. GOOGLE ANTIGRAVITY IDE] ──► [3. IMPLEMENTATION PLAN]
                                         │
     ┌───────────────────────────────────┴───────────────────────────────────┐
     ▼                                                                       ▼
  [FRONTEND UI & CLIENT AI]                                              [BACKEND FASTAPI & YOLO11]
  • HTML5 Glassmorphism UI                                               • Python 3.11 + FastAPI + Uvicorn
  • Firebase Google OAuth Auth                                           • PyTorch YOLO11 Inference Engine
  • In-Browser TensorFlow.js Engine                                      • Spatial Telemetry & Quadrant Math
  • Web Speech Audio Guidance                                            • Binary WebSocket Stream (/ws/detect)
     │                                                                       │
     ▼                                                                       ▼
  [FRONTEND DEPLOYMENT]                                                  [BACKEND DEPLOYMENT]
  • Firebase Hosting CDN                                                 • Render.com Cloud Python Service
  • Domain: https://audivue-258930.web.app                               • Domain: https://audivue-backend...
     │                                                                       │
     └───────────────────────────────────┬───────────────────────────────────┘
                                         ▼
                             [LIVE DUAL-ENGINE AI APP]
```

---

## 🧭 3. Step-by-Step Building Process using Antigravity

### Phase 1: Conceptualize & Architect
1. Launch **Antigravity IDE** or CLI (`agy`).
2. Describe your hackathon goal in plain English:
   > *"We want to build AUDIVUE, a real-time computer vision assistant for visually impaired users."*
3. Antigravity researches the codebase, creates an `implementation_plan.md`, and structures your project directory.

### Phase 2: Build Accessible Frontend UI
1. Ask Antigravity to build responsive HTML pages (`index.html`, `env_mode.html`, `currency_mode.html`).
2. Include glassmorphic dark themes, camera `<video>` feeds, canvas bounding box overlays (`ar-box`), and spatial telemetry cards.

### Phase 3: Build Asynchronous Backend Server
1. Create `main.py` using FastAPI and Uvicorn.
2. Initialize Ultralytics YOLO11 (`YOLO("yolo11n.pt")`).
3. Add a binary WebSocket endpoint `@app.websocket("/ws/detect")` to accept video frames from the browser, run inference, calculate spatial quadrants (`Left`, `Center`, `Right`) and distance proximity (`Close`, `Medium`, `Far`), and stream JSON results back at 15 FPS.

### Phase 4: Integrate Firebase Authentication & Firestore
1. Create Firebase project `audivue-258930` in Firebase Console.
2. Add Google OAuth login provider.
3. Write `assets/firebase_auth.js` to handle Google Sign-In and save user profile records (`uid`, `name`, `email`, `lastLoginAt`) to Firestore collection `users`.

### Phase 5: Implement In-Browser AI Fallback & Voice Assistant
1. Import TensorFlow.js and COCO-SSD (`@tensorflow-models/coco-ssd`) into HTML.
2. Add an in-browser detection loop that runs if the backend WebSocket is connecting or offline.
3. Implement `voice_assistant.js` with Web Speech API for natural voice alerts and an 8-second speech cooldown to prevent repetitive talking.

---

## 🌐 4. How to Deploy Frontend (Firebase Hosting)

### Step 1: Install Firebase Tools
```bash
npm install -g firebase-tools
```

### Step 2: Initialize Firebase Hosting
```bash
firebase login
firebase init hosting
```
- Select project: `audivue-258930`.
- Public directory: `.` (or `html/`).
- Single-page app rewrite: `No`.

### Step 3: Configure `firebase.json` Rewrites
```json
{
  "hosting": {
    "public": ".",
    "rewrites": [
      { "source": "/", "destination": "/html/index.html" },
      { "source": "/env_mode.html", "destination": "/html/env_mode.html" },
      { "source": "/currency_mode.html", "destination": "/html/currency_mode.html" }
    ]
  }
}
```

### Step 4: Deploy to Global CDN
```bash
npx firebase-tools deploy --only hosting
```
Your website is live at: `https://audivue-258930.web.app`

---

## ☁️ 5. How to Deploy Backend (Render.com)

### Step 1: Prepare Repository Files
- **`requirements.txt`**:
  ```text
  fastapi>=0.100.0
  uvicorn[standard]>=0.22.0
  websockets>=11.0.3
  opencv-python-headless>=4.8.0
  numpy>=1.24.0
  ultralytics>=8.3.0
  firebase-admin>=6.2.0
  ```
- **`render.yaml`**:
  ```yaml
  services:
    - type: web
      name: audivue-backend
      env: python
      buildCommand: pip install -r requirements.txt
      startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

### Step 2: Create Web Service on Render
1. Go to [Render.com Dashboard](https://dashboard.render.com).
2. Click **+ New** -> **Web Service**.
3. Connect your GitHub repository (`akhilgandloji789/AUDIVUE`).
4. Select Language: **Python 3**.
5. Click **Create Web Service**.

### Step 3: Fix RAM / Memory Limits (Status 137 OOM Prevention)
Render's free tier has a 512 MB RAM limit. In `main.py`, restrict PyTorch thread bloat:
```python
import os, gc, torch
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
torch.set_num_threads(1)

# Periodically trigger garbage collection
gc.collect()
```

### Step 4: Connect Live Frontend to Cloud Backend
In `env_mode.html` and `currency_mode.html`:
```javascript
const ws = new WebSocket("wss://audivue-backend-kray.onrender.com/ws/detect");
```

---

## 🏆 6. Winning Hackathon Pitch Tips for Your Team

1. **Demonstrate Dual-Engine Fault Tolerance:**
   - Turn off Wi-Fi during your demo to show judges that the **in-browser TensorFlow.js AI engine** keeps working seamlessly offline!
2. **Highlight Zero Black-Box APIs:**
   - Emphasize that your team built a real computer vision pipeline (YOLO11 + WebSockets) running in under 100ms without relying on expensive, slow multimodal LLM APIs.
3. **Showcase Measurable Impact:**
   - Demonstrate real-time bounding box percentage overlays, distance proximity telemetry (`Close`, `Medium`, `Far`), and monetary note summation.

---

<p align="center">
  <b>Generated with Google Antigravity (AGY)</b><br>
  📄 PDF file saved at: <code>C:\Users\akhil\OneDrive\Desktop\AUDIVUE\Hackathon_Building_and_Deployment_Guide.pdf</code>
</p>
