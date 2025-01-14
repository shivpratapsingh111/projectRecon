from app.api import file_get_all
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.services.manage_scan import start_scan
from app.interface.process_manager import DomainCommandManager
from fastapi import WebSocket, WebSocketDisconnect
import json

router = APIRouter()
manager = DomainCommandManager()

@router.get("/web", tags=["start-operation-web"])
async def web():
    return {"message": "Need input"}

@router.get("/get-status/{groupName}")
async def get_status1(groupName: str):
    try:
        result = manager.command_monitor(groupName)
        return {f"status of {groupName}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.websocket("/ws/get-all")
async def websocket_get_all(websocket: WebSocket):
    try:
        await websocket.accept()  # Accept the WebSocket connection
        while True:
            result = manager.get_all_data()  # Get your data
            # Convert result to JSON string before sending
            await websocket.send_text(json.dumps(result))  # Send the result over the WebSocket
            await asyncio.sleep(1)  # Add a small delay between updates
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()


@router.post("/process-scan")
async def process_scan(
    domain: Union[str, None] = Form(None),
    groupName: Union[str, None] = Form(None),
    file: Union[UploadFile, None] = None,
    scanOptions: Union[str, None] = Form(None),  # JSON string of selected scan options
):
    """
    Processes the request to extract scan names and domains.
    - `domain`: A comma-separated list of domains from a text input.
    - `file`: A file containing one domain per line.
    - `scanOptions`: A JSON string containing selected scan options.
    """

    # Parse scan options
    try:
        if scanOptions:
            scan_names = json.loads(scanOptions)
        else:
            scan_names = []
    except json.JSONDecodeError:
        return JSONResponse(
            content={"error": "Invalid format for scanOptions."},
            status_code=400,
        )

    # Validate at least one scan option is selected
    if not scan_names:
        return JSONResponse(
            content={"error": "No scan options provided."},
            status_code=400,
        )

    # Initialize the domains list
    domains = []

    # Process domains from the "domain" input field
    if domain:
        domains += [d.strip() for d in domain.split(",") if d.strip()]

    # Process domains from the uploaded file
    if file:
        file_content = (await file.read()).decode("utf-8")
        domains += [line.strip() for line in file_content.splitlines() if line.strip()]

    # If no domains are provided, return an error
    if not domains:
        return JSONResponse(
            content={"error": "No domains provided. Use either 'domain' or 'file'."},
            status_code=400,
        )

    # Print for debugging purposes
    print(groupName, domains, scan_names)

    # Create async task for scanning
    asyncio.create_task(asyncio.to_thread(start_scan, groupName, domains, scan_names))

    return {
        "groupName": groupName,
        "scanNames": scan_names,
        "domains": domains,
    }

@router.get("/stop-all/{groupName}")
async def stop_all(groupName: str):
    try:
        # log_dir=f"{root_Data_Dir}/{groupName}"
        result = manager.stop_processes(groupName)
        return {f"status of {groupName}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# @router.get("/stop-domain/{domain_name}")
# async def stop_domain(domain_name: str):
#     result = stop_domain_processes(domain_name)
#     return {f"status": result}

# @router.get("/get-status2/{command_name}")
# async def get_status2(command_name: str):
    
#     return {"status": monitor_command(command_name)}