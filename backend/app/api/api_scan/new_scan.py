# External imports
import asyncio
from fastapi import status

# Internal imports
from app.interface.scan_manager import start_scan
from app.interface.logger_manager import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(__name__, log_file_path="api", enable_debug=LOG_LEVEL_DEBUG)


# Logic
async def new_scan(domain, program_name, file, execution_style, scan_options):

    if not domain and not file:
        logger.error(
            "Neither domain nor file is provided, provide either 'domain' or 'file'"
        )
        return {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "status": False,
            "message": "Neither domain nor file is provided, provide either 'domain' or 'file'",
        }

    if domain and file:
        logger.error(
            "File and domain both are provided, provide either 'domain' or 'file'"
        )
        return {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "status": False,
            "message": "File and domain both are provided, provide either 'domain' or 'file'",
        }

    domain_list = []

    if domain:
        domain_list += [d.strip() for d in domain.split(",") if d.strip()]

    if file:
        file_content = (await file.read()).decode("utf-8")
        domain_list += [
            line.strip() for line in file_content.splitlines() if line.strip()
        ]

    logger.debug(
        f"Program_Name: {program_name}, \nDomains{domain_list}, \n Scan_Options{scan_options}"
    )

    asyncio.create_task(
        asyncio.to_thread(
            start_scan, program_name, domain_list, execution_style, scan_options
        )
    )

    return {"status": True, "message": "Scan started successfully"}
