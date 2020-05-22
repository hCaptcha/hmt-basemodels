from typing import Union
from schematics.models import Model
from schematics.types import StringType, ListType, URLType, ModelType, IntType, FloatType, UnionType


def create_wrapper_model(type):
    class WrapperModel(Model):
        data = type

    return WrapperModel


def validate_wrapper_model(Model, data):
    Model({"data": data}).validate()


groundtruth_entry_key_type = URLType()
GroundtruthEntryKeyModel = create_wrapper_model(groundtruth_entry_key_type)
"""
Groundtruth file format for `image_label_binary` job type:

{
  "https://domain.com/file1.jpeg": ["false", "false", "false"],
  "https://domain.com/file2.jpeg": ["true", "true", "true"]
}
"""
ilb_groundtruth_entry_type = ListType(StringType(choices=["true", "false"]))
ILBGroundtruthEntryModel = create_wrapper_model(ilb_groundtruth_entry_type)
"""
Groundtruth file format for `image_label_multiple_choice` job type:

{
  "https://domain.com/file1.jpeg": [
    ["cat"],
    ["cat"],
    ["cat"]
  ],
  "https://domain.com/file2.jpeg": [
    ["dog"],
    ["dog"],
    ["dog"]
  ]
}
"""
ilmc_groundtruth_entry_type = ListType(ListType(StringType))
ILMCGroundtruthEntryModel = create_wrapper_model(ilmc_groundtruth_entry_type)


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
ILASGroundtruthEntryModel = create_wrapper_model(ilas_groundtruth_entry_type)

groundtruth_entry_models_map = {
    "image_label_binary": ILBGroundtruthEntryModel,
    "image_label_multiple_choice": ILMCGroundtruthEntryModel,
    "image_label_area_select": ILASGroundtruthEntryModel
}


def validate_groundtruth_entry(key: str, value: Union[dict, list], request_type: str):
    """ Validate key & value of groundtruth entry based on request_type """
    GroundtruthEntryValueModel = groundtruth_entry_models_map.get(request_type)

    if GroundtruthEntryValueModel is None:
        return

    validate_wrapper_model(GroundtruthEntryKeyModel, key)
    validate_wrapper_model(GroundtruthEntryValueModel, value)
