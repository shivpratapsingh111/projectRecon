from app.api import file_get_all
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from app.utils.validators import validate_tests
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.services.manage_scan import start_scan
from celery.result import AsyncResult
# from app.services.pyscripts.subdomains import monitor_command
from app.interface.process_manager import DomainCommandManager
# from app.interface.global_manager import initialize_manager, get_manager, stop_group_processes

router = APIRouter()

@router.get("/web", tags=["start-operation-web"])
async def web():
    return {"message": "Need input"}

@router.post("/web/list", tags=["Domain list input"])
async def get_domain_list(
    background_tasks: BackgroundTasks,
    domain_list: str = Form(...),
    group_name: str = Form(...),
    scan_list: str = Form(...)
):

    start_scan(group_name, domain_list, scan_list)
    
    return {"Message": "Scan started successfully", "Group Name": group_name,"Domains": domain_list, "Scans Selected": scan_list}



@router.post("/web/file", tags=["Domain list input"])
async def get_domain_file(
    file: UploadFile = File(...),  # Required file upload
    group_name: str = Form(...),  # Required text input
    scan_list: List[str] = Form(...)  # Optional additional field
):
    domain_list: List[str] = []
    try:
        contents = await file.read()
        domain_list = contents.decode("utf-8").splitlines()
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}
    finally:
        await file.close()  # Ensure the file is closed
    
    print(group_name, domain_list, scan_list)
    asyncio.create_task(asyncio.to_thread(start_scan, group_name, domain_list, scan_list))
    time.sleep(2)
    manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{group_name}")
    # result = manager.command_monitor(group_name)
    return {"Group name": group_name,"Domains": domain_list, "Scans Selected": scan_list, "Status": "running"} 
    # return result
 

@router.get("/get-status/{group_name}")
async def get_status1(group_name: str):
    try:
        manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{group_name}")
        result = manager.command_monitor(group_name)
        return {f"status of {group_name}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stop-all/{group_name}")
async def stop_all(group_name: str):
    try:
        manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{group_name}")
        result = manager.stop_processes(group_name)
        return {f"status of {group_name}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# @router.get("/stop-domain/{domain_name}")
# async def stop_domain(domain_name: str):
#     result = stop_domain_processes(domain_name)
#     return {f"status": result}

# @router.get("/get-status2/{command_name}")
# async def get_status2(command_name: str):
    
#     return {"status": monitor_command(command_name)}