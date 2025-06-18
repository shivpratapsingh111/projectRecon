# External imports
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

# Internal imports
from app.api.api_mail_reports import handler_report
from app.api.api_insert import handler_insert
from app.api.api_monitor_endpoints import handler_monitor
from app.api.api_results import handler_results
from app.api.api_summary import handler_summary
from app.api.api_verify import handler_verify
from app.api.api_scan import handler_scan

# Initialization
app = FastAPI()
router = APIRouter()
# Allow all origins (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Logic
@app.get("/", tags=["root"])
async def root():
    """Root endpoint to check service status."""

    return {"message": "Yeah! Running"}


app.include_router(handler_scan.router, prefix="/scan", tags=["Start New Scan"])
app.include_router(handler_insert.router, prefix="/insert", tags=["Insert New Targets"])
app.include_router(handler_report.router, tags=["Report With Automation"])
app.include_router(
    handler_monitor.router, prefix="/monitor", tags=["Monitor Endpoints"]
)
app.include_router(
    handler_results.router, prefix="/results", tags=["Get Results Of Preivous Scans"]
)
app.include_router(
    handler_summary.router,
    prefix="/summary",
    tags=["Get Summary (total subdomains, etc) From Database"],
)
app.include_router(handler_verify.router, prefix="/verify", tags=["Run Checks"])
