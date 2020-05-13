from schematics.models import Model
from schematics.types import ListType, ModelType, UUIDType, URLType, StringType


class TaskData(Model):
    task_key = UUIDType(required=True)
    datapoint_uri = URLType(required=True, min_length=10)
    datapoint_hash = StringType(required=True, min_length=10)


class TaskDataList(Model):
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
    items = ListType(ModelType(TaskData))


def get_taskdata_model(data: list, **kwargs) -> TaskDataList:
    return TaskDataList({"items": data})
