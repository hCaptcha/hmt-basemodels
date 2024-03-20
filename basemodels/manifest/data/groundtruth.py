from typing import List, Optional, Union

import requests
from pydantic.v1 import BaseModel, HttpUrl, ValidationError, conlist, validator, root_validator, Field
from requests import RequestException
from typing_extensions import Literal

from basemodels.constants import SUPPORTED_CONTENT_TYPES


def create_wrapper_model(type):
    class WrapperModel(BaseModel):
        data: Optional[type]

        class Config:
            arbitrary_types_allowed = True

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
    entity_name: Optional[Union[int, float]]
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
}

def validate_content_type(uri: str) -> None:
    """Validate uri content type"""
    try:
        response = requests.head(uri, timeout=(3.5, 5))
        response.raise_for_status()
    except RequestException as e:
        raise ValidationError(f"groundtruth content type ({uri}) validation failed", GroundtruthEntryKeyModel) from e

    content_type = response.headers.get("Content-Type", "")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ValidationError(
            f"groundtruth entry has unsupported type {content_type}",
            GroundtruthEntryKeyModel,
        )


def validate_groundtruth_entry(
    key: str,
    value: Union[dict, list],
    request_type: str,
    validate_image_content_type: bool,
):
    """Validate key & value of groundtruth entry based on request_type"""
    GroundtruthEntryValueModel = groundtruth_entry_models_map.get(request_type)

    if GroundtruthEntryValueModel is None:
        return

    validate_wrapper_model(GroundtruthEntryKeyModel, key)
    validate_wrapper_model(GroundtruthEntryValueModel, value)

    if validate_image_content_type:
        validate_content_type(key)
