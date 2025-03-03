
import asyncio
from fastapi.responses import JSONResponse
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='web_scan', enable_debug = True)
import json
from app.interface.scan_manager import start_scan
from app.config.db_config  import db_config
from app.db.db_operations import DatabaseOperations
from app.db.db_manager import DatabaseManager
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

async def new_scan(domain, group_name, file, execution_style, scanOptions):
    try:
        if scanOptions:
            scan_config = json.loads(scanOptions)
        else:
            scan_config = []
    except json.JSONDecodeError:
        logger.exception("Invalid format for scanOptions.")
        return JSONResponse(
            content={"error": "Invalid format for scanOptions."},
            status_code=400,
        )

    # Validate at least one scan option is selected
    if not scan_config:
        logger.error("No scan options provided")
        return JSONResponse(
            content={"error": "No scan options provided."},
            status_code=400,
        )

    domain_list = []

    if domain:
        domain_list += [d.strip() for d in domain.split(",") if d.strip()]

    if file:
        file_content = (await file.read()).decode("utf-8")
        domain_list += [line.strip() for line in file_content.splitlines() if line.strip()]

    if not domain_list or not group_name or not execution_style or not scanOptions:
        logger.error("Necessary details not provided")
        return JSONResponse(
            content={"error": "Necessary details not provided"},
            status_code=400,
        )

    if not domain_list:
        logger.error("No domain_list provided. Use either 'domain' or 'file'.")
        return JSONResponse(
            content={"error": "No domain_list provided. Use either 'domain' or 'file'."},
            status_code=400,
        )
    # Check what domain is same in domain_list and user provided domains then call any scan function accordingly

    # result = db_ops.query_operations().get_all_web_targets()
    # domain_list_db = [item[0] for item in result]

    # for domain in domain_list:
    #     for domain_db in domain_list_db:
    #         if domain_db == domain:
    #             return JSONResponse(
    #                 content={"error": f"{domain} already exists in DB"},
    #                 status_code=400,
    #             )
    logger.debug(f"Scan_Name: {group_name}, \nDomains{domain_list}, \n Scan_Oprtions{scan_config}")

    asyncio.create_task(asyncio.to_thread(start_scan, group_name, domain_list, execution_style, scan_config))

    return {
        "Group Name": group_name,
        "Domains": domain_list,
        "Scan Config": scan_config,
    }
