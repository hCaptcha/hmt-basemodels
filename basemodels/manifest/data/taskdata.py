from typing import Dict, Optional, Union, Any, List, Tuple
from uuid import UUID

import requests
from pydantic import BaseModel, AnyHttpUrl, HttpUrl, field_validator, model_validator
from requests import RequestException

from basemodels.constants import SUPPORTED_CONTENT_TYPES
from basemodels.helpers import raise_validation_error


class Entity(BaseModel):
    """Entity configuration"""

    entity_id: UUID
    entity_uri: AnyHttpUrl
    coords: Tuple[int, int]


class TaskDataEntry(BaseModel):
    """
    Taskdata file format:

    [
      {
        "task_key": "407fdd93-687a-46bb-b578-89eb96b4109d",
        "datapoint_uri": "https://domain.com/file1.jpg",
        "datapoint_text": {},
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      },
      {
        "task_key": "20bd4f3e-4518-4602-b67a-1d8dfabcce0c",
        "datapoint_uri": "https://domain.com/file2.jpg",
        "datapoint_text": {},
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      }
    ]
    """

    task_key: Optional[UUID] = None
    datapoint_uri: Optional[HttpUrl] = None
    entities: Optional[List[Entity]] = None
    datapoint_text: Optional[Dict[str, str]] = None
    datapoint_hash: Optional[str] = None
    metadata: Optional[Dict[str, Optional[Union[str, int, float, Dict[str, Any]]]]] = None

    @field_validator("datapoint_uri")
    def validate_datapoint_uri(cls, value):
        if value and len(str(value)) < 10:
            raise ValueError("datapoint_uri need to be at least 10 char length.")
        return value

    @model_validator(mode="before")
    def validate_task_data(cls, values):
        """
        Validate datapoint_uri.

        Raise error if no datapoint_text and no value for URI.
        """
        if not values.get("datapoint_uri") and not values.get("datapoint_text"):
            raise ValueError(f"datapoint_uri is missing. {list(values.keys())}")
        return values

    @field_validator("metadata")
    def validate_metadata(cls, value):
        if value is None:
            return value

        if len(value) > 10:
            raise ValueError("10 key max. in metadata")

        if len(str(value)) > 1024:
            raise ValueError("metadata should be < 1024")

        return value

    datapoint_hash: Optional[str] = None
    metadata: Optional[Dict[str, Optional[Union[str, int, float, Dict[str, Any]]]]] = None


def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    try:
        response = requests.head(uri, timeout=(3.5, 5))
        response.raise_for_status()
    except RequestException as e:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"taskdata content type ({uri}) validation failed",
        )

    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"taskdata entry datapoint_uri has unsupported type {content_type}",
        )


def validate_taskdata_entry(value: dict, validate_image_content_type: bool) -> None:
    """Validate taskdata entry"""
    if not isinstance(value, dict):
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"taskdata entry should be dict",
        )
    task_data = TaskDataEntry(**value)

    if validate_image_content_type:
        validate_content_type(task_data.datapoint_uri)
