# Product Requirement Document (PRD) — AUDIVUE

---

## 1. Product Vision & Overview

**AUDIVUE** is a real-time assistive Computer Vision web application designed to empower visually impaired and blind individuals by transforming live camera feeds into actionable **spatial obstacle telemetry**, **automated currency calculation**, and **hands-free voice guidance**.

---

## 2. Core Functional Requirements

### 2.1 Obstacle & Spatial Awareness Pipeline
- **Real-Time Stream Processing:** Accepts camera feeds at 12–15 FPS via binary WebSockets or client canvas.
- **Object Recognition:** Identifies everyday physical hazards (people, chairs, doors, stairs, vehicles, obstacles).
- **Spatial Quadrant Mapping:** Calculates relative horizontal position (`Left`, `Center`, `Right`).
- **Distance Proximity Estimation:** Categorizes object distance into `Close`, `Medium`, and `Far` based on relative bounding box surface area.
- **Empty Frame Handling:** Instantly clears canvas overlays and resets captions when no objects are present in the camera field of view.

### 2.2 Currency Detection & Summation Pipeline
- **Multi-Note Detection:** Recognizes multiple paper banknotes simultaneously in a single camera view.
- **Automated Summation:** Computes the total monetary sum ($\sum \text{notes}$) of all detected banknotes and provides spoken audio confirmation.

### 2.3 Firebase Authentication & User Profile Management
- **Google OAuth Sign-In:** Allows users to log in securely using their Google account.
- **Firestore Console Data Sync:** Automatically stores user profile documents (`uid`, `email`, `displayName`, `lastLoginAt`) in Firebase Console **Firestore Database collection `users`**.
- **Session Management:** Automatically redirects logged-in users to Vision Mode and provides a glassmorphic top-right profile dropdown with single-click logout.

### 2.4 Voice Assistant & Audio Telemetry
- **Priority Speech Synthesis:** Speaks spatial telemetry using natural Web Speech voices.
- **Deduplication & Cooldown:** Enforces an **8-second speech cooldown** for stationary objects to eliminate repetitive speech loops.
- **Safety Interrupts:** Critical obstacle warnings immediately preempt non-urgent audio playback.

---

## 3. Target Users

- **Primary Users:** Blind and visually impaired individuals requiring real-time assistance during physical navigation and cash transactions.
- **Secondary Users:** Assistive tech developers, caregivers, NGOs, and educational institutions for the visually impaired.

---

## 4. Track 03 // Computer Vision Technical Compliance

- **Input Stream:** Frame-by-frame live video processing.
- **CV Pipeline Architecture:** Ultralytics YOLO11 (PyTorch) + TensorFlow.js Client Engine (Zero black-box APIs).
- **Automated Understanding:** Real-time object recognition, spatial quadrant mapping, and distance estimation.
- **Measurable Output:** Bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, and computed currency totals.
