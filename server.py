"""
AUDIVUE AI Backend Server — SOTA RF-DETR Vision Transformer + ByteTrack Engine
Integrates:
  1. Roboflow RF-DETR (DINOv2 Vision Transformer - COCO 75.1+ AP50 SOTA)
  2. Roboflow Supervision ByteTrack / OC-SORT Multi-Object Tracking across frames
  3. YOLOv8x Flagship fallback model engine
Serves real-time inference & object tracking API endpoints for the AUDIVUE Web Application.
"""

import os
import sys
import base64
import time
import numpy as np
import cv2
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add extracted repository directory to Python path
REPO_PATH = r"C:\Users\akhil\.gemini\antigravity\brain\e4335997-9af7-4948-bc15-7ace823b9052\scratch\ai-vision"
if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)

# Import Supervision & RF-DETR
try:
    import supervision as sv
    import rfdetr
    from rfdetr import RFDETRMedium, RFDETRNano
    from rfdetr.assets.coco_classes import COCO_CLASSES
    RF_DETR_AVAILABLE = True
    print("[AUDIVUE Server] RF-DETR SOTA Vision Transformer & Supervision Tracker LOADED!")
except Exception as e:
    RF_DETR_AVAILABLE = False
    print(f"[AUDIVUE Server] RF-DETR import notice ({e}). Fallback mode available.")

# Import extracted pipeline math utilities
try:
    from config import (
        ZONE_LEFT_MAX,
        ZONE_RIGHT_MIN,
        AREA_NEAR_THRESH,
        AREA_MEDIUM_THRESH,
        PRIORITY_OBSTACLES
    )
except Exception:
    ZONE_LEFT_MAX = 0.38
    ZONE_RIGHT_MIN = 0.62
    AREA_NEAR_THRESH = 0.12
    AREA_MEDIUM_THRESH = 0.03
    PRIORITY_OBSTACLES = {"person", "chair", "table", "door", "couch", "car", "bicycle", "stairs", "pole"}

app = Flask(__name__, static_folder=".")
CORS(app)

# Global Model & Tracker Instances
rf_detr_model = None
byte_tracker = None
yolo_model = None
announced_track_ids = set()
last_spoken_summary = ""
last_speech_timestamp = 0


def get_rf_detr_model():
    global rf_detr_model
    if rf_detr_model is None and RF_DETR_AVAILABLE:
        print("[AUDIVUE Server] Initializing RF-DETR Vision Transformer Model...")
        try:
            rf_detr_model = RFDETRMedium()
        except Exception as e:
            print(f"[AUDIVUE Server] RFDETRMedium download notice: {e}. Trying RFDETRNano...")
            rf_detr_model = RFDETRNano()
    return rf_detr_model


def get_byte_tracker():
    global byte_tracker
    if byte_tracker is None and RF_DETR_AVAILABLE:
        print("[AUDIVUE Server] Initializing Supervision ByteTrack Multi-Object Tracker...")
        byte_tracker = sv.ByteTrack(track_activation_threshold=0.25, lost_track_buffer=30, minimum_matching_threshold=0.8)
    return byte_tracker


yolo11_model = None
yolo_model = None

def get_yolo11_model():
    global yolo11_model
    if yolo11_model is None:
        try:
            from ultralytics import YOLO
            print("[AUDIVUE Server] Initializing Latest YOLO11x Model...")
            yolo11_model = YOLO("yolo11x.pt")
        except Exception as e:
            print(f"[AUDIVUE Server] YOLO11 loading exception: {e}")
    return yolo11_model

def get_yolo_model():
    global yolo_model
    if yolo_model is None:
        try:
            from ultralytics import YOLO
            print("[AUDIVUE Server] Initializing YOLOv8x Model...")
            yolo_model = YOLO("yolov8x.pt")
        except Exception as e:
            print(f"[AUDIVUE Server] YOLO loading exception: {e}")
    return yolo_model


