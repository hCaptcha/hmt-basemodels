import requests
from requests import RequestException
from schematics.models import Model, ValidationError
from schematics.types import UUIDType, URLType, StringType, DictType, IntType, FloatType, UnionType, BooleanType

from basemodels.constants import SUPPORTED_CONTENT_TYPES


class TaskDataEntry(Model):
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
        "datapoint_text": { "en": "any question here"},
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      }
    ]
    """
    task_key = UUIDType()
    datapoint_uri = URLType()
    datapoint_text = DictType(StringType())
    datapoint_hash = StringType()
    metadata = DictType(
      UnionType([
        StringType(required=False, max_length=256),
        FloatType,
        IntType
      ]),
    required=False)

    def validate_metadata(self, data, value):
        if len(str(value)) > 1024:
            raise ValidationError("metadata should be < 1024")
        return value

    def validate_datapoint_uri(self, data, value):
        """
        Validate datapoint_uri.

        Raise error if no datapoint_text and no value for URI or if length of URI less than 10.
        """
        if not value and not data.get('datapoint_text'):
            raise ValidationError("datapoint_uri is missing.")
        if value and len(value) < 10 and not data.get('datapoint_text'):
            raise ValidationError("datapoint_uri length is less than 10")
        return value


def validate_content_type(uri: str) -> None:
    """ Validate uri content type """
    try:
        response = requests.head(uri)
        response.raise_for_status()
    except RequestException as e:
        raise ValidationError(f"taskdata content type ({uri}) validation failed") from e

    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValidationError(f"taskdata entry datapoint_uri has unsupported type {content_type}")


def validate_taskdata_entry(value: dict, validate_image_content_type: bool) -> None:
    """ Validate taskdata entry """
    if not isinstance(value, dict):
        raise ValidationError("taskdata entry should be dict")

    TaskDataEntry(value).validate()

    if validate_image_content_type:
        validate_content_type(value['datapoint_uri'])
