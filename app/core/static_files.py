import os
from fastapi.staticfiles import StaticFiles

def mount_static(app):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.normpath(os.path.join(current_dir, "..", "static"))
    print(f"📂 Mounting static files from: {static_path}")
    app.mount("/static", StaticFiles(directory=static_path), name="static")
