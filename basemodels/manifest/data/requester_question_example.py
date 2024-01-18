from typing import Union

from pydantic.v1.error_wrappers import ErrorWrapper
from requests import RequestException
from pydantic.v1 import ValidationError
from .helpers import validate_content_type, ExampleResourceModel


def validate_requester_example_image(
    value: Union[str, list],
):
    """Validate requester example image"""
    uri_val = ""
    try:
        if isinstance(value, str):
            uri_val = value
            validate_content_type(value)
        elif isinstance(value, list):
            for uri in value:
                uri_val = uri
                validate_content_type(uri)
        else:
            raise ValueError(f"Not supported format for requester_question_example.")
    except RequestException as e:
        raise ValidationError(
            [
                ErrorWrapper(ValueError(f"could not retrieve requester example ({uri_val})"), "answer_example_uri")
            ],
            ExampleResourceModel
        ) from e
    except ValidationError as e:
        raise ValidationError(
            [
                ErrorWrapper(
                    ValueError(f"requester example image for {uri_val} has unsupported type"),
                    "answer_example_uri"
                )
            ],
            ExampleResourceModel
        ) from e

