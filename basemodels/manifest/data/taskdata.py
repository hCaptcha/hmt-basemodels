from schematics.models import Model, ValidationError
from schematics.types import UUIDType, URLType, StringType, DictType, IntType, FloatType, UnionType, BooleanType


class TaskDataEntry(Model):
    """
    Taskdata file format:

    [
      {
        "task_key": "407fdd93-687a-46bb-b578-89eb96b4109d",
        "datapoint_uri": "https://domain.com/file1.jpg",
        "datapoint_text": "",
        "is_text_question": False,
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      },
      {
        "task_key": "20bd4f3e-4518-4602-b67a-1d8dfabcce0c",
        "datapoint_uri": "",
        "datapoint_text": "any question here",
        "is_text_question": True,
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      }
    ]
    """
    task_key = UUIDType()
    datapoint_uri = URLType()
    datapoint_text = StringType()
    datapoint_hash = StringType()
    is_text_question = BooleanType()
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

    def validate_datapoint_text(self, data, value):
        if data.get('is_text_question') and not value:
            raise ValidationError("datapoint_text is missing.")
        return value

    def validate_datapoint_uri(self, data, value):
        if not data.get('is_text_question'):
            if not value:
                raise ValidationError("datapoint_uri is missing.")
            if len(value) < 10:
                raise ValidationError("datapoint_uri length is less than 10")
        return value


def validate_taskdata_entry(value: dict):
    """ Validate taskdata entry """
    if not isinstance(value, dict):
        raise ValidationError("taskdata entry should be dict")

    TaskDataEntry(value).validate()
