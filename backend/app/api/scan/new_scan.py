
# External Imports
import asyncio
from fastapi import HTTPException

# Internal Imports
from app.logger.logger import setup_logger
from app.interface.scan_manager import start_scan
from app.config.db_config  import db_config
from app.db.db_operations import DatabaseOperations
from app.db.db_manager import DatabaseManager

# Initialization
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)

# Logic
async def new_scan(domain, program_name, file, execution_style, scan_options):

    if not domain and not file:
        logger.error("Neither domain nor file is provided, provide either 'domain' or 'file'.")
        raise HTTPException(status_code=422, detail="No domain_list provided. Use either 'domain' or 'file'.")

    if domain and file:
        logger.error("File and domain both are provided, provide either 'domain' or 'file'.")
        raise HTTPException(status_code=422, detail="No domain_list provided. Use either 'domain' or 'file'.")

    domain_list = []

    if domain:
        domain_list += [d.strip() for d in domain.split(",") if d.strip()]

    if file:
        file_content = (await file.read()).decode("utf-8")
        domain_list += [line.strip() for line in file_content.splitlines() if line.strip()]

    logger.debug(f"Scan_Name: {program_name}, \nDomains{domain_list}, \n Scan_Options{scan_options}")

    asyncio.create_task(asyncio.to_thread(start_scan, program_name, domain_list, execution_style, scan_options))

    return {"message": "Scan started successfully"}
