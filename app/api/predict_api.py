from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
import io
import numpy as np
import cv2
from PIL import Image
import imghdr
import torch
import base64
from app.utils.calendar_utils import is_time_slot_available  # Import availability check function

# ✅ Proper modular imports
from app.models.yolo_model import load_yolo_model
from app.models.classifier import load_classifier_model
from app.models.labels import load_tattoo_labels
from app.services.preprocessing import preprocess_image
from app.services.pricing import estimate_price_and_time
from app.services.calendar_integration import create_calendar_event
from app.core.auth import check_api_key

# ✅ Load YOLO and classifier models
model = load_yolo_model()
classifier_model = load_classifier_model()
class_names, complexity_mapping = load_tattoo_labels()

# ✅ Constants for image validation
ALLOWED_IMAGE_TYPES = {"jpeg", "png", "jpg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


from app.services.session_duration import estimate_duration

# ✅ Create a router for the predict API
router = APIRouter()

@router.post("/predict/")
async def predict(file: UploadFile = File(...), bookingDateTime: str = Form(...), api_key: str = Depends(check_api_key)):
    print("🧪 Received bookingDateTime:", bookingDateTime)
    print("🧪 Received file filename:", file.filename)
    try:
        # ✅ Step 1: Check if the time slot is available before proceeding
        session_time = 1.5  # Default session time, modify as needed
        availability = is_time_slot_available(bookingDateTime, session_time)

        if isinstance(availability, dict) and "error" in availability:
            return JSONResponse(status_code=500, content={"status": "error", "message": availability["error"]})

        if not availability:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Selected time slot is already booked. Please choose a different time."})

        # ✅ Step 2: Validate file type
        print("🧪 Checking image format...")
        file_ext = imghdr.what(file.file)
        print("🧪 Detected format:", file_ext)
        if file_ext not in ALLOWED_IMAGE_TYPES:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid image format. Allowed formats: JPEG, PNG, JPG."})

        # ✅ Step 3: Validate file size
        print("🧪 Checking file size...")
        file.file.seek(0, 2)
        file_size = file.file.tell()
        print("🧪 Detected file size:", file_size)
        file.file.seek(0)
        if file_size > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"status": "error", "message": "File too large. Maximum allowed size is 5MB."})

        image_bytes = await file.read()
        try:
            image = Image.open(io.BytesIO(image_bytes))
        except Exception:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Invalid image file."})

        img_cv = np.array(image)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        print("🧪 Image dimensions:", img_cv.shape)
        
        # ✅ Ensure image meets minimum size requirements before YOLO processing
        min_size = 100
        h, w, _ = img_cv.shape
        if h < min_size or w < min_size:
            return JSONResponse(status_code=400, content={"status": "error", "message": "Image too small for detection. Please upload a larger image."})

        # ✅ Resize image before processing to speed up inference
        max_width, max_height = 800, 800
        if h > max_height or w > max_width:
            scale = min(max_width / w, max_height / h)
            img_cv = cv2.resize(img_cv, (int(w * scale), int(h * scale)))

        results = model(img_cv)
        print("✅ YOLO inference complete.")
        print(f"📦 Raw results object: {results}")
        if not results or not hasattr(results[0], 'boxes') or len(results[0].boxes) == 0:
            print("❌ No bounding boxes found.")
            return {
                "status": "success",
                "detections": [],
                "message": "No tattoos detected."
            }
        detections = []

        for r in results:
            for box in r.boxes:
                x_min, y_min, x_max, y_max = map(int, box.xyxy[0].tolist())
                confidence = box.conf.item()

                # ✅ Draw Bounding Boxes
                cv2.rectangle(img_cv, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
                cv2.putText(img_cv, f"{confidence:.2f}", (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                image_tensor = preprocess_image(image)

                with torch.no_grad():
                    outputs = classifier_model(image_tensor)
                    _, predicted_class = torch.max(outputs, 1)

                tattoo_style = class_names[predicted_class.item()] if predicted_class.item() < len(class_names) else "Unknown"
                complexity_level = complexity_mapping.get(tattoo_style, "Unknown")

                price_time, price = estimate_price_and_time((x_min, y_min, x_max, y_max), complexity_level)
                session_time = estimate_duration(tattoo_style, complexity_level)
                booking_data = create_calendar_event(session_time, bookingDateTime)

                detections.append({
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    "confidence": confidence,
                    "tattoo_style": tattoo_style,
                    "complexity_level": complexity_level,
                    "estimated_time_hours": session_time,
                    "estimated_price_usd": price,
                    "event_id": booking_data.get("event_id", ""),
                    "booking_link": booking_data.get("booking_link", "Error creating event")
                })

        if not detections:
            return {"status": "success", "detections": [], "message": "No tattoos detected."}

        _, buffer = cv2.imencode(".jpg", img_cv)
        image_base64 = base64.b64encode(buffer).decode()

        return {
            "status": "success",
            "detections": detections,
            "image_base64": f"data:image/jpeg;base64,{image_base64}"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": "Internal server error."})

# ✅ Register this router in `main.py` using `app.include_router(router)`
