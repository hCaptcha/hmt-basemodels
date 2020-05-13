from typing import Union
from schematics.models import Model
from schematics.types import StringType, ListType, URLType, BaseType, ModelType, IntType, FloatType, DictType, UnionType


class ILBGroundtruth(Model):
    """
    Groundtruth file format for `image_label_binary` job type:

    {
      "https://domain.com/file1.jpeg": ["false", "false", "false"],
      "https://domain.com/file2.jpeg": ["true", "true", "true"]
    }
    """
    items = BaseType()

    def validate_items(self, data, value):
        for k, v in value.items():
            URLType().validate(k)
            ListType(StringType(choices=["true", "false"])).validate(v)


class ILASGroundtruthDatapoint(Model):
    coords = ListType(UnionType([IntType, FloatType]))


class ILASGroundtruth(Model):
    """
    Groundtruth file format for `image_label_area_select` job type

    {
      "datapoints": [
        {
          "https://domain.com/file1.jpeg": {
            "coords": [303, 183]
          }
        },
        {
          "https://domain.com/file1.jpeg": {
            "coords": [361, 239]
          }
        }
      ]
    }
    """
    datapoints = ListType(DictType(ModelType(ILASGroundtruthDatapoint)), required=True)

    def validate_datapoints(self, data, value):
        for datapoint in value:
            for key in datapoint.keys():
                URLType().validate(key)


def get_groundtruth_model(data: Union[dict, list], request_type: str,
                          **kwargs) -> Union[None, ILBGroundtruth, ILASGroundtruth]:
    """
    Create appropriate groundtruth model based on request_type
    """
    if request_type == 'image_label_binary':
        return ILBGroundtruth({"items": data})
    elif request_type == 'image_label_area_select':
        return ILASGroundtruth(data)

    return None
