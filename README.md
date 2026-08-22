<p align="center">
  <h1 align="center">AUDIVUE</h1>
  <p align="center">
    <b>Real-Time AI Vision & Currency Assistant for the Visually Impaired</b><br>
    <i>Full-Stack Edge & Cloud Computer Vision Application featuring YOLO11 PyTorch, In-Browser Client AI Engine, Firebase Authentication, and Hands-Free Voice Guidance</i>
  </p>
</p>

<p align="center">
  <a href="https://audivue-258930.web.app">🌐 Live Web Application</a> •
  <a href="https://audivue-backend-kray.onrender.com">⚡ Live Cloud Backend API</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#system-architecture">Architecture</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a>
</p>

---

## 📌 Production Deployment Links

- **Frontend App (Firebase Hosting):** [https://audivue-258930.web.app](https://audivue-258930.web.app)
- **Backend API & WebSockets (Render):** [https://audivue-backend-kray.onrender.com](https://audivue-backend-kray.onrender.com)
- **Firebase Console Database:** Project ID `audivue-258930`

---

## 💡 Overview & Problem Statement

Over **2.2 billion people worldwide** live with vision impairment or blindness ([WHO Report](https://www.who.int/news-room/fact-sheets/detail/blindness-and-visual-impairment)). In daily life, visually impaired individuals face critical navigation and financial independence challenges:

1. **Spatial Hazard Detection:** Traditional white canes assist with ground-level contact, but cannot detect mid-level obstacles (open cabinet doors, overhanging signs, oncoming vehicles, people, or elevated barriers).
2. **Financial Independence:** Identifying paper banknotes rapidly and summing total cash during transactions is prone to errors without assistive tech.
3. **Hands-Free Operation:** Visual feedback must be translated into immediate, non-intrusive spoken audio telemetry without requiring touchscreen interaction.

**AUDIVUE** solves these challenges by combining **live web-stream computer vision**, **spatial telemetry**, **automated currency calculation**, and a **Voice Guidance Engine**.

---

## ✨ Key Features

- **⚡ Dual-Engine Vision Pipeline:**
  - **Primary Cloud / Local Engine:** Ultralytics YOLO11 PyTorch (`yolo11n.pt` / `yolo11x.pt`) streaming over low-latency binary WebSockets (`/ws/detect`).
  - **In-Browser Client Engine:** Integrated TensorFlow.js COCO-SSD for instant, zero-downtime, offline-capable bounding box detection directly inside the browser.
- **🎯 Spatial Quadrant Telemetry & Distance Mapping:**
  - Maps detections into 3 Spatial Quadrants (`Left`, `Center`, `Right`) and 3 Distance Zones (`Close`, `Medium`, `Far`).
  - Highlights high-risk obstacles with glowing alert bounding boxes.
- **💵 Automated Multi-Note Currency Counting:**
  - Identifies multiple banknotes in frame simultaneously and calculates the monetary sum ($\sum \text{notes}$).
- **🔐 Firebase Authentication & Console Data Sync:**
  - Google OAuth authentication connected to Firebase project `audivue-258930`.
  - Automatically saves user profile records (`uid`, `displayName`, `email`, `lastLoginAt`) to Firebase Console **Firestore Database (`users` collection)**.
  - Glassmorphic top-right header Profile Dropdown with account status and one-click logout.
- **🔊 Smart Voice Assistant & Cooldown Engine:**
  - Natural Web Speech synthesis with priority safety interrupts.
  - Deduplicated voice announcements with an **8-second smart cooldown** to prevent repetitive speech loops.
  - Automatic canvas overlay clearing when the camera frame becomes empty.

---

## ⚙️ System Architecture

```
                                  ┌──────────────────────────────────────────────┐
                                  │   Browser Client (https://audivue-258930.web.app) │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                    ┌────────────────────┴────────────────────┐
                                    ▼                                         ▼
                   ┌──────────────────────────────────┐      ┌──────────────────────────────────┐
                   │ Primary Binary WebSocket Stream  │      │   In-Browser TensorFlow.js Engine │
                   │  wss://.../ws/detect (12-15 FPS) │      │     (Instant Client Fallback)    │
                   └────────────────┬─────────────────┘      └────────────────┬─────────────────┘
                                    │                                         │
                                    ▼                                         ▼
                   ┌──────────────────────────────────┐      ┌──────────────────────────────────┐
                   │  FastAPI + Uvicorn ASGI Server   │      │  Canvas Overlay & Spatial Math   │
                   │   Ultralytics YOLO11 (PyTorch)   │      │    Bounding Boxes & Proximity   │
                   └────────────────┬─────────────────┘      └────────────────┬─────────────────┘
                                    │                                         │
                                    └────────────────────┬────────────────────┘
                                                         ▼
                                       ┌───────────────────────────────────┐
                                       │   Voice Guidance & Audio Engine   │
                                       │ (Deduplicated Speech + Telemetry) │
                                       └───────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend UI** | HTML5, CSS3 Glassmorphism, WebGL | High-contrast accessible web interface |
| **Client AI Engine** | TensorFlow.js + COCO-SSD | In-browser instant client-side object detection |
| **Backend Framework** | FastAPI + Uvicorn (ASGI) | Asynchronous Python 3.11 web server |
| **Transport Layer** | WebSockets + HTTP REST Fallback | Low-latency binary JPEG streaming (`/ws/detect`) |
| **Computer Vision** | PyTorch, Ultralytics YOLO11 | Flagship real-time object detection architecture |
| **Authentication** | Firebase Auth (Google OAuth) | Project `audivue-258930` user authentication |
| **Database** | Firebase Firestore Console | User profile collection (`users/{uid}`) |
| **Voice Engine** | Web Speech API | Priority Text-to-Speech & Speech-to-Text assistant |
| **Hosting** | Firebase Hosting + Render.com | Global CDN static hosting & cloud python backend |

---

## 📁 File Structure

```
AUDIVUE/
├── main.py                  # FastAPI + Uvicorn ASGI Server & WebSocket endpoint (/ws/detect)
├── requirements.txt         # Python dependencies for cloud deployment
├── render.yaml              # Render.com Cloud Service deployment manifest
├── firebase.json            # Firebase Hosting rewrites & CDN configuration
├── .firebaserc              # Firebase project target (audivue-258930)
├── assets/
│   ├── audivue.css          # Modern glassmorphism UI styles
│   └── firebase_auth.js     # Firebase Auth (Google OAuth) & Firestore Console data sync
├── html/
│   ├── index.html           # Landing Page & Google Account Authentication
│   └── env_mode.html        # Live Vision Workspace & Real-Time Bounding Box Overlay
├── voice_assistant/
│   └── voice_assistant.js   # Voice Assistant Engine (Speech Synthesis & STT Listener)
├── README.md                # Project Overview & Deployment Documentation
├── Architecture.md          # Technical Architecture & Dataflow Diagrams
├── PRD.md                   # Product Requirements Document
└── RULES.md                 # Engineering Rules & Guidelines
```

---

## 🚀 Quick Start (Local Running)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/akhilgandloji789/AUDIVUE.git
cd AUDIVUE
pip install -r requirements.txt
```

### 2. Run FastAPI Backend Server
```bash
python main.py
```
The server will launch on `http://localhost:8000`.

### 3. Open Web Application
Navigate to `http://localhost:8000` in your web browser. Click **Sign in with Google** to launch Vision Mode!

---

## 🎯 Track 03 // Computer Vision Compliance Matrix

| Track 03 Requirement | AUDIVUE Implementation | Status |
| :--- | :--- | :---: |
| **Input Stream Processing** | Real-time video frame ingestion over WebSockets & HTML5 Canvas. | ✅ Pass |
| **CV Pipeline Architecture** | Ultralytics YOLO11 (PyTorch) + TensorFlow.js Client Engine (Zero black-box APIs). | ✅ Pass |
| **Automated Understanding** | Real-time object recognition, spatial quadrant mapping, and distance estimation. | ✅ Pass |
| **Measurable Output** | Bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, and currency totals. | ✅ Pass |

---

<p align="center">
  <i>AUDIVUE — Empowering Independence Through Real-Time Computer Vision</i>
</p>