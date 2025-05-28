# Tattoo Booking System (AI-Powered) 🎨🤖

An end-to-end tattoo booking and scheduling system powered by AI. This project integrates image recognition using YOLOv8, tattoo style classification with PyTorch, session duration & pricing estimation, and Google Calendar syncing — all wrapped in a FastAPI web backend.

---

## 🚀 Features

- **Tattoo Complexity Detection** (YOLOv8)
- **Tattoo Style Classification** (PyTorch-based CNN)
- **Session Duration & Pricing Estimator**
- **AI Chatbot** for User Queries
- **Admin & Customer Dashboards** (HTML + JS)
- **Google Calendar Integration**
- **Modular FastAPI Backend**
- Model training notebooks and scripts included

---

## 🗂️ Project Structure

```bash
tattoo-booking-system/
│
├── app/
│   ├── api/              # FastAPI route handlers
│   ├── core/             # Config, auth, static/templates loading
│   ├── models/           # Model wrappers (YOLO & classifier)
│   ├── routes/           # Frontend page routes
│   ├── services/         # Business logic: pricing, calendar, preprocessing
│   ├── static/           # JS, CSS, favicon
│   ├── templates/        # HTML templates
│   └── utils/            # Utility functions
│
├── data/                 # Sample/test data (JSON, CSV)
├── models/               # Pretrained model files (ignored in Git)
├── notebooks/            # Model training scripts
├── scripts/              # Utility & testing scripts
├── tests/                # Unit tests
├── main.py               # App entrypoint
├── .env.example          # Environment variable template
├── requirements.txt      # Python dependencies
└── README.md             # You're here :)
```

---

## 🧪 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/VibhavJaiswal/tattoo-booking-system.git
cd tattoo-booking-system
```

### 2. Setup virtual environment

```bash
python -m venv venv
venv\\Scripts\\activate     # On Windows
source venv/bin/activate  # On Linux/Mac
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add `.env` file

Create a `.env` file (you can start with `.env.example`) and add your API keys, model paths, and calendar credentials.

---

## 🤖 Model Files

Large model files are **not included** in this repository.

This project uses pretrained models:
- `best.pt` or `yolov8n.pt` (YOLOv8 from [Ultralytics](https://github.com/ultralytics/yolov5))
- `tattoo_classifier.pth` (a PyTorch classifier based on publicly available architectures)

⚠️ These models are used strictly for demonstration and educational purposes.

Please download them separately and place in the `/models/` folder. Do not redistribute.

---

## 🧠 How it works

- Upload an image
- YOLO detects tattoo complexity
- PyTorch classifies the style
- Pricing + session time estimated
- User can book appointment → auto-added to Google Calendar

---

## 📸 Screenshots

### 🔧 Admin Dashboard
This page shows the administrator's view with booking management, complexity insights, and session estimations.
![Admin Dashboard](screenshots/admin_dashboard.png)

---

### 🧑‍🎨 User Booking Page
This interface allows users to upload tattoo references, get AI-based estimates, and book appointments.
![User Booking Page](screenshots/user_booking.png)


---

## 📄 License

It is intended strictly for educational and portfolio demonstration purposes only.

No pretrained models are redistributed with this codebase. Users must acquire models from official sources and follow their respective licenses.

---

## 🙌 Author

**Vibhav Jaiswal**  
📧 mail.vibhav@gmail.com  
🌐 [GitHub Profile](https://github.com/VibhavJaiswal)

---

> Built for real-world learning and portfolio showcase. Feel free to fork or contribute!
