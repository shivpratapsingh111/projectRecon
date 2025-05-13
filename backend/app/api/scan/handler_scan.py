# External Imports
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    HTTPException,
    Form,
)
import asyncio, json
from pydantic import ValidationError
from typing import Literal, Optional

# Local Imports
from app.interface.process_manager import CommandExecutor
from app.config.config import *
from app.config.db_config import db_config
from app.api.scan.new_scan import new_scan
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.api.scan.scan_db_manager import get_existing_program_names
from app.logger.logger import setup_logger
from .data_model_scan import (
    ProgramsData,
    ExistingProgramNamesResponse,
    ScanOptionsRequest,
    StopCommandProcessResponse,
    ProcessScanResponse,
    StopDomainProcessResponse,
    StopProgramProcessResponse
)

# Initialization
logger = setup_logger(__name__, log_file_path="web_scan", enable_debug=True)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)
router = APIRouter()
manager = CommandExecutor()


# Handlers
@router.websocket("/ws/get-all")
async def websocket_get_all(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            result = manager.get_all_data()
            validated_data = ProgramsData.parse_obj(result)
            await websocket.send_text(validated_data.json())
            await asyncio.sleep(10)

    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        await websocket.close(code=1003)  # 1003 = Unsupported Data
        raise HTTPException(
            status_code=500, detail="Invalid data format received from manager"
        )

    except WebSocketDisconnect:
        logger.warning("Client disconnected")

    except Exception as e:
        logger.exception(f"Unhandled error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()
        raise HTTPException(status_code=500, detail="Unexpected server error")


# ---


@router.get(
    "/get-all",
    response_model=ProgramsData,
    summary="Get all program data",
)
async def api_get_all():
    """
    Returns a dictionary of all available program data in detail.
    """
    try:
        result = manager.get_all_data()
        return ProgramsData(**result)
    except Exception as e:
        logger.exception(f"Error: {str(e)}")


# ---


@router.get(
    "/get-existing-programnames",
    response_model=ExistingProgramNamesResponse,
    summary="Get all existing program names",
)
async def api_get_existing_program_names():
    """
    Returns a list of all program names already existing in the database.
    """
    return await get_existing_program_names()


# ---


@router.post(
    "/process-scan",
    response_model=ProcessScanResponse,
    summary="Start a scan",
)
async def process_scan(
    domain: str = Form(
        ...,
        description="Comma-separated domains"
    ),
    programName: str = Form(
        ...,
        description="Program name to which target domain belongs.",
    ),
    execution_style: Literal["sequential", "parallel"] = Form(
        ...,
        description="Execution style for the scan. Allowed values: 'sequential', 'parallel'",
    ),
    scanOptions: str = Form(..., description="JSON string of scan options"),
    file: Optional[UploadFile] = File(default=None),
):
    """
    ### How to Use This Endpoint

    Submit a multipart/form-data request with the following fields:
    - `domain`: e.g., "google.com"
    - `programName`: e.g., "Google"
    - `execution_style`: "sequential" or "parallel"
    - `scanOptions`: JSON string. Example:
    ```json
    {
    "subdomainEnum": {
        "run": True,
        "includeApi": True,
        "toolSelection": True,
        "selectedTools": [
        "bbot",
        "subdominator",
        "subfinder",
        "cero",
        "yass",
        "sublist3r",
        "githubsubdomains",
        "gitlabsubdomains"
        ],
        "isPassive": True,
        "dnsBruteforce": False,
        "httpx": True,
        "screenshot": True
    },
    "urlEnum": {
        "run": True,
        "includeApi": True,
        "toolSelection": True,
        "selectedTools": [
        "waybackurls",
        "gau",
        "waymore"
        ],
        "isPassive": False,
        "dnsBruteforce": False
    },
    "nuclei": {
        "run": True,
        "allTemplates": True,
        "specificTemplates": False,
        "templateInput": "",
        "customTemplates": False,
        "specificCommand": False,
        "commandInput": ""
    },
    "nmap": {
        "run": False,
        "allPorts": False,
        "topPorts": False,
        "webPorts": False,
        "specificPorts": False,
        "portInput": "",
        "specificCommand": False,
        "commandInput": ""
    },
    "js": {
        "run": True,
        "doEverything": True,
        "specificRegex": False,
        "regexInput": "",
        "regexOnly": False
    }
    }

    ```
    """
    try:
        parsed_options = json.loads(scanOptions)
        validated_options = ScanOptionsRequest(**parsed_options)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid scanOptions format: {e}")


    return await new_scan(
        domain=domain,
        program_name=programName,
        file=file,
        execution_style=execution_style,
        scan_options=validated_options.dict(),
    )


# ---


@router.post(
    "/stop/command/{process_id}",
    response_model=StopCommandProcessResponse,
    summary="Stop a running command",
)
async def stop_command_processes(process_id: str):
    """
    - Stop a running command by its process ID.
    - Returns either `killed` or `not found`.
    """
    try:
        result = manager.kill_process_by_pid(process_id, "single")
        return StopCommandProcessResponse(status=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---


@router.post("/stop/domain/{program_uuid}/{target_uuid}",
    response_model=StopDomainProcessResponse,
    summary="Stop all running commands under a domain",
)
async def stop_domain_processes(program_uuid: str, target_uuid: str):
    """
    - Kill all processes running under a domain/target by program_uuid and target_uuid
    - Returns a list of killed pids
    """
    try:
        result = manager.kill_domain_processes(program_uuid, target_uuid)
        return {f"status of domain {target_uuid} of program {program_uuid}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---


@router.post("/stop/program/{program_name}",
    response_model=StopProgramProcessResponse,
    summary="Stop all running commands under a program",
)
async def stop_program_processes(program_name: str):
    """
    - Kill all processes running under a program by program_name
    - Returns a list of killed pids
    """

    try:
        result = manager.kill_program_processes(program_name)
        return {f"status of {program_name}": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
