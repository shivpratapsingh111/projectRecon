from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.interface.process_manager import DomainCommandManager
import json
import logging
import shutil

from app.services.monitor_endpoints.monitor import monitor_endpoints

router = APIRouter()
manager = DomainCommandManager()

@router.get("")
async def monitor():
    return {"message": "Yeah! Running"}

@router.post("/new")
async def create_new_scan(
    endpoint: Union[List[str], None] = Form([]), 
    scan_name: Union[str, None] = Form(None),
    file: Union[UploadFile, None] = None,
    scan_options: Union[str, None] = Form(None),  # JSON string of selected scan options
):
    try:
        if scan_name is None:
            raise HTTPException(status_code=400, detail="Scan name not provided.")
        
        if not endpoint and not file:
            raise HTTPException(status_code=400, detail="Provide either an endpoint or a file.")
        
        if endpoint and file:
            raise HTTPException(status_code=400, detail="Provide either an endpoint or a file at a time.")

        # Parse scan_options if provided
        if scan_options:
            try:
                scan_options = json.loads(scan_options)
            except json.JSONDecodeError:
                return JSONResponse(content={"error": "Invalid format for scanOptions."}, status_code=400)

        # Process endpoint input
        if endpoint:
            asyncio.create_task(monitor_endpoints(endpoint, scan_name))

        # Process file input
        if file:
            scan_dir = f"{root_Data_Dir}/monitoring/{scan_name}"
            file_location = f"{scan_dir}/{file.filename}"
            os.makedirs(scan_dir, exist_ok=True)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open(file_location, "r") as file_content:
                endpoints_from_file = [line.strip() for line in file_content.readlines() if line.strip()]
            print(endpoints_from_file)
            asyncio.create_task(monitor_endpoints(endpoints_from_file, scan_name))
            
        return JSONResponse(content={"message": "Scan started"}, status_code=200)

    except Exception as e:
        error = logging.exception("Error")
        return {JSONResponse(content={"error": error}, status_code=500)}
        # return JSONResponse(content={"error": str(e)}, status_code=500)

    # asyncio.create_task(asyncio.to_thread(start_scan, groupName, domains, scan_options))
    # return {
    #     "Scan Name": scan_name,
    #     "Scan Options": scan_options,
    #     "endpoint": endpoint,
    # }
