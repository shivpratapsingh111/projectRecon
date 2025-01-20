from app.config.config  import *
from fastapi import UploadFile, Form
from fastapi.responses import JSONResponse
from typing import List, Union
import asyncio
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, EmailStr, Field
from typing import List, Optional

from .add_manager import add_program
from .add_manager import add_mobile_target
from .add_manager import add_web_target
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = False)

router = APIRouter()

# Define Pydantic model
class ProgramData(BaseModel):
    program_name: str = Field(..., example="Bolt")
    program_url: HttpUrl = Field(..., example="https://bolt.eu/no-bounty")
    acquisitions: List[str] = Field([''], example=["Apple, Google, Prosche"])
    email: Optional[Union[EmailStr, str]] = Field(None, example="no-bounty@bolt.com")
    report_form: Optional[str] = Field(None, example=None)

class MobileTarget(BaseModel):
    program_id: str = Field(..., example="0d7228af-154e-4423-84d6-4761efc6e59b")
    program_name: str = Field(None, example="Bolt")
    target_package: str = Field(..., example="com.example.android")
    target_apk: str = Field(None, example="support@example.com")
    technology: List[str] = Field([''], example=["AWS, Cloudflare"])
    download_url: Optional[Union[HttpUrl, str]] = Field(None, example="https://example.com/path")

class WebTarget(BaseModel):
    program_id: str = Field(..., example="0d7228af-154e-4423-84d6-4761efc6e59b")
    program_name: str = Field(None, example="Bolt")
    target_domain: str = Field(..., example="account.example.com")
    technology: List[str] = Field([''], example=["AWS, Cloudflare"])


@router.get("")
async def monitor():
    return {"message": "Yeah! Running"}

@router.post("/program")
async def api_add_program(program_data: ProgramData):
    program_dict = program_data.dict()
    program_dict["program_url"] = str(program_dict["program_url"])
    return await add_program(program_dict)

@router.post("/target/mobile")
async def api_add_mobile_target(data: MobileTarget):
    # Transform the incoming data into the desired format
    if not data.target_package and not data.program_id:
        return "Target Package adn Program ID is needed"

    mobile_target_data = {
        'program_id': str(data.program_id),  # Convert UUID to string
        'target_package': data.target_package,
        'target_apk': data.target_apk if data.target_apk else None,
        'technology': data.technology if data.technology else [''],
        'download_url': str(data.download_url) if data.download_url else None,
        'vulnerability_reported': []
    }
    return await add_mobile_target(mobile_target_data)

@router.post("/target/web")
async def api_add_web_target(data: WebTarget):
    # Transform the incoming data into the desired format
    web_target_data = {
        'program_id': str(data.program_id),  # Convert UUID to string
        'target_domain': data.target_domain,
        'technology': data.technology if data.technology else [''],
        'status_code': None,
        'port': None,
        'host': None,
        'ipv4': [''],
        'ipv6': [''],
        'response_time': None,
        'webserver': None,
        'vulnerability_reported': ['']

    }
    return await add_web_target(web_target_data)

