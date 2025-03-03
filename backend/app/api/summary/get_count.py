import asyncio
from app.interface.process_manager import CommandExecutor
import json
import os
from app.config.config import *
from app.logger.logger import setup_logger
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pathlib import Path


logger = setup_logger(__name__, log_file_path='results', enable_debug=True)
manager = CommandExecutor()


async def read_file(file_path: Path, limit: Optional[int] = None, offset: int = 0) -> dict:
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    try:
        with file_path.open('r') as file:
            lines = [line.strip() for line in file]
            
            total_lines = len(lines)

        return {
            "total_lines": total_lines
        }
    except Exception as e:
        logger.exception(f"Error reading file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error reading file")
