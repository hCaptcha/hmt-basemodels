from schematics.models import Model, ValidationError
from schematics.types import ListType, ModelType, UUIDType, URLType, StringType


class TaskDataEntry(Model):
    """
    Taskdata file format:

    [
      {
        "task_key": "407fdd93-687a-46bb-b578-89eb96b4109d",
        "datapoint_uri": "https://domain.com/file1.jpg",
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      },
      {
        "task_key": "20bd4f3e-4518-4602-b67a-1d8dfabcce0c",
        "datapoint_uri": "https://domain.com/file2.jpg",
        "datapoint_hash": "f4acbe8562907183a484498ba901bfe5c5503aaa"
      }
    ]
    """
    task_key = UUIDType()
    datapoint_uri = URLType(required=True, min_length=10)
    datapoint_hash = StringType()


def validate_taskdata_entry(value: dict):
    """ Validate taskdata entry """
    if not isinstance(value, dict):
        raise ValidationError("taskdata entry should be dict")

    TaskDataEntry(value).validate()
