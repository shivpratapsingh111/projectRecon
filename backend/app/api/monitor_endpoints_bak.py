from app.api import file_get_all
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.interface.process_manager import DomainCommandManager
import json

router = APIRouter()
manager = DomainCommandManager()


@router.post("/create")
async def report(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    options: str = Form("{}")
):
    try:
        if not url and not file:
            raise HTTPException(status_code=400, detail="Provide either a URL or a file.")
        
        if url and file:
            raise HTTPException(status_code=400, detail="Provide either a URL or a file at a time")
        
        monitor_options = json.loads(options)
        
        response_data = {"success": True, "message": "Report received successfully!"}

        if url:
            response_data["url"] = url

        if file:
            file_content = await file.read()  # Read file content
            response_data["file_name"] = file.filename
            response_data["file_size"] = len(file_content)
            

        response_data["options"] = monitor_options
        
        return JSONResponse(content=response_data, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)
