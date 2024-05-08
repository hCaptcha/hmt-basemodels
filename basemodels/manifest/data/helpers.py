import requests
from pydantic import BaseModel, HttpUrl

from basemodels.constants import SUPPORTED_CONTENT_TYPES
from basemodels.helpers import raise_validation_error


class ExampleResourceModel(BaseModel):
    answer_example_uri: HttpUrl


def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    response = requests.head(uri, timeout=(3.5, 5))
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"Unsupported type {content_type}",
        )
