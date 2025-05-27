from app.config.config  import *
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter


from app.services.mail_reports.report import *

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='mail_reports', enable_debug = False)

router = APIRouter()

class Report(BaseModel):
    program_name: str
    program_url: str
    target_package: str
    target_apk: str
    technology: List[str]
    download_url: Optional[str]
    email: str
    attachment_url: Optional[str]
    report_form: Optional[str]
    poc_path: Optional[str]
    acquisitions: List[str]
    strandhog: bool = False
    oauth: bool = False


class ReportList(BaseModel):
    formData: List[Report] 


@router.post("/report")
async def submit_report(report_request: ReportList):
    reports = report_request.formData 
    messages = []
        
    try:
        logger.info(f"Number of programs provided: {len(reports)}")
        invalid_reports = [
            report.program_name
            for report in reports
            if (report.strandhog and report.oauth) or (not report.strandhog and not report.oauth)
        ]
        if invalid_reports:
            return {"messages": f"Error: Please select one scan at a time for: {', '.join(invalid_reports)}"}
        
        if isinstance(reports, list) and len(reports) > 1:
            
            # Collect program_names, which dont either have selected both or none scans
            try:
                for report in reports:
                    strandhog = report.strandhog
                    oauth = report.oauth
                    if strandhog and not oauth:
                        messages.extend(send_report(report.model_dump(), "Strandhog"))
                    elif not strandhog and oauth:
                        messages.extend(send_report(report.model_dump(), "OAuth"))
                    # messages.extend("Success: Emails Sent!")
            except Exception as e:
                messages.extend(logger.exception("Error: Something went wrong"))
                    
        else:
            for report in reports:
                strandhog = report.strandhog
                oauth = report.oauth
                if strandhog and not oauth:
                    messages.extend(send_report(report.model_dump(), "Strandhog"))
                elif not strandhog and oauth:
                    messages.extend(send_report(report.model_dump(), "OAuth"))
                elif strandhog and oauth:
                    messages.extend("Info: Only one scan can be selected at a time")
                elif not strandhog and not oauth:
                    messages.extend("Info: No scan selected")
                    

        # Return collected messages
        if messages:
            return {"messages": messages}

        return {"message": "Error: Something went wrong"}

    except Exception as e:
        logger.exception("Error: Unable to process reports")
        return {"message": "Error: Unable to process reports", "error": str(e)}

