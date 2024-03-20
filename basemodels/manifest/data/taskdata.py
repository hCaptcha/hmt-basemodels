from typing import Dict, Optional, Union, Any
from uuid import UUID

import requests
from pydantic.v1 import BaseModel, HttpUrl, validate_model, ValidationError, validator, root_validator
from pydantic.v1.error_wrappers import ErrorWrapper
from requests import RequestException

from basemodels.constants import SUPPORTED_CONTENT_TYPES


# New type
class AtLeastTenCharUrl(HttpUrl):
    min_length = 10


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

    task_key: Optional[UUID]
    datapoint_uri: Optional[HttpUrl]
    datapoint_text: Optional[Dict[str, str]]

    @validator("datapoint_uri", always=True)
    def validate_datapoint_uri(cls, value):
        if value and len(value) < 10:
            raise ValidationError("datapoint_uri need to be at least 10 char length.")
        return value

    @validator("metadata")
    def validate_metadata(cls, value):
        if value is None:
            return value

        if len(value) > 10:
            raise ValidationError("10 key max. in metadata")

        if len(str(value)) > 1024:
            raise ValidationError("metadata should be < 1024")

        return value

    datapoint_hash: Optional[str]
    metadata: Optional[Dict[str, Optional[Union[str, int, float, Dict[str, Any]]]]]

    @root_validator
    def validate_datapoint_text(cls, values):
        """
        Validate datapoint_uri.

        Raise error if no datapoint_text and no value for URI.
        """
        if not values.get("datapoint_uri") and not values.get("datapoint_text"):
            raise ValueError("datapoint_uri is missing.")
        return values


def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    try:
        response = requests.head(uri, timeout=(3.5, 5))
        response.raise_for_status()
    except RequestException as e:
        raise ValidationError(
            [
                ErrorWrapper(ValueError(f"taskdata content type ({uri}) validation failed"), "datapoint_uri")
            ],
            TaskDataEntry
        ) from e

    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValidationError(
            [
                ErrorWrapper(
                    ValueError(f"taskdata entry datapoint_uri has unsupported type {content_type}"),
                    "datapoint_uri"
                )
            ],
            TaskDataEntry
        )


def validate_taskdata_entry(value: dict, validate_image_content_type: bool) -> None:
    """Validate taskdata entry"""
    if not isinstance(value, dict):
        raise ValidationError("taskdata entry should be dict", TaskDataEntry())

    *_, validation_error = validate_model(TaskDataEntry, value)
    if validation_error:
        raise validation_error

    if validate_image_content_type:
        validate_content_type(value["datapoint_uri"])
