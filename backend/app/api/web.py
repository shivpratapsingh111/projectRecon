from app.api import file_get_all
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Dict
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
    groupName: str = Form(...),
    scan_list: str = Form(...)
):

    start_scan(groupName, domain_list, scan_list)
    
    return {"Message": "Scan started successfully", "Group Name": groupName,"Domains": domain_list, "Scans Selected": scan_list}



@router.post("/web/file", tags=["Domain list input"])
async def get_domain_file(
    file: UploadFile = File(...),  # Required file upload
    groupName: str = Form(...),  # Required text input
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
    
    print(groupName, domain_list, scan_list)
    # asyncio.create_task(asyncio.to_thread(start_scan, groupName, domain_list, scan_list))
    time.sleep(2)
    # manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{groupName}")
    # result = manager.command_monitor(groupName)
    return {"Group name": groupName,"Domains": domain_list, "Scans Selected": scan_list, "Status": "running"} 
    # return result
 

@router.get("/get-status/{groupName}")
async def get_status1(groupName: str):
    try:
        manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{groupName}")
        result = manager.command_monitor(groupName)
        return {f"status of {groupName}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/process-scan")
async def process_scan(
    domain: Union[str, None] = Form(None),
    groupName: Union[str, None] = Form(None),
    file: Union[UploadFile, None] = None,
    subdomainPassive: Union[str, None] = Form(None),
    subdomainBoth: Union[str, None] = Form(None),
    urlEnum: Union[str, None] = Form(None),
):
    """
    Processes the request to extract scan names and domains.
    - `domain`: A comma-separated list of domains from a text input.
    - `file`: A file containing one domain per line.
    - Scan parameters are passed as boolean-like strings ("true").
    """

    # Initialize the scan names and domains list
    scan_names = []
    domains = []

    # Collect scan names if the parameters are "true"
    if subdomainPassive == "true":
        scan_names.append("subdomainPassive")
    if subdomainBoth == "true":
        scan_names.append("subdomainBoth")
    if urlEnum == "true":
        scan_names.append("urlEnum")

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

    print(groupName, domains, scan_names)

    asyncio.create_task(asyncio.to_thread(start_scan, groupName, domains, scan_names))
    manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{groupName}")
    # result = manager.command_monitor(groupName)

    return {
        "groupName": groupName,
        "scanNames": scan_names,
        "domains": domains,
    }



@router.get("/stop-all/{groupName}")
async def stop_all(groupName: str):
    try:
        manager = DomainCommandManager(log_dir=f"{root_Data_Dir}/{groupName}")
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