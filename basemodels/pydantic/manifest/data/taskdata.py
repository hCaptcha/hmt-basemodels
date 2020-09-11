from typing import Dict
from pydantic import BaseModel, HttpUrl, validate_model, ValidationError, validator
from uuid import UUID
from typing import Optional

# New type
class AtLeastTenCharUrl(HttpUrl):
    min_length = 10

class TaskDataEntry(BaseModel):
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
    task_key: Optional[UUID]
    datapoint_uri: HttpUrl

    @validator("datapoint_uri", always=True)
    def validate_datapoint_uri(cls, value):
        if len(value) < 10:
            raise ValidationError("datapoint_uri need to be at least 10 char length.")

    datapoint_hash: Optional[str]


def validate_taskdata_entry(value: dict):
    """ Validate taskdata entry """
    if not isinstance(value, dict):
        raise ValidationError("taskdata entry should be dict", TaskDataEntry())

    *_, validation_error = validate_model(TaskDataEntry, value)
    if validation_error:
          raise validation_error
