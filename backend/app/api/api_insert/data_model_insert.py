# External imports
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator
from typing import Optional, TypeVar, Dict, Any

# Internal imports
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG
)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)


# Logic
class InsertProgram__Request(BaseModel):
    program_name: str = Field(..., example="Bolt")  # required
    program_url: HttpUrl = Field(..., example="https://bolt.eu/no-bounty")  # required
    acquisitions: Optional[List[str]] = Field(
        default=None, example=["Apple", "Google", "Porsche"]
    )  # optional
    email: Optional[EmailStr] = Field(
        default=None, example="no-bounty@bolt.com"
    )  # optional
    report_form: Optional[HttpUrl] = Field(
        default=None, example="https://docs.google.com/xxx"
    )  # optional

    @field_validator("email", "report_form", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        return value or None


# ---


class InsertMobileTarget__Request(BaseModel):
    program_uuid: UUID = Field(
        ..., example="0d7228af-154e-4423-84d6-4761efc6e59b"
    )  # required
    target_package: str = Field(..., example="com.example.android")  # required
    target_apk: Optional[str] = Field(default=None, example="Example APK")  # optional
    technology: Optional[List[str]] = Field(
        default=None, example=["AWS", "Cloudflare"]
    )  # optional
    download_url: Optional[HttpUrl] = Field(
        default=None, example="https://example.com/path"
    )  # optional

    @field_validator("target_apk", "download_url", mode="before")
    @classmethod
    def empty_str_to_none(cls, value):
        return value or None


# ---


class InsertWebTarget__Request(BaseModel):
    program_uuid: UUID = Field(
        ..., example="0d7228af-154e-4423-84d6-4761efc6e59b"
    )  # required
    target_domain: str = Field(..., example="account.example.com")  # required
    technology: Optional[List[str]] = Field(
        default=None, example=["AWS", "Cloudflare"]
    )  # optional


# ---


class Generic__Response(BaseModel):
    status_code: Optional[int] = Field(default=None, example=200)
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Program inserted successfully",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
