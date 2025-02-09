from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from urllib.parse import urlparse
import logging
import shutil
import json
import os

from app.config.db_config import db_config
from app.config.config import root_Data_Dir

from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
logger = setup_logger(__name__, log_file_path='monitor_endpoints', enable_debug = True)


db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)

def get_review_endpoints():
    result = []
    data = db_ops.query_operations().get_need_review_endpoints()
    if data is not None:
        for row in data:
            result.append({
                'id': row[0],
                'program_id': row[1],
                'target_id': row[2],
                'scan_name': row[3],
                'url': row[4],
                'change_detected_at': row[5],  # You may need to convert this to a simpler format if required
                'old_status_code': row[6],
                'new_status_code': row[7],
                'old_response_size': row[8],
                'new_response_size': row[9],
                'old_body_file_path': row[10],
                'new_body_file_path': row[11]
            })

        # Convert the result into JSON format
        json_result = json.dumps(result)
        return json_result
    else:
        return None

def get_response_body_changes(endpoint_id):
    result = []
    
    data = db_ops.query_operations().get_endpoint_response_body_filepaths(endpoint_id)

    if data is not None:
        result.append({
            'old_body_file_path': data[0],
            'new_body_file_path': data[1]
        })
        old_body_file_path = data[0]
        new_body_file_path = data[1]
        
        # Check if the files exist
        try:
            
            if not os.path.isfile(old_body_file_path) or not os.path.isfile(new_body_file_path):
                raise HTTPException(status_code=404, detail="One or both files not found")
        except Exception as e:
            logger.exception(f"Probably, Path is None. {e}")

        try:
            # Read the content of both files
            with open(old_body_file_path, "r") as file1:
                file_content1 = file1.read()

            with open(new_body_file_path, "r") as file2:
                file_content2 = file2.read()

        except Exception as e:
            logger.exception("Error reading files")
            raise HTTPException(status_code=500, detail=f"Error reading files: {e}")

        # Return both files' contents in a JSON response
        return JSONResponse(content={"file1": file_content1, "file2": file_content2})

    else:
        return None

def mark_review_endpoints(endpoint_id):
    try:
        db_ops.update_operations().update_need_review_endpoint(endpoint_id)
        return JSONResponse(content={"message": "Marked endpoint reviewed"})
    except Exception as e:
        logger.exception("Error marking endpoint reviewd")
        raise HTTPException(status_code=500, detail=f"Error marking endpoint reviewd: {e}")
    
def update_endpoint_scan_interval(endpoint_id, interval):
    try:
        db_ops.update_operations().update_endpoint_interval(endpoint_id, interval)
        return JSONResponse(content={"message": f"Updated endpoint scan interval to {interval}"})
    except Exception as e:
        logger.exception("Error updating endpoint scan interval")
        raise HTTPException(status_code=500, detail=f"Error updating endpoint scan interval: {e}")

def get_endpoints_by_status(status):
    try:
        data = db_ops.query_operations().get_endpoints_data_by_status(status)
        result = []

        if data is not None:
            for row in data:
                entry = {
                    'id': row[0],
                    'program_id': row[1],
                    'program_name': None,
                    'scan_name': row[2],
                    'scan_interval': row[3],
                    'status': row[4],
                    'url': row[5],
                    'new_status_code': row[6],
                    'new_response_size': row[7],
                    'new_body_file_path': row[8],
                    'last_check': str(row[9])
                }

                program_name = db_ops.query_operations().get_program_name(row[1])
                if program_name:
                    entry['program_name'] = program_name[0][0]
                else:
                    entry['program_name'] = None
                result.append(entry)

            return result
        else:
            return None

    except Exception as e:
        logger.exception(f"Error fetching endpoints by status: {e}")
        return None    

def update_endpoint_status(endpoint_id, status):
    try:
        db_ops.update_operations().update_endpoint_status(endpoint_id, status)
        return JSONResponse(content={"message": "endpoint status updated"}, status_code=200)
    except Exception as e:
        logger.exception("Error updating endpoint status")
        raise HTTPException(status_code=500, detail=f"Error updating endpoint status: {e}")

async def get_existing_programs():
    try:
        data = db_ops.query_operations().get_all_programs()

        result = []

        if data is not None:
            for row in data:
                entry = {
                    'id': row[0],
                    'program_name': row[1],
                    'program_url': row[2],
                    'acquisitions': row[3],
                    'email': row[4],
                    'report_form': row[5],
                    'created_at': str(row[6])
                }
                result.append(entry)

            return JSONResponse(content=result, status_code=200)
        else:
            return None
    
    except Exception as e:
        logger.exception("Error getting programs")
        raise HTTPException(status_code=500, detail=f"Error getting programs: {e}")
    
