# External Imports
from fastapi import status
from urllib.parse import urlparse
import traceback, shutil, json, os

# Local Imports
from app.config.db_config import db_config
from app.config.config import ROOT_DATA_DIR
from app.services.monitor_endpoints.db.db_manager import DatabaseManager
from app.services.monitor_endpoints.db.db_operations import DatabaseOperations
from app.logger.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(
    __name__, log_file_path="api_monitor_endpoints", enable_debug=LOG_LEVEL_DEBUG
)
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


# Logic
def get_review_endpoints():
    result = []
    data = db_ops.query_operations().get_need_review_endpoints()
    if data is not None:
        for row in data:
            result.append(
                {
                    "id": row[0],
                    "program_uuid": row[1],
                    "target_id": row[2],
                    "scan_name": row[3],
                    "url": row[4],
                    "change_detected_at": row[5],
                    "old_status_code": row[6],
                    "new_status_code": row[7],
                    "old_response_size": row[8],
                    "new_response_size": row[9],
                    "old_body_file_path": row[10],
                    "new_body_file_path": row[11],
                }
            )

        return {
            "status": True,
            "message": "Successfully fetched existing programs",
            "data": {"content": result},
        }
    else:
        return {
            "status": True,
            "message": "No data found",
            "data": {"content": None},
        }


# ---


