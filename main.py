"""
AUDIVUE FastAPI + WebSocket Real-Time AI Server
Tech Stack:
  - Framework: FastAPI + Uvicorn (Async ASGI Server)
  - Transport: Low-Latency Binary WebSocket Streaming (/ws/detect)
  - CV Model: Ultralytics YOLO11 (PyTorch) + OpenCV
  - Telemetry: Spatial Quadrants + Distance Proximity + Currency Summation
"""

import os
import sys
import asyncio
import base64
import time
import numpy as np
import cv2
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from ultralytics import YOLO

# Add extracted repository directory to Python path if available
REPO_PATH = r"C:\Users\akhil\.gemini\antigravity\brain\e4335997-9af7-4948-bc15-7ace823b9052\scratch\ai-vision"
if REPO_PATH not in sys.path:
    sys.path.insert(0, REPO_PATH)

app = FastAPI(title="AUDIVUE AI Vision & Currency Engine", version="2.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global YOLO11 PyTorch Model Instance
yolo11_model = None

def get_yolo11_model():
    global yolo11_model
    if yolo11_model is None:
        print("[AUDIVUE FastAPI] Loading Ultralytics YOLO11 Model...")
        try:
            yolo11_model = YOLO("yolo11x.pt")
            print("[AUDIVUE FastAPI] YOLO11x (PyTorch) loaded successfully!")
        except Exception as e:
            print(f"[AUDIVUE FastAPI] Fallback loading yolo11n.pt ({e})...")
            yolo11_model = YOLO("yolo11n.pt")
    return yolo11_model

# Constants for Spatial Telemetry
ZONE_LEFT_MAX = 0.38
ZONE_RIGHT_MIN = 0.62
AREA_NEAR_THRESH = 0.12
AREA_MEDIUM_THRESH = 0.03
PRIORITY_OBSTACLES = {"person", "chair", "table", "door", "couch", "car", "bicycle", "stairs", "pole", "bottle"}


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


def process_frame_sync(frame: np.ndarray, mode: str = "obstacle") -> Dict:
    """
    Synchronous execution of YOLO11 inference on frame.
    Called off the main async event loop via asyncio.to_thread.
    """
    h, w = frame.shape[:2]
    model = get_yolo11_model()
    conf_thresh = 0.30 if mode == "obstacle" else 0.35
    
    results = model(frame, conf=conf_thresh, verbose=False)[0]
    detections_list = []
    alert_phrases = []
    total_currency = 0
    note_counter = {}

    for idx, box in enumerate(results.boxes):
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0].cpu().numpy())
        cls_id = int(box.cls[0].cpu().numpy())
        raw_label = model.names[cls_id]

        bw = x2 - x1
        bh = y2 - y1
        cx = (x1 + x2) / 2.0
        norm_cx = cx / w
        area_ratio = (bw * bh) / (w * h)
        height_ratio = bh / h

        pos_label, pos_phrase = calculate_spatial_position(norm_cx)
        prox_label, prox_phrase = calculate_proximity(area_ratio, height_ratio)

        # Parse denomination if in currency mode
        import re
        digits = re.findall(r'\d+', raw_label)
        val = int(digits[0]) if digits and int(digits[0]) in {10,20,50,100,200,500,2000} else 0
        if val == 0 and raw_label.lower() in {"book", "paper", "card", "cell phone"}:
            val = 500

        if mode == "currency" and val > 0:
            note_counter[val] = note_counter.get(val, 0) + 1
            total_currency += val

        det_info = {
            "label": f"₹{val}" if mode == "currency" and val > 0 else raw_label,
            "confidence": round(conf, 2),
            "track_id": idx + 1,
            "position": pos_label,
            "proximity": prox_label,
            "priority": raw_label.lower() in PRIORITY_OBSTACLES,
            "bbox_pct": {
                "left": round((x1 / w) * 100, 2),
                "top": round((y1 / h) * 100, 2),
                "width": round((bw / w) * 100, 2),
                "height": round((bh / h) * 100, 2)
            }
        }
        detections_list.append(det_info)
        phrase = f"{raw_label} {pos_phrase}, {prox_phrase}"
        alert_phrases.append((det_info["priority"], prox_label == "Close", phrase))

    spoken_summary = ""
    if mode == "obstacle" and alert_phrases:
        alert_phrases.sort(key=lambda item: (item[0], item[1]), reverse=True)
        top_phrases = [item[2] for item in alert_phrases[:3]]
        spoken_summary = ". ".join(top_phrases).capitalize() + "."
    elif mode == "currency":
        if total_currency > 0:
            parts = [f"{c} note of ₹{d}" if c == 1 else f"{c} notes of ₹{d}" for d, c in note_counter.items()]
            spoken_summary = f"{', '.join(parts)} detected. Total sum is {total_currency} rupees."
        else:
            spoken_summary = "Scan currency notes."

    return {
        "status": "success",
        "engine": "FastAPI + YOLO11 (PyTorch)",
        "frame_size": {"width": w, "height": h},
        "detections": detections_list,
        "total_rupees": total_currency,
        "spoken_summary": spoken_summary
    }


