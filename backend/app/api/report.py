from app.api import file_get_all
from app.config.config  import *
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Union, Dict
from pydantic import BaseModel
import uvicorn, asyncio, time
from fastapi import APIRouter
from app.interface.process_manager import DomainCommandManager
import json
import logging


from app.services.sendReports.oauth.oauthReport import *
from app.services.sendReports.strandhog.strandhogReport import *


router = APIRouter()
manager = DomainCommandManager()

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
        print(f"Number of programs provided: {len(reports)}")
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
                        print("Calling Strandhog")
                        messages.extend(strandhog_send_mail(report.model_dump()))
                    elif not strandhog and oauth:
                        print("Calling OAuth")
                        messages.extend(oauth_send_mail(report.model_dump()))
                    # messages.append("Success: Emails Sent!")
            except Exception as e:
                messages.append(logging.exception("Error: Something went wrong"))
                    
        else:
            for report in reports:
                strandhog = report.strandhog
                oauth = report.oauth
                if strandhog and not oauth:
                    print("Calling Strandhog")
                    messages.append(strandhog_send_mail(report.model_dump()))
                elif not strandhog and oauth:
                    print("Calling OAuth")
                    messages.append(oauth_send_mail(report.model_dump()))
                elif strandhog and oauth:
                    messages.append("Info: Only one scan can be selected at a time")
                elif not strandhog and not oauth:
                    messages.append("Info: No scan selected")
                    

        # Return collected messages
        if messages:
            return {"messages": messages}

        return {"message": "Error: Something went wrong"}

    except Exception as e:
        logging.exception("An error occurred")
        return {"message": "Error: Unable to process reports", "error": str(e)}