async def get_existing_scans():
    try:
        data = db_ops.query_operations().get_all_scannames()

        if data is not None:
            flattened = [item[0] for item in data]  # Flatten the list
            unique_items = sorted(set(flattened))   # Remove duplicates and sort
            return JSONResponse(content={"scan_name": unique_items}, status_code=200)
        else:
            return None
    
    except Exception as e:
        logger.exception("Error in getting scan names")
        raise HTTPException(status_code=500, detail=f"Error in getting scan names: {e}")

async def add_new_endpoints(scan_name, endpoint, file, scan_options):
    
    current_data = {
        'program_id': None,
        'target_id': None,
        'scan_name': scan_name,
        'status': 'active',
        'url': None,
        'old_status_code': None,
        'new_status_code': None,
        'old_response_size': None,
        'new_response_size': None,
        'old_body_hash': None,
        'new_body_hash': None,
        'old_body_file_path': None,
        'new_body_file_path': None,
        'change_detected_at': None,
        'need_review': False
    }
    
    try:
        if scan_name is None:
            raise HTTPException(status_code=400, detail="Scan name not provided.")
        
        if not endpoint and not file:
            raise HTTPException(status_code=400, detail="Provide either an endpoint or a file.")
        
        if endpoint and file:
            raise HTTPException(status_code=400, detail="Provide either an endpoint or a file at a time.")

        # Parse scan_options if provided
        if scan_options:
            try:
                scan_options = json.loads(scan_options)
            except json.JSONDecodeError:
                return JSONResponse(content={"error": "Invalid format for scanOptions."}, status_code=400)

        # Process endpoint input
        if endpoint:
            result = urlparse(endpoint)
            if result.scheme in ('http', 'https') and result.netloc != '':
                current_data['url'] = endpoint
                try:
                    domain_name = get_domain_from_url(endpoint)
                    ids = db_ops.query_operations().get_target_and_program_id(domain_name)
                    if ids is not None:
                        target_id, program_id = ids
                    else: 
                        target_id = None
                        program_id = None 
                        
                    if program_id is not None:
                        logger.info(f"Program Id found for target_domain {domain_name}")
                        current_data['program_id'] = program_id
                    else:
                        logger.warning(f"Program Id not found for target_domain {domain_name}. Continuing with null value")
                        
                    if target_id is not None:
                        current_data['target_id'] = target_id
                        logger.info(f"Targer Id found for target_domain {domain_name}")
                    else:
                        logger.warning(f"Target Id not found for target_domain {domain_name}. Continuing with null value")

                    db_ops.insert_operations().insert_endpoint(current_data)
                    logger.info(f"New endpoint added to DB: {endpoint}")
                    return JSONResponse(content={"message": f"Endpoint Added: {endpoint}"}, status_code=200)
                except Exception as e:
                    logger.exception("Error: Unable to add new endpoint to DB")
                    return JSONResponse(content={"message": "Error: Unable to add new endpoint to DB"}, status_code=500)
            else:
                logger.info(f"Invalid Endpoint {endpoint}")

        # Process file input
        if file:
            scan_dir = f"{root_Data_Dir}/monitoring/{scan_name}"
            file_location = f"{scan_dir}/{file.filename}"
            os.makedirs(scan_dir, exist_ok=True)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open(file_location, "r") as file_content:
                all_lines = file_content.readlines()
                valid_urls = [url for url in all_lines if urlparse(url).scheme in ["http", "https"] and urlparse(url).netloc]
                for line in valid_urls:
                    endpoint = line.strip()
                    current_data['url'] = endpoint
                    try:
                        domain_name = get_domain_from_url(endpoint)
                        ids = db_ops.query_operations().get_target_and_program_id(domain_name)
                        if ids is not None:
                            target_id, program_id = ids
                        else: 
                            target_id = None
                            program_id = None 
                            
                        if program_id is not None:
                            logger.info(f"Program Id found for target_domain {domain_name}")
                            current_data['program_id'] = program_id
                        else:
                            logger.warning(f"Program Id not found for target_domain {domain_name}. Continuing with null value")
                            
                        if target_id is not None:
                            current_data['target_id'] = target_id
                            logger.info(f"Targer Id found for target_domain {domain_name}")
                        else:
                            logger.warning(f"Target Id not found for target_domain {domain_name}. Continuing with null value")
                            
                        db_ops.insert_operations().insert_endpoint(current_data)
                    except Exception as e:
                        logger.exception("Error: Unable to add new endpoint to DB", endpoint)
                        return JSONResponse(content={"message": "Error: Unable to add new endpoint to DB"}, status_code=500)
        
                endpoints_from_file = [line.strip() for line in all_lines if line.strip()]
            return JSONResponse(content={"message": f"Endpoints Added [{len(endpoints_from_file)}]"}, status_code=200)
        
    except Exception as e:
        error = logging.exception("Error", exc_info=True)
        return {JSONResponse(content={"error": error}, status_code=500)}


def get_domain_from_url(url):
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        # Ensure the URL has a valid scheme and netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.debug("Invalid URL provided")
        return parsed_url.netloc
    except Exception as e:
        logger.debug(f"Error parsing URL: {e}")