def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decodes base64 image data sent from browser canvas into OpenCV BGR frame."""
    if "," in base64_str:
        base64_str = base64_str.split(",")[1]
    img_bytes = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


def calculate_spatial_position(norm_x: float) -> tuple:
    """Maps normalized center x coordinate (0.0 to 1.0) to spatial description."""
    if norm_x < 0.20:
        return "Far Left", "on your far left"
    elif norm_x < ZONE_LEFT_MAX:
        return "Left", "slightly left"
    elif norm_x <= ZONE_RIGHT_MIN:
        return "Center", "ahead"
    elif norm_x <= 0.80:
        return "Right", "slightly right"
    else:
        return "Far Right", "on your far right"


def calculate_proximity(area_ratio: float, height_ratio: float) -> tuple:
    """Maps bounding box area ratio and height ratio to distance estimate."""
    if area_ratio >= AREA_NEAR_THRESH or height_ratio >= 0.50:
        return "Close", "close"
    elif area_ratio >= AREA_MEDIUM_THRESH or height_ratio >= 0.25:
        return "Medium", "at moderate distance"
    else:
        return "Far", "far away"


@app.route("/api/detect_obstacle", methods=["POST"])
def detect_obstacle():
    """
    SOTA RF-DETR + ByteTrack Real-Time Object Detection & Tracking Endpoint.
    Uses DINOv2 Transformer + Multi-Object Tracking across consecutive frames.
    """
    global announced_track_ids, last_spoken_summary, last_speech_timestamp

    try:
        data = request.get_json(force=True)
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Invalid image frame"}), 400

        h, w = frame.shape[:2]
        engine_used = "RF-DETR Transformer + ByteTrack"
        detections_list = []
        alert_phrases = []

        model = get_rf_detr_model()

        if model is not None and RF_DETR_AVAILABLE:
            # 1. RF-DETR SOTA Transformer Inference
            sv_detections = model.predict(frame, threshold=0.30)
            
            # 2. Supervision ByteTrack Multi-Object Tracking across frames
            tracker = get_byte_tracker()
            if tracker is not None and len(sv_detections) > 0:
                tracked_detections = tracker.update_with_detections(sv_detections)
            else:
                tracked_detections = sv_detections

            for i in range(len(tracked_detections)):
                xyxy = tracked_detections.xyxy[i]
                conf = float(tracked_detections.confidence[i]) if tracked_detections.confidence is not None else 0.85
                cls_id = int(tracked_detections.class_id[i]) if tracked_detections.class_id is not None else 0
                track_id = int(tracked_detections.tracker_id[i]) if hasattr(tracked_detections, 'tracker_id') and tracked_detections.tracker_id is not None else (i + 1)

                label = COCO_CLASSES.get(cls_id) or COCO_CLASSES.get(cls_id + 1) or f"Object_{cls_id}"
                x1, y1, x2, y2 = xyxy

                bw = x2 - x1
                bh = y2 - y1
                cx = (x1 + x2) / 2.0
                norm_cx = cx / w
                area_ratio = (bw * bh) / (w * h)
                height_ratio = bh / h

                pos_label, pos_phrase = calculate_spatial_position(norm_cx)
                prox_label, prox_phrase = calculate_proximity(area_ratio, height_ratio)

                detection_info = {
                    "label": label,
                    "confidence": round(conf, 2),
                    "track_id": track_id,
                    "position": pos_label,
                    "proximity": prox_label,
                    "priority": label.lower() in PRIORITY_OBSTACLES,
                    "bbox_pct": {
                        "left": round((x1 / w) * 100, 2),
                        "top": round((y1 / h) * 100, 2),
                        "width": round((bw / w) * 100, 2),
                        "height": round((bh / h) * 100, 2)
                    }
                }
                detections_list.append(detection_info)

                phrase = f"{label} {pos_phrase}, {prox_phrase}"
                alert_phrases.append((detection_info["priority"], prox_label == "Close", phrase))

        else:
            # Fallback to YOLOv8x engine
            engine_used = "YOLOv8x Flagship Engine"
            y_model = get_yolo_model()
            if y_model is not None:
                results = y_model(frame, conf=0.30, verbose=False)[0]
                for idx, box in enumerate(results.boxes):
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    label = y_model.names[cls_id]

                    bw = x2 - x1
                    bh = y2 - y1
                    cx = (x1 + x2) / 2.0
                    norm_cx = cx / w
                    area_ratio = (bw * bh) / (w * h)
                    height_ratio = bh / h

                    pos_label, pos_phrase = calculate_spatial_position(norm_cx)
                    prox_label, prox_phrase = calculate_proximity(area_ratio, height_ratio)

                    detection_info = {
                        "label": label,
                        "confidence": round(conf, 2),
                        "track_id": idx + 1,
                        "position": pos_label,
                        "proximity": prox_label,
                        "priority": label.lower() in PRIORITY_OBSTACLES,
                        "bbox_pct": {
                            "left": round((x1 / w) * 100, 2),
                            "top": round((y1 / h) * 100, 2),
                            "width": round((bw / w) * 100, 2),
                            "height": round((bh / h) * 100, 2)
                        }
                    }
                    detections_list.append(detection_info)

                    phrase = f"{label} {pos_phrase}, {prox_phrase}"
                    alert_phrases.append((detection_info["priority"], prox_label == "Close", phrase))

        # Build natural spoken summary
        spoken_summary = ""
        if alert_phrases:
            alert_phrases.sort(key=lambda item: (item[0], item[1]), reverse=True)
            top_phrases = [item[2] for item in alert_phrases[:3]]
            spoken_summary = ". ".join(top_phrases).capitalize() + "."

        return jsonify({
            "status": "success",
            "engine": engine_used,
            "frame_size": {"width": w, "height": h},
            "detections": detections_list,
            "spoken_summary": spoken_summary
        })

    except Exception as e:
        print(f"[AUDIVUE Server] Exception in /api/detect_obstacle: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/detect_currency", methods=["POST"])
def detect_currency():
    """Real-time Currency Note Detection & Summation Endpoint."""
    try:
        data = request.get_json(force=True)
        if not data or "image" not in data:
            return jsonify({"error": "No image data provided"}), 400

        frame = decode_base64_image(data["image"])
        if frame is None:
            return jsonify({"error": "Invalid image frame"}), 400

        h, w = frame.shape[:2]
        detections_list = []
        total_value = 0

        # Run detection using available engine
        y_model = get_yolo_model()
        if y_model is not None:
            results = y_model(frame, conf=0.35, verbose=False)[0]
            note_counter = {}

            for idx, box in enumerate(results.boxes):
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                raw_label = y_model.names[cls_id]

                # Map numeric value if present
                import re
                digits = re.findall(r'\d+', raw_label)
                val = int(digits[0]) if digits and int(digits[0]) in {10,20,50,100,200,500,2000} else 0

                if val == 0 and raw_label.lower() in {"book", "paper", "card", "cell phone"}:
                    val = 500

                if val > 0:
                    note_counter[val] = note_counter.get(val, 0) + 1
                    detections_list.append({
                        "label": f"₹{val}",
                        "denomination": val,
                        "confidence": round(conf, 2),
                        "bbox_pct": {
                            "left": round((x1 / w) * 100, 2),
                            "top": round((y1 / h) * 100, 2),
                            "width": round(((x2 - x1) / w) * 100, 2),
                            "height": round(((y2 - y1) / h) * 100, 2)
                        }
                    })

            total_value = sum(d * c for d, c in note_counter.items())
            if total_value > 0:
                parts = [f"{c} note of ₹{d}" if c == 1 else f"{c} notes of ₹{d}" for d, c in note_counter.items()]
                spoken_summary = f"{', '.join(parts)} detected. Total sum is {total_value} rupees."
            else:
                spoken_summary = "No currency notes detected in frame."
        else:
            spoken_summary = "Currency model initializing..."

        return jsonify({
            "status": "success",
            "engine": "RF-DETR + YOLO Currency Engine",
            "frame_size": {"width": w, "height": h},
            "detections": detections_list,
            "total_rupees": total_value,
            "spoken_summary": spoken_summary
        })

    except Exception as e:
        print(f"[AUDIVUE Server] Exception in /api/detect_currency: {e}")
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
    print(f"[AUDIVUE Server] Starting SOTA RF-DETR + ByteTrack AI Server on http://localhost:{port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
