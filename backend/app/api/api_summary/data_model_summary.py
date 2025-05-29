# External Imports
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, TypeVar, Generic
from enum import Enum

# Local Imports
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Intialization
logger = setup_logger(
    __name__, log_file_path="api_insert", enable_debug=LOG_LEVEL_DEBUG
)
T = TypeVar(
    "T"
)  # This defines a type variable T — a placeholder for any Pydantic model (like User, Program, Product, etc.)

# Logic


class DetailedStatus(BaseModel):
    active: int = Field(..., example=10)
    stopped: int = Field(..., example=13)

class DataCount__Response(BaseModel):
    count: int = Field(
        ..., example=69, description="Shows the count of the requsted data in database"
    )
    details: Optional[DetailedStatus] = Field(
        default=None,
        description="Optional detailed breakdown of process statuses"
    )


# ---


class Generic__Response(BaseModel, Generic[T]):
    status_code: Optional[int] = Field(default=None, example=200)
    status: bool = Field(
        ..., example=True, description="Indicates if the request was successfull"
    )
    message: str = Field(
        ...,
        example="Data successfully fetched",
        description="Brief message about the response",
    )
    data: Optional[T] = None
    debug: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional debug information, such as error details or internal context",
    )
