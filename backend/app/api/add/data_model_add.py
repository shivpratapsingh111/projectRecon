from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, HttpUrl, EmailStr, Field

# Pydantic data models
class AddProgramRequest(BaseModel):
    program_name: str = Field(..., example="Bolt")  # required
    program_url: HttpUrl = Field(..., example="https://bolt.eu/no-bounty")  # required
    acquisitions: Optional[List[str]] = Field(default=None, example=["Apple", "Google", "Porsche"])  # optional
    email: Optional[EmailStr] = Field(default=None, example="no-bounty@bolt.com")  # optional
    report_form: Optional[HttpUrl] = Field(default=None, example="https://docs.google.com/xxx")  # optional

class AddMobileTarget(BaseModel):
    program_uuid: UUID = Field(..., example="0d7228af-154e-4423-84d6-4761efc6e59b")  # required
    target_package: str = Field(..., example="com.example.android")  # required
    target_apk: Optional[str] = Field(default=None, example="Android APK")  # optional
    technology: Optional[List[str]] = Field(default=None, example=["AWS", "Cloudflare"])  # optional
    download_url: Optional[HttpUrl] = Field(default=None, example="https://example.com/path")  # optional

class WebTarget(BaseModel):
    program_uuid: UUID = Field(..., example="0d7228af-154e-4423-84d6-4761efc6e59b")  # required
    target_domain: str = Field(..., example="account.example.com")  # required
    technology: Optional[List[str]] = Field(default=None, example=["AWS", "Cloudflare"])  # optional

class GenericResponse(BaseModel):
    message: str = Field(..., example="Program inserted successfully")
    id: UUID = Field(..., example="0d7228af-154e-4423-84d6-4761efc6e59b")