def get_response_body_changes(endpoint_id):
    try:
        result = []
        data = db_ops.query_operations().get_endpoint_response_body_filepaths(
            endpoint_id
        )
        if data is not None:
            result.append(
                {"old_body_file_path": data[0], "new_body_file_path": data[1]}
            )
            old_body_file_path = data[0]
            new_body_file_path = data[1]
            try:
                if not os.path.isfile(old_body_file_path) or not os.path.isfile(
                    new_body_file_path
                ):
                    return {
                        "status_code": status.HTTP_404_NOT_FOUND,
                        "status": False,
                        "message": f"One or both files not found",
                    }
            except Exception as e:
                logger.exception(f"Probably, file path is None. {e}")
            try:
                with open(old_body_file_path, "r") as old_file:
                    old_file_content = old_file.read()

                with open(new_body_file_path, "r") as new_file:
                    new_file_content = new_file.read()
            except Exception as e:
                full_trace = traceback.format_exc()
                logger.exception("Error reading files")
                return {
                    "status": False,
                    "message": f"Error while reading response body file",
                    "debug": {"error": str(e), "traceback": full_trace},
                }

            return {
                "status": True,
                "message": "Response body data",
                "data": {
                    "old_response": old_file_content,
                    "new_response": new_file_content,
                },
            }

        else:
            logger.exception("No response body file paths found in database")
            return {
                "status": False,
                "message": f"No response body file paths found in database",
                "debug": {"error": str(e), "traceback": full_trace},
            }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error while reading response body: {e}")
        return {
            "status": False,
            "message": f"Unexpected error while reading response body file",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


def mark_review_endpoints(endpoint_id):
    try:
        db_ops.update_operations().update_need_review_endpoint(endpoint_id)
        return {
            "status": True,
            "message": f"Marked the endpoint as reviewed",
        }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error in marking the endpoint as reviewd: {e}")
        return {
            "status": False,
            "message": f"Unexpected error in marking the endpoint as reviewd, Make sure you provide a valid endpoint ID",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


def update_endpoint_scan_interval(endpoint_id, interval):
    try:
        db_ops.update_operations().update_endpoint_interval(endpoint_id, interval)
        return {
            "status": True,
            "message": f"Updated endpoint scan interval to {interval}",
        }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Unexpected error in updating endpoint scan interval: {e}")
        return {
            "status": False,
            "message": f"Unexpected error in updating endpoint scan interval, Make sure you provide a valid endpoint ID",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


def get_endpoints_by_state(status):
    try:
        data = db_ops.query_operations().get_endpoints_data_by_status(status)
        result = []

        if data is not None:
            for row in data:
                entry = {
                    "id": row[0],
                    "program_uuid": row[1],
                    "program_name": None,
                    "scan_name": row[2],
                    "scan_interval": row[3],
                    "status": row[4],
                    "url": row[5],
                    "new_status_code": row[6],
                    "new_response_size": row[7],
                    "new_body_file_path": row[8],
                    "last_check": str(row[9]),
                }

                program_name = db_ops.query_operations().get_program_name(row[1])
                if program_name:
                    entry["program_name"] = program_name[0][0]
                else:
                    entry["program_name"] = None
                result.append(entry)
            return {
                "status": True,
                "message": "Successfully fetched existing programs",
                "data": {"content": result},
            }
        else:
            return {
                "status": True,
                "message": "No data found",
                "data": {"content": None},
            }

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Error fetching endpoints by status: {e}")
        return {
            "status": False,
            "message": "Error fetching endpoints by status",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


def update_endpoint_status(endpoint_id, status):
    try:
        db_ops.update_operations().update_endpoint_status(endpoint_id, status)
        return {
            "status": True,
            "message": f"Endpoint status updated to {status}",
        }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Error updating endpoint status: {e}")
        return {
            "status": False,
            "message": f"Error updating endpoint status to {status}",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


async def get_existing_programs():
    try:
        data = db_ops.query_operations().get_all_programs()

        result = []

        if data is not None:
            for row in data:
                entry = {
                    "id": row[0],
                    "program_name": row[1],
                    "program_url": row[2],
                    "acquisitions": row[3],
                    "email": row[4],
                    "report_form": row[5],
                    "created_at": str(row[6]),
                }
                result.append(entry)
            return {
                "status": True,
                "message": "Successfully fetched existing programs",
                "data": {"content": result},
            }

        else:
            return {
                "status": True,
                "message": "There are not any existing programs in database",
                "data": {"content": None},
            }

    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Error getting existing programs: {e}")
        return {
            "status": False,
            "message": "Error getting existing programs",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


async def get_existing_scans():
    try:
        data = db_ops.query_operations().get_all_scannames()

        if data is not None:
            flattened = [item[0] for item in data]  # Flatten the list
            unique_items = sorted(set(flattened))  # Remove duplicates and sort
            return {
                "status": True,
                "message": "Successfully fetched existing scans",
                "data": {"scan_names": unique_items},
            }
        else:
            return {
                "status": True,
                "message": "There are not any existing scans in database",
                "data": {"content": None},
            }
    except Exception as e:
        full_trace = traceback.format_exc()
        logger.exception(f"Error in getting scan names: {e}")
        return {
            "status": False,
            "message": "Error in getting scan names",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


async def insert_new_endpoints(scan_name, endpoint, file, scan_options):

    current_data = {
        "program_uuid": None,
        "target_id": None,
        "scan_name": scan_name,
        "status": "active",
        "url": None,
        "old_status_code": None,
        "new_status_code": None,
        "old_response_size": None,
        "new_response_size": None,
        "old_body_hash": None,
        "new_body_hash": None,
        "old_body_file_path": None,
        "new_body_file_path": None,
        "change_detected_at": None,
        "need_review": False,
    }

    try:

        if not endpoint and not file:
            logger.error(
                "Neither endpoint nor file is provided, provide either 'endpoint' or 'file'"
            )
            return {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": False,
                "message": "Neither endpoint nor file is provided, provide either 'endpoint' or 'file'",
            }

        if endpoint and file:
            logger.error(
                "File and endpoint both are provided, provide either 'endpoint' or 'file'"
            )
            return {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "status": False,
                "message": "File and endpoint both are provided, provide either 'endpoint' or 'file'",
            }

        # Parse scan_options if provided
        if scan_options:
            try:
                scan_options = json.loads(scan_options)
            except json.JSONDecodeError:
                return {
                    "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "status": False,
                    "message": "Invalid format for scanOptions",
                }

        # Process endpoint input
        if endpoint:
            parsed = urlparse(endpoint.strip())
            if parsed.scheme in ("http", "https") and parsed.netloc:
                current_data["url"] = endpoint
                try:
                    domain_name = parsed.netloc

                    ids = db_ops.query_operations().get_target_and_program_uuid(
                        domain_name
                    )
                    target_id, program_uuid = ids if ids else (None, None)

                    if program_uuid:
                        logger.info(f"Program ID found for domain {domain_name}")
                        current_data["program_uuid"] = program_uuid
                    else:
                        logger.warning(f"Program ID not found for domain {domain_name}")

                    if target_id:
                        logger.info(f"Target ID found for domain {domain_name}")
                        current_data["target_id"] = target_id
                    else:
                        logger.warning(f"Target ID not found for domain {domain_name}")

                    db_ops.insert_operations().insert_endpoint(current_data)
                    logger.info(f"New endpoint added to DB: {endpoint}")
                    return {
                        "status": True,
                        "message": f"Endpoint added: {endpoint}",
                    }

                except Exception as e:
                    full_trace = traceback.format_exc()
                    logger.exception(f"Error: Unable to add endpoint to DB: {endpoint}")
                    return {
                        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "status": False,
                        "message": f"Unable to add endpoint to DB: {endpoint}",
                        "debug": {"error": str(e), "traceback": full_trace},
                    }
            else:
                logger.info(f"Invalid endpoint format: {endpoint}")

        # Process file input
        if file:
            scan_dir = f"{ROOT_DATA_DIR}/{scan_name}/monitoring"
            file_location = f"{scan_dir}/{file.filename}"
            os.makedirs(scan_dir, exist_ok=True)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            with open(file_location, "r") as file_content:
                all_lines = file_content.readlines()
                valid_urls = []
                for line in all_lines:
                    url = line.strip()
                    parsed = urlparse(url)
                    if parsed.scheme in ["http", "https"] and parsed.netloc:
                        valid_urls.append((url, parsed.netloc))

                success_count = 0
                for endpoint, domain_name in valid_urls:
                    endpoint_data = current_data.copy()
                    endpoint_data["url"] = endpoint
                    try:
                        ids = db_ops.query_operations().get_target_and_program_uuid(
                            domain_name
                        )
                        if ids is not None:
                            target_id, program_uuid = ids
                        else:
                            target_id = None
                            program_uuid = None

                        if program_uuid is not None:
                            logger.info(
                                f"Program Id found for target_domain {domain_name}"
                            )
                            endpoint_data["program_uuid"] = program_uuid
                        else:
                            logger.warning(
                                f"Program Id not found for target_domain {domain_name}. Continuing with null value"
                            )

                        if target_id is not None:
                            endpoint_data["target_id"] = target_id
                            logger.info(
                                f"Target Id found for target_domain {domain_name}"
                            )
                        else:
                            logger.warning(
                                f"Target Id not found for target_domain {domain_name}. Continuing with null value"
                            )

                        db_ops.insert_operations().insert_endpoint(endpoint_data)
                        success_count += 1
                    except Exception as e:
                        full_trace = traceback.format_exc()
                        logger.exception(
                            f"Error: Unable to add this endpoint to DB: {endpoint}"
                        )
                        return {
                            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "status": False,
                            "message": f"Unable to add this endpoint to DB: {endpoint}",
                            "debug": {"error": str(e), "traceback": full_trace},
                        }

            return {
                "status": True,
                "message": f"Endpoints added {success_count} out of {len(all_lines)} lines",
            }

    except Exception as e:
        full_trace = traceback.format_exc()
        return {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "status": False,
            "message": "Something went wrong",
            "debug": {"error": str(e), "traceback": full_trace},
        }


# ---


def get_domain_from_url(url):
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.debug("Invalid URL provided")
        return parsed_url.netloc
    except Exception as e:
        logger.debug(f"Error parsing URL: {e}")
