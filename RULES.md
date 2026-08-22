# Development Rules & Technical Guidelines — AUDIVUE

---

## 1. What to Use

- **Real Computer Vision Architectures:** Use **YOLOv8** (PyTorch / Ultralytics) as the primary object detection framework for both pipelines.
- **Pretrained Weights for General Objects:** Use pretrained COCO weights (`yolov8n.pt` / `yolov8s.pt`) for Pipeline 1 (Obstacle & Object Awareness) to save build time.
- **Custom Fine-Tuned Weights for Currency:** Use fine-tuned YOLOv8 model weights trained on Indian currency datasets (₹10 to ₹2000) for Pipeline 2 (Currency Detection & Counting).
- **Quantifiable Telemetry Output:** Extract real bounding box coordinates $(x, y, w, h)$, class confidence scores, spatial quadrants (*left, center, right*), distance vectors (*close, medium, far*), and calculated currency totals ($\sum \text{denominations}$).
- **Live Stream Input Processing:** Use OpenCV (`cv2.VideoCapture`) or WebRTC for real-time video frame ingestion.
- **Non-Blocking Execution:** Run vision pipelines asynchronously so video processing loops never freeze or drop frames.
- **Modular Code Architecture:** Keep vision inference logic, spatial math, and currency summation strictly decoupled in separate modules.

---

## 2. What to Avoid

- **Black-Box Vision APIs as Primary Pipeline:** **DO NOT** use third-party multimodal LLMs or vision APIs (OpenAI GPT-4V, Google Cloud Vision, AWS Rekognition) as the core vision detection pipeline (violates Track 03 rules).
- **Non-Quantifiable / Plain Text Descriptions:** **DO NOT** rely on unstructured text descriptions without underlying bounding boxes, labels, and computed numerical totals.
- **Mocked or Hardcoded Telemetry:** **DO NOT** use hardcoded bounding box coordinates or dummy money totals in production pipelines.
- **Cloud-Only Infrastructure Dependencies:** **DO NOT** build inference logic that fails when internet connectivity is lost; local edge processing is required.
