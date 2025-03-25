from fastapi import FastAPI

# Load configs
from app.core.config import (
    OPENAI_API_KEY,
    API_SECRET_KEY,
    MODEL_PATH,
    CLASSIFIER_MODEL_PATH,
    GOOGLE_CALENDAR_CREDENTIALS,
    GOOGLE_CALENDAR_ID,
)

# Load core helpers
from app.core.auth import check_api_key
from app.core.static_files import mount_static
from app.core.templates import templates

# Load models
from app.models.yolo_model import load_yolo_model
from app.models.classifier import load_classifier_model
from app.models.labels import load_tattoo_labels

# Load utilities
from app.services.preprocessing import preprocess_image
from app.services.pricing import estimate_price_and_time
from app.services.calendar_integration import create_calendar_event

# Initialize app
app = FastAPI()

# Mount /static folder
mount_static(app)

# Templates setup
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

# Load AI models and label data
model = load_yolo_model()
classifier_model = load_classifier_model()
class_names, complexity_mapping = load_tattoo_labels()

# Include routers
from app.routes.home import router as home_router
from app.routes.chat import router as chat_router
from app.routes.cancel_booking import router as cancel_router
from app.api.predict_api import router as predict_router
from app.api.availability_api import router as availability_router
from app.api.admin_api import router as admin_router

app.include_router(home_router)
app.include_router(chat_router)
app.include_router(cancel_router)
app.include_router(predict_router)
app.include_router(availability_router)
app.include_router(admin_router)
