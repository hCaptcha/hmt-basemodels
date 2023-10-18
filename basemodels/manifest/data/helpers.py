import requests
from pydantic import ValidationError, BaseModel, HttpUrl
from pydantic.error_wrappers import ErrorWrapper

from basemodels.constants import SUPPORTED_CONTENT_TYPES


class ExampleResourceModel(BaseModel):
    answer_example_uri: HttpUrl


def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    response = requests.head(uri)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValidationError(
            [
                ErrorWrapper(ValueError(f"Unsupported type {content_type}"), "answer_example_uri")
            ],
            ExampleResourceModel
        )
