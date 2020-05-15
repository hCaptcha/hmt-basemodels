from typing import Union
from schematics.models import Model
from schematics.types import StringType, ListType, URLType, ModelType, IntType, FloatType, UnionType

groundtruth_entry_key_type = URLType()

"""
Groundtruth file format for `image_label_binary` job type:

{
  "https://domain.com/file1.jpeg": ["false", "false", "false"],
  "https://domain.com/file2.jpeg": ["true", "true", "true"]
}
"""
ilb_groundtruth_entry_type = ListType(StringType(choices=["true", "false"]))

class ILASGroundtruthEntry(Model):
    entity_name = UnionType([IntType, FloatType])
    entity_type = StringType()
    entity_coords = ListType(UnionType([IntType, FloatType]))

"""
Groundtruth file format for `image_label_area_select` job type

{
  "https://domain.com/file1.jpeg": [
    [
      {
        "entity_name": 0,
        "entity_type": "gate",
        "entity_coords": [275, 184, 454, 183, 453, 366, 266, 367]
      }
    ]
  ]
}
"""
ilas_groundtruth_entry_type = ListType(ListType(ModelType(ILASGroundtruthEntry)))

groundtruth_entry_types_map = {
  "image_label_binary": ilb_groundtruth_entry_type,
  "image_label_area_select": ilas_groundtruth_entry_type,
}

def validate_groundtruth_entry(key: str, value: Union[dict, list], request_type: str):
    """ Validate key & value of groundtruth entry based on request_type """
    groundtruth_entry_type = groundtruth_entry_types_map.get(request_type)

    if groundtruth_entry_type is None:
      return

    groundtruth_entry_key_type.validate(key)
    groundtruth_entry_type.validate(value)


