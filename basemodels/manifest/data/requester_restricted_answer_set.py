from requests import RequestException
from schematics.models import ValidationError
from .helpers import validate_content_type


def extract_answer_uri(restricted_answer_set: dict) -> list:
    """Extract the answer_uri from the answer set"""
    answer_uris = []
    for _, value in restricted_answer_set.items():
        if isinstance(value, dict) and value.get("answer_example_uri"):
            answer_uris.append(value["answer_example_uri"])

    return answer_uris


def validate_requester_restricted_answer_set_uris(restricted_answer_set: dict) -> None:
    """Validate requester restricted entry"""
    if not isinstance(restricted_answer_set, dict):
        raise ValidationError("Requester restricted set should be a dict")
    uris = extract_answer_uri(restricted_answer_set)
    for uri in uris:
        try:
            validate_content_type(uri)
        except RequestException as e:
            raise ValidationError(f"requester example image content type ({uri}) validation failed") from e
        except ValidationError as e:
            raise ValidationError(f"requester example image for {uri} has unsupported type") from e
