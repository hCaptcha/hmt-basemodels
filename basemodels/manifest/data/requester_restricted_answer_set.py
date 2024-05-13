from requests import RequestException
from pydantic import ValidationError
from .helpers import validate_content_type
from basemodels.helpers import raise_validation_error


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
        raise ValueError("Requester restricted set should be a dict")
    uris = extract_answer_uri(restricted_answer_set)
    for uri in uris:
        try:
            validate_content_type(uri)
        except RequestException as e:
            raise_validation_error(
                location=("requester_restricted_answer_set",),
                error_message=f"could not retrieve requester restricted answer set example uri ({uri})",
            )
        except ValidationError as e:
            raise_validation_error(
                location=("requester_restricted_answer_set",),
                error_message=f"requester restricted answer set uri({uri}) content type failed validation: {e.title}",
            )
