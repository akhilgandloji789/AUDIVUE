# Product Requirement Document (PRD) — AUDIVUE

---

## 1. What to Build

**AUDIVUE** is a real-time AI Vision Assistant that processes live camera feeds (smartphone or webcam) using local computer vision to perceive the environment on behalf of visually impaired users and delivers immediate spoken audio feedback and voice commands via an integrated **Web Voice Assistant Module**.

The system is built around two focused vision pipelines powered by local YOLOv8 architectures:

1. **Pipeline 1: Obstacle & Object Detection**
   - Ingests live video streams frame-by-frame.
   - Detects obstacles, hazards, doors, stairs, vehicles, and people using a pretrained YOLOv8 model.
   - Maps bounding box coordinates to spatial position (*left, right, center*) and distance proximity (*close, medium, far*).
   - Produces immediate spatial obstacle alerts (e.g., *"Chair ahead, slightly left, close"*).

2. **Pipeline 2: Currency Detection & Counting**
   - Analyzes camera frames focused on paper currency notes.
   - Uses a fine-tuned YOLOv8 model trained on Indian currency denominations (₹10 to ₹2000).
   - Detects multiple notes simultaneously in a single frame, identifies individual denominations, and automatically calculates the total monetary sum (e.g., *"500, 200, and 100 rupees detected — total 800 rupees"*).

3. **Web Voice Assistant Module (`voice_assistant/`)**
   - Provides text-to-speech output using top-rated natural female voices (e.g., Google US English Female, MS Jenny/Zira, Apple Samantha).
   - High-priority safety interrupts: Critical obstacle warnings immediately preempt lower-priority speech.
   - Hands-free voice commands: Listens for commands like *"obstacle mode"*, *"currency mode"*, *"repeat"*, *"status"*, and *"stop"*.

---

## 2. Target Users

- **Primary Users:** Blind and visually impaired individuals seeking independence in daily physical navigation and handling paper currency.
- **Secondary Users:** Caregivers, family members, educators at schools for the blind, and assistive technology NGOs.

---

## 3. Features

- **Real-Time Stream Ingestion:** Continuous frame-by-frame video processing.
- **Obstacle & Hazard Detection:** Identifies obstacles (chairs, doors, stairs, vehicles, people) with relative spatial quadrant and distance estimation.
- **Multi-Note Currency Recognition:** Identifies multiple banknotes simultaneously in a single camera view.
- **Automated Money Summation:** Dynamically aggregates detected banknote values into a total calculated sum ($\sum \text{notes}$).
- **Web Voice Assistant & Female TTS:** Top-rated natural female voice synthesis with priority interrupts and hands-free voice control (STT).
- **Quantifiable CV Output:** Produces exact bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, and computed currency totals (fulfilling Track 03 requirements).
- **Local Edge Inference:** Operates locally on YOLOv8 without third-party vision API dependencies.
