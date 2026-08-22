# Product Requirement Document (PRD) — AUDIVUE

---

## 1. What to Build

**AUDIVUE** is a real-time AI Vision Assistant that processes live camera feeds (smartphone or webcam) using local computer vision to perceive the environment on behalf of visually impaired users.

The system is built exclusively around two focused vision pipelines powered by local YOLOv8 architectures:

1. **Pipeline 1: Obstacle & Object Detection**
   - Ingests live video streams frame-by-frame.
   - Detects obstacles, hazards, doors, stairs, vehicles, and people using a pretrained YOLOv8 model.
   - Maps bounding box coordinates to spatial position (*left, right, center*) and distance proximity (*close, medium, far*).
   - Produces immediate spatial obstacle alerts (e.g., *"Chair ahead, slightly left, close"*).

2. **Pipeline 2: Currency Detection & Counting**
   - Analyzes camera frames focused on paper currency notes.
   - Uses a fine-tuned YOLOv8 model trained on Indian currency denominations (₹10 to ₹2000).
   - Detects multiple notes simultaneously in a single frame, identifies individual denominations, and automatically calculates the total monetary sum (e.g., *"500, 200, and 100 rupees detected — total 800 rupees"*).

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
- **Quantifiable CV Output:** Produces exact bounding box coordinates $(x, y, w, h)$, class labels, confidence scores, and computed currency totals (fulfilling Track 03 requirements).
- **Local Edge Inference:** Operates locally on YOLOv8 without third-party vision API dependencies.
