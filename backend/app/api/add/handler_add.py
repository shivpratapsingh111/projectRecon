# External Imports
from fastapi import APIRouter, HTTPException

# Local Imports
from app.logger.logger import setup_logger
from app.config.config  import *
from .add_manager import add_program
from .add_manager import add_mobile_target
from .add_manager import add_web_target
from .data_model_add import *

# Initializatioon
logger = setup_logger(__name__, log_file_path='add_program', enable_debug = False)
router = APIRouter()

# Handlers
@router.post("/program", response_model=GenericResponse, summary="Add a new program in database")
async def api_add_program(program_data: AddProgramRequest):
    program_dict = program_data.dict()
    program_dict["program_url"] = str(program_dict["program_url"])
    result = await add_program(program_dict)
    return GenericResponse(**result)

# ---

@router.post("/target/mobile", response_model=GenericResponse, summary="Add a new mobile target in database")
async def api_add_mobile_target(data: AddMobileTarget):
    if not data.target_package or not data.program_uuid:
        raise HTTPException(status_code=422, detail="Both program_uuid and target_package must be provided")
    mobile_target_data = {
        'program_uuid': str(data.program_uuid),
        'target_package': data.target_package,
        'target_apk': data.target_apk if data.target_apk else None,
        'technology': data.technology or [''],
        'download_url': str(data.download_url) if data.download_url else None,
        'vulnerability_reported': []
    }
    result = await add_mobile_target(mobile_target_data)
    return GenericResponse(**result)

# ---

@router.post("/target/web", response_model=GenericResponse, summary="Add a new web target in database")
async def api_add_web_target(data: WebTarget):
    if not data.target_domain or not data.program_uuid:
        raise HTTPException(422, "Both target domain and program_uuid is required")
    web_target_data = {
        'program_uuid': str(data.program_uuid),
        'target_domain': data.target_domain,
        'technology': data.technology or [''],
        'status_code': None,
        'port': None,
        'host': None,
        'ipv4': [''],
        'ipv6': [''],
        'response_time': None,
        'webserver': None,
        'vulnerability_reported': ['']

    }
    result = await add_web_target(web_target_data)
    return GenericResponse(**result)

