from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import pandas as pd
from ultralytics import YOLO
from googleapiclient.discovery import build
from google.oauth2 import service_account
import datetime
from dotenv import load_dotenv
import openai
from pydantic import BaseModel
import imghdr  # ✅ Added for file type validation
from app.utils.calendar_utils import is_time_slot_available


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")  # ✅ Added for API key authentication

if not OPENAI_API_KEY:
    raise ValueError("\u274c OpenAI API Key not found! Please add it to .env.")

if not API_SECRET_KEY:
    raise ValueError("\u274c API_SECRET_KEY not found! Please add it to .env.")

# ✅ Debugging API Key Loading
print(f"🔑 Loaded API Key from .env: {API_SECRET_KEY}")  # ✅ Debugging log

# Initialize FastAPI app
app = FastAPI()

# ✅ Authentication Dependency
def check_api_key(x_api_key: str = Header(None)):
    print(f"🔍 Received API Key: {x_api_key}")  # ✅ Debugging log
    if x_api_key is None:
        raise HTTPException(status_code=403, detail="❌ Missing API key.")
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="❌ Invalid API key.")

# Serve Static Files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_home():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    print(f"🔍 Checking file: {file_path}")  # ✅ Debugging statement added
    if os.path.exists(file_path):
        print("✅ index.html found, returning file")  # ✅ Debugging log
        return FileResponse(file_path)
    print("❌ index.html not found!")  # ✅ Debugging log
    return {"detail": "index.html not found"}

# Load YOLOv8 model
MODEL_PATH = os.getenv("MODEL_PATH")
if MODEL_PATH and os.path.exists(MODEL_PATH):
    print(f"📌 Attempting to load YOLO model from: {MODEL_PATH}")  # ✅ Debugging log
    try:
        model = YOLO(MODEL_PATH)
        print("✅ YOLO Model Loaded Successfully!")  # ✅ Debugging log
    except Exception as e:
        raise ValueError(f"❌ Error loading YOLO model: {e}")
else:
    raise ValueError(f"❌ ERROR: YOLO model file not found at {MODEL_PATH}. Check your .env settings!")

# Load AI classifier model & labels
CLASSIFIER_MODEL_PATH = os.getenv("CLASSIFIER_MODEL_PATH", "tattoo_classifier.pth")
LABELS_FILE = "tattoo_labels.csv"

if not CLASSIFIER_MODEL_PATH or not os.path.exists(CLASSIFIER_MODEL_PATH):
    raise ValueError("❌ ERROR: Classifier model file not found. Check CLASSIFIER_MODEL_PATH in .env.")

if os.path.exists(LABELS_FILE):
    labels_df = pd.read_csv(LABELS_FILE)
    class_names = labels_df["tattoo_style"].tolist()
    complexity_mapping = dict(zip(labels_df["tattoo_style"], labels_df["complexity_level"]))
    print("✅ Tattoo labels loaded successfully.")
else:
    raise ValueError("Error: LABELS_FILE (tattoo_labels.csv) not found!")

# Load classifier model (Ensuring it supports 3 classes)
classifier_model = models.efficientnet_b0(weights=None)
num_ftrs = classifier_model.classifier[1].in_features
classifier_model.classifier = torch.nn.Sequential(
    torch.nn.Linear(num_ftrs, 256),
    torch.nn.ReLU(),
    torch.nn.Linear(256, 3)  # Model is trained with exactly 3 classes
)
classifier_model.load_state_dict(torch.load(CLASSIFIER_MODEL_PATH, map_location=torch.device('cpu')))
classifier_model.eval()
print("✅ Classifier model loaded successfully (3 classes).")

# ✅ Define file validation settings
ALLOWED_IMAGE_TYPES = {"jpeg", "png", "jpg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Preprocessing function
def preprocess_image(image):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return transform(image).unsqueeze(0)

# Function to estimate price & time dynamically based on tattoo size & complexity
def estimate_price_and_time(bounding_box, complexity_level):
    x_min, y_min, x_max, y_max = map(int, bounding_box)
    tattoo_area = (x_max - x_min) * (y_max - y_min)
    
    # Normalize based on a standard reference image size (640x480)
    normalized_area = tattoo_area / (640 * 480)
    
    # Complexity multipliers
    complexity_multiplier = {"simple": 1, "medium": 2, "complex": 3}
    
    # Base price and time
    base_price = 50  # Minimum price in USD
    base_time = 1.5  # Minimum time in hours
    
    # Adjust price and time based on area & complexity
    estimated_price = base_price * normalized_area * complexity_multiplier.get(complexity_level, 1)
    estimated_time = base_time * normalized_area * complexity_multiplier.get(complexity_level, 1)
    
    return round(max(estimated_time, 1), 2), round(max(estimated_price, 50), 2)

# Google Calendar API Setup
def create_calendar_event(session_time, user_selected_datetime):
    try:
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
            return {"error": "Google Calendar credentials file missing or incorrect path."}

        if not CALENDAR_ID:
            return {"error": "Google Calendar ID missing from environment variables."}

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        start_time = datetime.datetime.fromisoformat(user_selected_datetime)
        end_time = start_time + datetime.timedelta(hours=session_time)

        event = {
            "summary": "Tattoo Appointment",
            "description": f"Tattoo session estimated for {session_time} hours.",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        }

        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        return {
            "event_id": event.get("id"),  # ✅ Store the correct event ID
            "booking_link": event.get("htmlLink")
        }

    except Exception as e:
        error_message = f"❌ Error Creating Calendar Event: {e}"
        print(error_message)
        return {"error": error_message}

# ✅ NEW FUNCTION ADDED TO CANCEL APPOINTMENTS
@app.post("/cancel_booking/")
async def cancel_booking(event_id: str = Form(...), api_key: str = Depends(check_api_key)):
    try:
        SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS")
        CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

        if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
            return JSONResponse(status_code=500, content={"error": "Google Calendar credentials file missing or incorrect path."})

        if not CALENDAR_ID:
            return JSONResponse(status_code=500, content={"error": "Google Calendar ID missing from environment variables."})

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=credentials)

        try:
            service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
            return {"status": "success", "message": "Appointment canceled successfully."}

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Failed to cancel appointment: {str(e)}"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected Error: {str(e)}"})


# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat/")
async def chat(request: ChatRequest, api_key: str = Depends(check_api_key)):
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    print(f"📩 User Message: {user_message}")  # ✅ Debugging log

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use "gpt-4o" for latest OpenAI model
            messages=[
                {"role": "system", "content": "You are an AI assistant for a tattoo booking system. Answer user queries about tattoo styles, pricing, and booking."},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content
        print(f"🤖 Bot Reply: {bot_reply}")  # ✅ Debugging log
        return {"reply": bot_reply}

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"OpenAI Error: {str(e)}"})
