from typing import List, Optional, Union
from uuid import UUID

import requests
from pydantic import BaseModel, HttpUrl, ConfigDict
from requests import RequestException
from typing_extensions import Literal

from basemodels.constants import SUPPORTED_CONTENT_TYPES, BaseJobTypesEnum
from basemodels.helpers import raise_validation_error


def create_wrapper_model(type):
    class WrapperModel(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        data: Optional[type] = None

    return WrapperModel


def validate_wrapper_model(Model, data):
    Model.validate({"data": data})


groundtruth_entry_key_type = HttpUrl
GroundtruthEntryKeyModel = create_wrapper_model(groundtruth_entry_key_type)
"""
Groundtruth file format for `image_label_binary` job type:

{
  "https://domain.com/file1.jpeg": ["false", "false", "false"],
  "https://domain.com/file2.jpeg": ["true", "true", "true"]
}
"""
ilb_groundtruth_entry_type = List[Literal["true", "false"]]
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
ilmc_groundtruth_entry_type = List[List[str]]
ILMCGroundtruthEntryModel = create_wrapper_model(ilmc_groundtruth_entry_type)


class ILASGroundtruthEntry(BaseModel):
    entity_name: Optional[Union[int, float]] = None
    entity_type: str
    entity_coords: List[Union[int, float]]


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
ilas_groundtruth_entry_type = List[List[ILASGroundtruthEntry]]
ILASGroundtruthEntryModel = create_wrapper_model(ilas_groundtruth_entry_type)


class IDDGroundtruthEntry(BaseModel):
    entity_name: UUID
    entity_type: Optional[str]
    entity_coords: List[int]


"""
Groundtruth file format for `image_drag_drop` job type

{
  "81fb76f3-3906-4fbd-8168-9dff208860a5": [
    {
      "entity_name": "04606112-4b9d-455f-8f43-9cc1a9bca185",
      "entity_type": "default",
      "entity_coords": [275, 184]
    }
  ]
}
"""
idd_groundtruth_entry_type = List[IDDGroundtruthEntry]
IDDGroundtruthEntryModel = create_wrapper_model(idd_groundtruth_entry_type)

idd_groundtruth_entry_key_type = UUID
IDDGroundtruthEntryKeyModel = create_wrapper_model(idd_groundtruth_entry_key_type)


class TLMSSGroundTruthEntry(BaseModel):
    start: int
    end: int
    label: str


"""
Groundtruth file format for `text_label_multiple_span_select` job type

{
  "https://domain.com/file1.txt": [
    {
      "start": 0,
      "end": 4,
      "label": "0"
    }
  ]
}
"""
tlmss_groundtruth_entry_type = List[TLMSSGroundTruthEntry]
TLMSSGroundTruthEntryModel = create_wrapper_model(tlmss_groundtruth_entry_type)


groundtruth_entry_models_map = {
    "image_label_binary": ILBGroundtruthEntryModel,
    "image_label_multiple_choice": ILMCGroundtruthEntryModel,
    "image_label_area_select": ILASGroundtruthEntryModel,
    "text_label_multiple_span_select": TLMSSGroundTruthEntryModel,
    "image_drag_drop": IDDGroundtruthEntryModel,
}


def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    try:
        response = requests.head(uri, timeout=(3.5, 5))
        response.raise_for_status()
    except RequestException as e:
        raise_validation_error(
            location=("groundtruth_uri",),
            error_message=f"groundtruth content type ({uri}) validation failed",
            input_data={"groundtruth_uri": uri}
        )

    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise_validation_error(
            location=("groundtruth_uri",),
            error_message=f"groundtruth entry has unsupported type {content_type}",
            input_data={"groundtruth_uri": uri}
        )


def validate_groundtruth_entry(
    key: str,
    value: Union[dict, list],
    request_type: str,
    validate_image_content_type: bool,
):
    """Validate key & value of groundtruth entry based on request_type"""
    groundtruth_entry_value_model_class = groundtruth_entry_models_map.get(request_type)
    groundtruth_entry_key_model_class = GroundtruthEntryKeyModel

    if groundtruth_entry_value_model_class is None:
        return

    if request_type == BaseJobTypesEnum.image_drag_drop:
        groundtruth_entry_key_model_class = IDDGroundtruthEntryKeyModel

    validate_wrapper_model(groundtruth_entry_key_model_class, key)
    validate_wrapper_model(groundtruth_entry_value_model_class, value)

    if validate_image_content_type:
        validate_content_type(key)
