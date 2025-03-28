from backend.app.api.results.read_results import websocket_read_results
from backend.app.api.results.read_results import http_read_results
from backend.app.api.results.read_results import get_log_file_content
from app.api.results.get_download_ready import get_download
from app.api.results.get_download_ready import get_program_scan

from fastapi import WebSocket, WebSocketDisconnect
from fastapi import APIRouter
import asyncio
import json
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
from pathlib import Path

from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='results', enable_debug = True)

router = APIRouter()

@router.get("")
async def results():
    return {"message": "Yeah! Running"}

@router.websocket("/subdomains/{target_uuid}")
async def api_running_results_subdomains(target_uuid, websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            result = await websocket_read_results(target_uuid, 'subdomains') 
            
            await websocket.send_text(json.dumps(result)) 
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()


@router.websocket("/urls/{target_uuid}")
async def api_running_results_urls(target_uuid, websocket: WebSocket):
    try:
        await websocket.accept() 
        while True:
            result = await websocket_read_results(target_uuid, 'urls')
            
            await websocket.send_text(json.dumps(result))
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        logger.warning("Client disconnected")
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        if not websocket.client_state.DISCONNECTED:
            await websocket.close()



@router.get("/get/{target_uuid}")
async def api_stored_results(target_uuid: str, file: str = Query(..., description="The file name"), limit: Optional[int] = Query(20, gt=0), offset: int = Query(0, ge=0)):
    try:
        result = await http_read_results(target_uuid, file, limit, offset)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/get-log")
async def api_get_log_file_content(pid: int = Query(..., description="Process ID"), log_type: str = Query(..., description="Log type")):
    try:
        result = await get_log_file_content(pid, log_type)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



# ============================[Download Routes]

@router.get("/download/{program_name}")
async def download_program_scan(program_name):
    try:
        result = await get_program_scan(program_name)
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{target_uuid}/subdomains")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{target_uuid}/live-subdomains")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'live_subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/download/{target_uuid}/httpx-subdomains")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'httpx_subdomains')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

        
@router.get("/download/{target_uuid}/urls")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'urls')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{target_uuid}/extensions")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'extensions')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{target_uuid}/live-extensions")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'live_extensions')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")
        
@router.get("/download/{target_uuid}/nuclei")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'nuclei')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")



@router.get("/download/{target_uuid}/js_nuclei") # DONT REPLACE '_' WITH '-' THAT IS INTENTIONAL
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'js_nuclei')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

@router.get("/download/{target_uuid}/extracted-urls")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'extracted_urls')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

@router.get("/download/{target_uuid}/extracted-paths")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'extracted-paths')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

@router.get("/download/{target_uuid}/sensitive-data")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'sensitive_data')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")

@router.get("/download/{target_uuid}/sensitive-keywords")
async def download(target_uuid):
    try:
        result = await get_download(target_uuid, 'sensitive_keywords')
        return result
    except Exception as e:
        logger.exception(f"Error: {str(e)}")