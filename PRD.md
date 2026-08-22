# Product Requirement Document (PRD) — AUDIVUE

---

## 1. What to Build

**AUDIVUE** is a real-time AI Vision Assistant that processes a camera feed (smartphone or webcam) using local computer vision to perceive the environment on behalf of visually impaired users and translates visual data into immediate spoken audio feedback.

The system is built around two core vision pipelines powered by local computer vision architectures (YOLOv8):

1. **Pipeline 1: Obstacle & Object Awareness**
   - Processes live video streams frame-by-frame.
   - Detects objects, hazards, and people in the environment using a pretrained YOLOv8 model.
   - Maps bounding box coordinates to spatial orientation (*left, right, center*) and distance proximity (*close, medium, far*).
   - Generates immediate spoken alerts (e.g., *"Chair ahead, slightly left, close"*).

2. **Pipeline 2: Currency Detection & Counting**
   - Analyzes camera feed pointed at paper currency notes.
   - Uses a fine-tuned YOLOv8 model trained on Indian currency denominations (₹10 to ₹2000).
   - Detects multiple notes simultaneously in a single frame, extracts individual values, and automatically calculates the total aggregate sum.
   - Speaks the result aloud (e.g., *"500, 200, and 100 rupees detected — total 800 rupees"*).

3. **Text-To-Speech (TTS) Layer**
   - Integrates detection telemetry into clear audio prompts, requiring zero manual screen interaction.

---

## 2. Target Users

- **Primary Users:** Blind and visually impaired individuals who require independent assistance for daily navigation, obstacle awareness, and handling monetary transactions.
- **Secondary Users:** Caregivers, family members, educators at schools for the blind, and assistive technology NGOs.
- **Future Target:** Wearable assistive device users (e.g., smart glasses, edge cameras).

---

## 3. Features

- **Real-Time Stream Processing:** Continuous frame-by-frame video ingestion from live camera streams.
- **Spatial Obstacle Detection:** Identifies mid-to-high level hazards (chairs, doors, stairs, vehicles, people) and calculates relative position and proximity.
- **Multi-Note Currency Recognition:** Detects multiple overlapping or adjacent banknotes simultaneously in a single camera view.
- **Automated Money Summation:** Dynamically aggregates individual note values into a total calculated monetary value ($\sum \text{notes}$).
- **Hands-Free Audio Guidance:** Converts bounding box telemetry into simple, clear spoken feedback without requiring touch interface inputs.
- **Quantifiable CV Output:** Produces exact bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, and calculated totals (strictly adhering to Track 03 requirements).
- **Local Edge Inference:** Operates on local YOLOv8 models without black-box third-party vision API dependencies.
