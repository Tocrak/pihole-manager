import sys
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger("app")
from routers.client_group import router as client_group_router

app = FastAPI(title="Pi-Hole Administration Proxy")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(client_group_router)

@app.get("/", response_class=HTMLResponse)
async def website():
    """Serves the static index file for the web interface."""
    return FileResponse("static/index.html")

@app.get("/reboot")
async def reboot():
    """Immediately exits the application (for containerized restarts)."""
    print("[INFO] Reboot endpoint hit. Exiting.")
    sys.exit(0)
