
import asyncio
from fastapi.responses import JSONResponse
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)
import json
from app.interface.scan_manager import start_scan

async def new_scan(domain, groupName, file, execution_style, scanOptions):
    try:
        if scanOptions:
            scan_names = json.loads(scanOptions)
        else:
            scan_names = []
    except json.JSONDecodeError:
        logger.exception("Invalid format for scanOptions.")
        return JSONResponse(
            content={"error": "Invalid format for scanOptions."},
            status_code=400,
        )

    # Validate at least one scan option is selected
    if not scan_names:
        logger.error("No scan options provided")
        return JSONResponse(
            content={"error": "No scan options provided."},
            status_code=400,
        )

    # Initialize the domains list
    domains = []

    # Process domains from the "domain" input field
    if domain:
        domains += [d.strip() for d in domain.split(",") if d.strip()]

    # Process domains from the uploaded file
    if file:
        file_content = (await file.read()).decode("utf-8")
        domains += [line.strip() for line in file_content.splitlines() if line.strip()]

    # If no domains are provided, return an error
    if not domains or not groupName or not execution_style or not scanOptions:
        logger.error("Necessary details not provided")
        return JSONResponse(
            content={"error": "Necessary details not provided"},
            status_code=400,
        )

    # If no domains are provided, return an error
    if not domains:
        logger.error("No domains provided. Use either 'domain' or 'file'.")
        return JSONResponse(
            content={"error": "No domains provided. Use either 'domain' or 'file'."},
            status_code=400,
        )

    # Print for debugging purposes
    logger.debug(f"Scan_Name: {groupName}, \nDomains{domains}, \n Scan_Oprtions{scan_names}")

    # Create async task for scanning
    asyncio.create_task(asyncio.to_thread(start_scan, groupName, domains, execution_style, scan_names))

    return {
        "groupName": groupName,
        "scanNames": scan_names,
        "domains": domains,
    }
