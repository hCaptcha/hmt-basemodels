from typing import Union
from requests import RequestException
from pydantic import ValidationError
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
            raise ValidationError(f"Not supported format for requester_question_example.")
    except RequestException as e:
        raise ValidationError(
            f"could not retrieve requester example ({uri_val})",
            ExampleResourceModel
        ) from e
    except ValidationError as e:
        raise ValidationError(
            f"requester example image for {uri_val} has unsupported type",
            ExampleResourceModel
        ) from e
