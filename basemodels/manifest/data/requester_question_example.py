from typing import Union

from requests import RequestException
from pydantic import ValidationError
from .helpers import validate_content_type
from basemodels.helpers import raise_validation_error


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
        raise_validation_error(
            location=("requester_question_example",),
            error_message="could not retrieve requester example",
        )
    except ValidationError as e:
        raise_validation_error(
            location=("requester_question_example",),
            error_message=f"requester example image for {uri_val} has unsupported type",
        )
