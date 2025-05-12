from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.db.db_manager import DatabaseManager
from app.api.mail_reports import handler_report
from app.api.add import handler_add
from app.api.monitor_endpoints import handler_monitor
from app.api.results import handler_results
from app.api.summary import handler_summary
from app.api.terminal import handler_terminal

from app.config.db_config import db_config
from app.api.scan import handler_scan

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


app.include_router(handler_scan.router, prefix="/scan", tags=["Start New Scan"])
app.include_router(handler_add.router, prefix="/add", tags=["Add New Targets"])
app.include_router(handler_report.router, tags=["Report With Automation"])
app.include_router(handler_monitor.router, prefix="/monitor", tags=["Monitor Endpoints"])
app.include_router(handler_results.router, prefix="/results", tags=["Get Results Of Preivous Scans"])
app.include_router(handler_summary.router, prefix="/summary", tags=["Get Summary (total subdomains, etc) From Database"])
app.include_router(handler_terminal.router, prefix="/terminal", tags=["Access Terminal"])
