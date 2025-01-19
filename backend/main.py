from app.api import file_get_all, web
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.db.db_manager import DatabaseManager
from app.api.mail_reports import report
from backend.app.api.add import handle_add
from backend.app.api.monitor_endpoints import handle_monitor

from app.config.db_config import db_config

db_manager = DatabaseManager(db_config) # Just to create DB and tables, if doesn't exists

app = FastAPI()
router = APIRouter()

# Allow all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint to check service status."""

    return {"message": "Yeah! Running"}




app.include_router(web.router, prefix="/scan", tags=["Scanning"])
app.include_router(handle_add.router, prefix="/add", tags=["Add"])
app.include_router(report.router, tags=["Report"])
app.include_router(handle_monitor.router, prefix="/monitor", tags=["Endpoint Monitor"])



    # # CURL Request Example:
# # curl -X POST "http://127.0.0.1:8000/input-box" \
# #      -H "Content-Type: application/json" \
# #      -d '{"data": ["example1", "example2", "example3"]}'

# main.py
# from fastapi import FastAPI, UploadFile, File, HTTPException

# app = FastAPI()

# @app.post("/upload-file")
# async def upload_file(file: UploadFile = File(...)):
#     """
#     Accepts a single file upload using request body.
#     """
#     if not file:
#         raise HTTPException(status_code=400, detail="No file provided.")
#     content = await file.read()
#     return {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "size": len(content),
#     }

