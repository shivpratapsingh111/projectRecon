# External imports
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    status,
    File,
    Form,
)
import asyncio, json, traceback
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Literal, Optional

# Internal imports
from app.api.api_scan.new_scan import new_scan
from app.api.api_scan.scan_db_manager import get_existing_program_names
from app.interface.logger import setup_logger
from .data_model_scan import (
    Generic__Response,
    ProgramsData__Response,
    ExistingProgramNames__Response,
    ScanOptions__Request,
    StopCommandProcess__Response,
    ProcessScan__Response,
    StopDomainProcess__Response,
    StopProgramProcess__Response,
)
from app.interface.process_manager import CommandExecutor
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)
router = APIRouter()
manager = CommandExecutor()


# Handlers
@router.websocket("/ws/get-all")
async def websocket_get_all(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            result = manager.get_all_data()
            validated_data = ProgramsData__Response.parse_obj(result)
            await websocket.send_text(validated_data.json())
            await asyncio.sleep(10)

    except ValidationError as e:
        logger.error(f"Data validation failed: {e}")
        await websocket.close(code=1003)  # 1003 = Unsupported Data
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Invalid data format received from manager",
            },
        )

    except WebSocketDisconnect:
        logger.warning("Client disconnected")

    except Exception as e:
        logger.exception(f"Unhandled error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()
        return JSONResponse(
            status_code=500,
            content={
                "status": False,
                "message": "Unexpected server error",
            },
        )


# ---


@router.get(
    "/get-all",
    response_model=Generic__Response[ProgramsData__Response],
    summary="Get all program data",
)
async def api_get_all():
    """
    Returns a dictionary of all available program data in detail.
    """
    try:
        data = manager.get_all_data()
        result = {
            "status": True,
            "message": "Programs data fetched successfully",
            "data": data,
        }
        if result["status"]:
            return Generic__Response[ProgramsData__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---


@router.get(
    "/get-existing-programnames",
    response_model=Generic__Response[ExistingProgramNames__Response],
    summary="Get all existing program names",
)
async def api_get_existing_program_names():
    """
    Returns a list of all program names already existing in the database.
    """
    try:
        result = await get_existing_program_names()
        if result["status"]:
            return Generic__Response[ExistingProgramNames__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---

# ===UNDER CONSTRUCTION===

# @router.get(
#     "/verify-scan-setup",
#     response_model=SET_THIS_UP,
#     summary="Get all existing program names",
# )
# async def api_verify_scan_setup():
#     """
#     Verifies the reqired system environment before running scan.
#     """
#     try:
#         result =  {
#                 "status": True,
#                 "message": "Verification completed",
#                 "data": "All tools are installed, Enviornment is ready to run scan.",
#                 "debug": {"error": str(e), "traceback": full_trace},
#             }
#         if result["status"]:
#             return Generic__Response[SET_THIS_UP](**result)
#         else:
#             return JSONResponse(
#                 status_code=result.get("status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
#                 content=result,
#             )

#     except Exception as e:
#         full_trace = traceback.format_exc()
#         logger.error(f"Error at api handler level: {e} \n {full_trace}")
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={
#                 "status": False,
#                 "message": "Error at api handler level",
#                 "debug": {"error": str(e), "traceback": full_trace},
#             },
#         )

# ---


@router.post(
    "/process-scan",
    response_model=Generic__Response[ProcessScan__Response],
    summary="Start a scan",
)
async def process_scan(
    domain: str = Form(..., description="Comma-separated domains"),
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
        try:
            parsed_options = json.loads(scanOptions)
            validated_options = ScanOptions__Request(**parsed_options)
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            full_trace = traceback.format_exc()
            return JSONResponse(
                status_code=422,
                content={
                    "status": False,
                    "message": f"Invalid scanOptions format",
                    "debug": {"error": str(e), "traceback": full_trace},
                },
            )

        result = await new_scan(
            domain=domain,
            program_name=programName,
            file=file,
            execution_style=execution_style,
            scan_options=validated_options.dict(),
        )
        if result["status"]:
            return Generic__Response[ProcessScan__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---


@router.post(
    "/stop/command/{process_id}",
    response_model=Generic__Response[StopCommandProcess__Response],
    summary="Stop a running command",
)
async def stop_command_processes(process_id: str):
    """
    - Stop a running command by its process ID.
    - Returns either `killed` or `not found`.
    """
    try:
        response = manager.kill_process_by_pid(process_id, "single")
        result = {
            "status_code": (
                status.HTTP_200_OK if response else status.HTTP_404_NOT_FOUND
            ),
            "status": response,
            "message": "Killed successfully" if response else "Not Found",
            "data": {"status": "killed" if response else "not found"},
        }
        if result["status"]:
            return Generic__Response[StopCommandProcess__Response](**result)
        else:
            return JSONResponse(
                status_code=result.get(
                    "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
                content=result,
            )

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---


@router.post(
    "/stop/domain/{program_uuid}/{target_uuid}",
    response_model=Generic__Response[StopDomainProcess__Response],
    summary="Stop all running commands under a domain",
)
async def stop_domain_processes(program_uuid: str, target_uuid: str):
    """
    - Kill all processes running under a domain/target by program_uuid and target_uuid
    - Returns a list of killed pids
    """
    try:
        response = manager.kill_domain_processes(program_uuid, target_uuid)
        result = {
            "status": True,
            "message": f"Killed these PIDs {response}",
            "data": {"killed_pids": response},
        }
        return Generic__Response[StopDomainProcess__Response](**result)
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.error(f"Error at api handler level: {e} \n {full_trace}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": False,
                "message": "Error at api handler level",
                "debug": {"error": str(e), "traceback": full_trace},
            },
        )


# ---

# ===UNDER CONSTRUCTION===

# @router.post(
#     "/stop/program/{program_name}",
#     response_model=StopProgramProcess__Response,
#     summary="Stop all running commands under a program",
# )
# async def stop_program_processes(program_name: str):
#     """
#     - Kill all processes running under a program by program_name
#     - Returns a list of killed pids
#     """

#     try:
#         result = manager.kill_program_processes(program_name)
#         return {f"status of {program_name}": result}
#     except ValueError as e:
#         return JSONResponse(
#             status_code=422,
#             content={
#                 "status": False,
#                 "message": f"{str(e)}",
#             },
#         )
