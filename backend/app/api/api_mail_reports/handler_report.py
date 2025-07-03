# External imports
import traceback
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import List

# Internal imports
from app.config.config  import LOG_LEVEL_DEBUG
from app.services.mail_reports.report import send_report
from app.interface.logger_manager import setup_logger
from .data_model_report import Generic__Response, ReportList__Request, Report__Response

# Initialization
logger = setup_logger(__name__, log_file_path='api', enable_debug = LOG_LEVEL_DEBUG)
router = APIRouter()

# NOT IMPLETEMENTED PROPERLY

# Logic
@router.post("/report")
async def submit_report(report_request: ReportList__Request):
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={
            "status": False,
            "message": "NOT IMPLEMENTED PROPERLY",
        },
    )
    # reports = report_request.formData
    # messages = []

    # try:
    #     logger.info(f"Number of programs provided: {len(reports)}")
    #     invalid_reports = [
    #         report.program_name
    #         for report in reports
    #         if (report.strandhog and report.oauth)
    #         or (not report.strandhog and not report.oauth)
    #     ]
    #     # if invalid_reports:
    #     #     return {
    #     #         "messages": f"Error: Please select one scan at a time for: {', '.join(invalid_reports)}"
    #     #     }

    #     if isinstance(reports, list) and len(reports) > 1:

    #         # Collect program_names, which dont either have selected both or none scans
    #         try:
    #             for report in reports:
    #                 strandhog = report.strandhog
    #                 oauth = report.oauth
    #                 if strandhog and not oauth:
    #                     messages.append(send_report(report.model_dump(), "Strandhog"))
    #                 elif not strandhog and oauth:
    #                     messages.append(send_report(report.model_dump(), "OAuth"))
    #                 # messages.append("Success: Emails Sent!")
    #         except Exception as e:
    #             logger.exception("Error: Something went wrong")
    #             messages.append("Error: Something went wrong")

    #     else:
    #         for report in reports:
    #             strandhog = report.strandhog
    #             oauth = report.oauth
    #             if strandhog and not oauth:
    #                 messages.append(send_report(report.model_dump(), "Strandhog"))
    #             elif not strandhog and oauth:
    #                 messages.append(send_report(report.model_dump(), "OAuth"))
    #             elif strandhog and oauth:
    #                 messages.append("Info: Only one scan can be selected at a time")
    #             elif not strandhog and not oauth:
    #                 messages.append("Info: No scan selected")

    #     # Return collected messages
    #     if messages:
    #         return Generic__Response[Report__Response](
    #             status=True,
    #             message="Report(s) processed",
    #             data=Report__Response(message=messages),
    #         )

    #     return Generic__Response[List[str]](
    #         status=False,
    #         message="Something went wrong",
    #     )

    # except Exception as e:
    #     full_trace = traceback.format_exc()
    #     logger.error(f"Error at api handler level: {e} \n {full_trace}")
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={
    #             "status": False,
    #             "message": "Error at api handler level",
    #             "debug": {"error": str(e), "traceback": full_trace},
    #         },
    #     )
