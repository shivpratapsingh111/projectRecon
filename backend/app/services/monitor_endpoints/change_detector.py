# External imports
import pytz, os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

# Internal imports
from app.interface.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG

# Initialization
logger = setup_logger(
    __name__, log_file_path="service", enable_debug=LOG_LEVEL_DEBUG
)

@dataclass
class ChangeMetadata:
    field_name: str
    old_value: Any
    new_value: Any

@dataclass
class EndpointData:
    id: str
    url: str
    old_status_code: Optional[int]
    new_status_code: int
    old_response_size: Optional[int]
    new_response_size: int
    old_body_hash: Optional[str]
    new_body_hash: str
    old_body_file_path: Optional[str]
    new_body_file_path: str
    change_detected_at: Optional[datetime]
    need_review: bool = False


# Logic
class FieldTracker:
    """Handles field comparisons and change tracking"""

    def __init__(self):
        self.fields_to_track = {
            "status_code": self._compare_values,
            "response_size": self._compare_values,
            "body_hash": self._compare_values,
            "body_file_path": self._compare_paths,
        }

    def _compare_values(self, old: Any, new: Any) -> bool:
        """Compare simple values"""
        return old != new and new is not None

    def _compare_paths(self, old_path: Optional[str], new_path: Optional[str]) -> bool:
        """Compare file paths and ensure they exist"""
        if not new_path:
            return False
        return old_path != new_path and os.path.exists(new_path)

    def track_changes(
        self, previous: Dict[str, Any], current: Dict[str, Any]
    ) -> List[ChangeMetadata]:
        """Track changes between previous and current data"""
        changes = []

        logger.debug(f"Previous Value {previous}")
        logger.debug(f"Current Value {current}")

        old_body_hash = previous["new_body_hash"]
        new_body_hash = current["new_body_hash"]

        if old_body_hash != new_body_hash:
            changes.append(
                ChangeMetadata(
                    field_name="body_hash",
                    old_value=old_body_hash,
                    new_value=new_body_hash,
                )
            )

        return changes


# ---


class EndpointChangeDetector:
    def __init__(self, db_ops):
        self.db_ops = db_ops
        self.field_tracker = FieldTracker()

    def _rotate_data(
        self, previous_data: Dict[str, Any], current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Rotate old and new values in the data"""
        rotated_data = current_data.copy()

        for field in ["status_code", "response_size", "body_hash", "body_file_path"]:
            old_field = f"old_{field}"
            new_field = f"new_{field}"

            old_body_file_path = current_data["old_body_file_path"]
            # Previous new value becomes the new old value
            rotated_data[old_field] = previous_data[new_field]

            # Current new value stays as is
            rotated_data[new_field] = current_data[new_field]
            rotated_data["old_body_file_path"] = old_body_file_path

            logger.debug(f"Rotated {field}:")
            logger.debug(f"Old: {rotated_data[old_field]}")
            logger.debug(f"New: {rotated_data[new_field]}")

        return rotated_data

    # ---

    def _handle_file_rotation(
        self, previous_data: Dict[str, Any], current_data: Dict[str, Any]
    ) -> None:
        """Handle file rotation for response bodies"""
        old_path = previous_data.get("new_body_file_path")
        new_path = current_data.get("new_body_file_path")

        if old_path and new_path and old_path != new_path:
            try:
                # Keep only the two most recent files
                if os.path.exists(old_path):
                    if previous_data.get("old_body_file_path"):
                        try:
                            os.remove(previous_data["old_body_file_path"])
                            logger.debug(
                                f"Removed old file: {previous_data['old_body_file_path']}"
                            )
                        except OSError as e:
                            logger.warning(f"Could not remove old file: {e}")

                logger.debug(
                    f"File rotation complete. New file: {new_path}, Old file: {old_path}"
                )
            except Exception as e:
                logger.exception(f"Error during file rotation: {e}")

    # ---

    def detect_and_update_changes(
        self, previous_data: Dict[str, Any], current_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Detect changes between previous and current endpoint data and update the database accordingly.
        Returns (changes_detected: bool, changed_fields: List[str])
        """
        try:
            # Track changes
            changes = self.field_tracker.track_changes(previous_data, current_data)

            # Rotate data
            updated_data = self._rotate_data(previous_data, current_data)

            # Handle file rotation
            self._handle_file_rotation(previous_data, updated_data)

            # Update timestamp
            if changes:

                if (
                    previous_data["old_status_code"] is not None
                    or previous_data["new_status_code"] is not None
                ):
                    updated_data["change_detected_at"] = datetime.now(
                        pytz.timezone("Asia/Kolkata")
                    )
                    updated_data["need_review"] = True

                    # Update database with changes
                    self._update_database(previous_data["id"], updated_data, changes)

                    changed_fields = [change.field_name for change in changes]
                    logger.info(
                        f"Changes detected for {updated_data['url']}: {', '.join(changed_fields)}"
                    )
                    return True, changed_fields
                else:
                    logger.info("Running For the first time")
                    self._update_database(previous_data["id"], updated_data, changes)

                    changed_fields = [change.field_name for change in changes]
                    logger.info(
                        f"Changes detected for {updated_data['url']}: {', '.join(changed_fields)}"
                    )
                    return True, changed_fields
            else:
                # Update timestamp only
                self.db_ops.update_operations().update_endpoint_timestamp(
                    previous_data["id"]
                )
                logger.debug(
                    f"No changes detected for {updated_data['url']}, timestamp updated"
                )
                return False, []

        except Exception as e:
            logger.exception(
                f"Error in change detection for {current_data.get('url', 'unknown URL')}: {e}"
            )
            raise

    # ---

    def _update_database(
        self,
        endpoint_id: str,
        update_data: Dict[str, Any],
        changes: List[ChangeMetadata],
    ) -> None:
        """Update the database with detected changes"""
        try:
            self.db_ops.update_operations().update_endpoint_data(
                endpoint_id, update_data
            )

            change_summary = ", ".join(f"{change.field_name}" for change in changes)
            logger.info(
                f"Database updated for {update_data['url']} with changes: {change_summary}"
            )

        except Exception as e:
            logger.exception(f"Database update failed for endpoint {endpoint_id}: {e}")
            raise
