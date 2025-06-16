# External imports
from fastapi import UploadFile, Form, status
from fastapi.responses import JSONResponse
from typing import Literal, Optional
import asyncio, traceback

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)

# WRITE PYTHON CODE TO CHECK IF EACH REQUIRED UTILITY AND TOOL IS INSTALLED 