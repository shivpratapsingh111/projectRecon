from app.api.results.get_results import get_results
from app.api.download.get_download_ready import get_download
from app.api.download.get_download_ready import get_group_scan
from fastapi import APIRouter
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from backend.app.interface.process_manager import CommandExecutor
import json

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='download', enable_debug = True)

router = APIRouter()
manager = CommandExecutor()

@router.get("")
async def results():
    return {"message": "Yeah! Running"}
        
@router.get("/{group_name}")
async def download_group_scan(group_name):
    try:
        result = get_group_scan(group_name)
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
        
        
        
        
@router.get("/all-subdomains/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/live-subdomains/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'liveSubdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/httpx-subdomains/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'httpx_subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/all-urls/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'urls')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/urls-arranged-all/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'urlsArrangedAll')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/urls-arranged-200/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'urlsArranged200')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/urls-arranged-200-small/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'urlsArranged200_small')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/nuclei-results/{domain_id}")
async def download(domain_id):
    try:
        result = get_download(domain_id, 'nuclei_results')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