# ==========================================
# REAL-TIME LOW-LATENCY WEBSOCKET ENDPOINT
# ==========================================
@app.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    """
    High-speed binary WebSocket endpoint for real-time camera streaming.
    Receives binary JPEG frame bytes from browser canvas, runs YOLO11 off thread,
    and returns detection JSON back to canvas in milliseconds.
    """
    await websocket.accept()
    print("[FastAPI WebSocket] Client connected to live stream.")

    try:
        while True:
            # Receive binary JPEG bytes or JSON message
            message = await websocket.receive()
            
            if "bytes" in message and message["bytes"]:
                jpeg_bytes = message["bytes"]
                frame = cv2.imdecode(np.frombuffer(jpeg_bytes, np.uint8), cv2.IMREAD_COLOR)
            elif "text" in message and message["text"]:
                import json
                payload = json.loads(message["text"])
                b64_str = payload.get("image", "")
                if "," in b64_str:
                    b64_str = b64_str.split(",")[1]
                frame = cv2.imdecode(np.frombuffer(base64.b64decode(b64_str), np.uint8), cv2.IMREAD_COLOR)
            else:
                continue

            if frame is None:
                continue

            # Run YOLO11 inference off the main event loop
            results = await asyncio.to_thread(process_frame_sync, frame, "obstacle")
            await websocket.send_json(results)

    except WebSocketDisconnect:
        print("[FastAPI WebSocket] Client disconnected.")
    except Exception as e:
        print(f"[FastAPI WebSocket] Error: {e}")


# ==========================================
# REST API FALLBACK ENDPOINTS
# ==========================================
@app.post("/api/detect_obstacle")
async def api_detect_obstacle(data: dict):
    b64_str = data.get("image", "")
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    frame = cv2.imdecode(np.frombuffer(base64.b64decode(b64_str), np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    results = await asyncio.to_thread(process_frame_sync, frame, "obstacle")
    return JSONResponse(content=results)


@app.post("/api/detect_currency")
async def api_detect_currency(data: dict):
    b64_str = data.get("image", "")
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    frame = cv2.imdecode(np.frombuffer(base64.b64decode(b64_str), np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    results = await asyncio.to_thread(process_frame_sync, frame, "currency")
    return JSONResponse(content=results)


# ==========================================
# STATIC FILES & SINGLE ENTRY POINT ROUTING
# ==========================================
@app.get("/")
async def serve_index():
    return FileResponse("html/index.html")

@app.get("/{path:path}")
async def serve_static_files(path: str):
    if os.path.exists(path):
        return FileResponse(path)
    html_path = os.path.join("html", path)
    if os.path.exists(html_path):
        return FileResponse(html_path)
    raise HTTPException(status_code=404, detail="Not Found")


if __name__ == "__main__":
    import uvicorn
    print("[AUDIVUE FastAPI] Starting Uvicorn ASGI server on http://localhost:8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
