"""
AUDIVUE AI Backend Server
Integrates extracted YOLOv8 Object Detection & Currency Detection Pipelines
from the extracted repository (https://github.com/123-aishwarya/ai-vision.git).
Serves real-time inference endpoints for the AUDIVUE Web Application.
"""

import os
import sys
import base64
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add extracted repository directory to Python path
REPO_PATH = r"C:\Users\akhil\.gemini\antigravity\brain\e4335997-9af7-4948-bc15-7ace823b9052\scratch\ai-vision"
if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)

# Import pipelines from extracted repository
try:
    from pipeline_obstacle import ObstacleDetectorPipeline
    from pipeline_currency import CurrencyDetectorPipeline
    print("[AUDIVUE Server] Successfully loaded AI pipelines from extracted repository.")
except Exception as e:
    print(f"[AUDIVUE Server] Error importing pipelines: {e}")
    ObstacleDetectorPipeline = None
    CurrencyDetectorPipeline = None

app = Flask(__name__, static_folder=".")
CORS(app)

# Global Pipeline Instances
obstacle_detector = None
currency_detector = None

def get_obstacle_detector():
    global obstacle_detector
    if obstacle_detector is None and ObstacleDetectorPipeline is not None:
        print("[AUDIVUE Server] Initializing YOLOv8 Obstacle Detector...")
        obstacle_detector = ObstacleDetectorPipeline("yolov8n.pt")
    return obstacle_detector

def get_currency_detector():
    global currency_detector
    if currency_detector is None and CurrencyDetectorPipeline is not None:
        print("[AUDIVUE Server] Initializing YOLOv8 Currency Detector...")
        currency_detector = CurrencyDetectorPipeline("yolov8n.pt")
    return currency_detector


def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decodes base64 image data sent from browser canvas into OpenCV BGR frame."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


@app.route("/api/detect_obstacle", methods=["POST"])
def detect_obstacle():
    """Real-time YOLOv8 Obstacle Detection API Endpoint."""
    try:
        data = request.get_json(force=True)
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Invalid image frame"}), 400

        h, w = frame.shape[:2]
        detector = get_obstacle_detector()
        
        if detector is None or detector.model is None:
            # Fallback mock response if model is loading
            return jsonify({
                "status": "initializing",
                "detections": [],
                "spoken_summary": "YOLOv8 vision model initializing..."
            })

        _, detections, spoken_summary = detector.process_frame(frame, speak=False)

        # Normalize bounding box coordinates (0.0 to 1.0) for responsive web overlays
        normalized_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            norm_box = {
                "label": det["label"],
                "confidence": round(det["confidence"], 2),
                "position": det["position"],
                "proximity": det["proximity"],
                "priority": det["priority"],
                "bbox_pct": {
                    "left": round((x1 / w) * 100, 2),
                    "top": round((y1 / h) * 100, 2),
                    "width": round(((x2 - x1) / w) * 100, 2),
                    "height": round(((y2 - y1) / h) * 100, 2)
                }
            }
            normalized_detections.append(norm_box)

        return jsonify({
            "status": "success",
            "frame_size": {"width": w, "height": h},
            "detections": normalized_detections,
            "spoken_summary": spoken_summary
        })

    except Exception as e:
        print(f"[AUDIVUE Server] Error in /api/detect_obstacle: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/detect_currency", methods=["POST"])
def detect_currency():
    """Real-time YOLOv8 Currency Detection & Summation Endpoint."""
    try:
        data = request.get_json(force=True)
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Invalid image frame"}), 400

        h, w = frame.shape[:2]
        detector = get_currency_detector()

        if detector is None or detector.model is None:
            return jsonify({
                "status": "initializing",
                "detections": [],
                "total_rupees": 0,
                "spoken_summary": "Currency detection model initializing..."
            })

        _, detections, total_rupees, spoken_summary = detector.process_frame(frame, speak=False)

        normalized_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            norm_box = {
                "label": det["label"],
                "denomination": det.get("denomination", 0),
                "confidence": round(det["confidence"], 2),
                "bbox_pct": {
                    "left": round((x1 / w) * 100, 2),
                    "top": round((y1 / h) * 100, 2),
                    "width": round(((x2 - x1) / w) * 100, 2),
                    "height": round(((y2 - y1) / h) * 100, 2)
                }
            }
            normalized_detections.append(norm_box)

        return jsonify({
            "status": "success",
            "frame_size": {"width": w, "height": h},
            "detections": normalized_detections,
            "total_rupees": total_rupees,
            "spoken_summary": spoken_summary
        })

    except Exception as e:
        print(f"[AUDIVUE Server] Error in /api/detect_currency: {e}")
        return jsonify({"error": str(e)}), 500


# Static File Routes for Website Frontend
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(path):
        return send_from_directory(".", path)
    return "Not Found", 404


if __name__ == "__main__":
    port = 8000
    print(f"[AUDIVUE Server] Starting AI Vision Web Server with YOLOv8 on http://localhost:{port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
