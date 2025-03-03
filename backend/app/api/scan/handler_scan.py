from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.interface.process_manager import CommandExecutor
from fastapi import WebSocket, WebSocketDisconnect
import json

from app.config.db_config import db_config
from app.api.scan.new_scan import new_scan
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.api.scan.scan_db_manager import get_existing_programnames

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)


db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

router = APIRouter()
manager = CommandExecutor()

@router.get("/web", tags=["start-operation-web"])
async def web():
    return {"message": "Need input"}

@router.websocket("/ws/get-all")
async def websocket_get_all(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            result = manager.get_all_data()  
            await websocket.send_text(json.dumps(result)) 
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()

        
@router.get("/get-all")
async def api_get_all():
    try:
        result = manager.get_all_data()
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/get-existing-programnames")
async def api_get_existing_programnames():
    return await get_existing_programnames()

@router.post("/process-scan")
async def process_scan(
    domain: Union[str, None] = Form(None),
    groupName: Union[str, None] = Form(None),
    file: Union[UploadFile, None] = None,
    execution_style: Union[str, None] = Form("sequential"),
    scanOptions: Union[str, None] = Form(None),
):
    """
    Processes the request to extract scan names and domains.
    - `domain`: A comma-separated list of domains from a text input.
    - `file`: A file containing one domain per line.
    - `scanOptions`: A JSON string containing selected scan options.
    """
    return await new_scan(domain, groupName, file, execution_style, scanOptions)
    
@router.post("/stop/command/{process_id}")
async def stop_command_processes(process_id: str):
    try:
        result = manager.kill_process_by_pid(process_id, "single")
        return {f"status of {process_id}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/stop/domain/{group_id}/{domain_id}")
async def stop_domain_processes(group_id: str, domain_id: str):
    try:
        result = manager.kill_domain_processes(group_id, domain_id)
        return {f"status of domain {domain_id} of group {group_id}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/stop/group/{group_name}")
async def stop_group_processes(group_name: str):
    try:
        result = manager.kill_group_processes(group_name)
        return {f"status of {group_name}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
