import uuid
import requests
from requests.exceptions import RequestException
from typing_extensions import Literal
from typing import Dict, Callable, Any, Union, Type, List, Optional
from enum import Enum
from uuid import UUID
from .data.groundtruth import validate_groundtruth_entry
from .data.taskdata import validate_taskdata_entry
from pydantic import BaseModel, validator, ValidationError, validate_model, HttpUrl
from pydantic.fields import Field
from decimal import Decimal

# Validator function for taskdata and taskdata_uri fields
def validator_taskdata_uri(cls, value, values, **kwargs):
    taskdata = values.get('taskdata')
    taskdata_uri = values.get('taskdata_uri')
    if taskdata is not None and len(taskdata) > 0 and taskdata_uri is not None:
        raise ValidationError(u'Specify only one of taskdata {} or taskdata_uri {}'.format(taskdata, taskdata_uri))
    return value

# A validator function for UUID fields
def validate_uuid(cls, value):
    return value or uuid.uuid4()

# Base job types
class BaseJobTypesEnum(str, Enum):
    image_label_binary = "image_label_binary"
    image_label_multiple_choice = "image_label_multiple_choice"
    text_free_entry = "text_free_entry"
    text_multiple_choice_one_option = "text_multiple_choice_one_option"
    text_multiple_choice_multiple_options = "text_multiple_choice_multiple_options"
    image_label_area_adjust = "image_label_area_adjust"
    image_label_area_select = "image_label_area_select"
    image_label_single_polygon = "image_label_single_polygon"
    image_label_multiple_polygons = "image_label_multiple_polygons"
    image_label_semantic_segmentation_one_option = "image_label_semantic_segmentation_one_option"
    image_label_semantic_segmentation_multiple_options = "image_label_semantic_segmentation_multiple_options"
    image_label_text = "image_label_text"
    multi_challenge = "multi_challenge"

# Return a request type validator function
class RequestTypeValidator(object):
    def __init__(self, multi_challenge: bool = True):
        self.multi_challenge = multi_challenge
    def validate(self, cls, value, values):
        """
        validate request types for all types of challenges
        multi_challenge should always have multi_challenge_manifests
        """
        if value == BaseJobTypesEnum.multi_challenge:
            if not self.multi_challenge:
                raise ValidationError("multi_challenge request is not allowed here.")
            if "multi_challenge_manifests" not in values:
                raise ValidationError("multi_challenge requires multi_challenge_manifests.")
        elif value in [BaseJobTypesEnum.image_label_multiple_choice, BaseJobTypesEnum.image_label_area_select]:
            if values.get('multiple_choice_min_choices', 1) > values.get('multiple_choice_max_choices', 1):
                raise ValidationError(
                    "multiple_choice_min_choices cannot be greater than multiple_choice_max_choices")
        return value

# Shape types enum
class ShapeTypes(str, Enum):
    point = "point"
    bounding_box = "bounding_box"
    polygon = "polygon"

class Model(BaseModel):
    def to_primitive(self):
        return self.dict()

    # Helper function for using in the unittest
    def check(self, return_new=False):
        self.__class__.validate(self)
        out_dict, _, validation_error = validate_model(self.__class__, self.__dict__)
        if validation_error:
            raise validation_error

        # For compatibility with tests
        if return_new:
            return self.__class__(**out_dict)

class Webhook(Model):
    """ Model for webhook configuration """
    webhook_id: UUID
    chunk_completed: Optional[List[str]]
    job_completed: Optional[List[str]]

    # States that might be interesting later
    # job_skipped: List[str] = None
    # job_inserted : List[str] = None
    # job_activated : List[str] = None


class TaskData(Model):
    """ objects within taskdata list in Manifest """
    task_key: UUID
    datapoint_uri: HttpUrl

    @validator("datapoint_uri", always=True)
    def validate_datapoint_uri(cls, value):
        if len(value) < 10:
            raise ValidationError("datapoint_uri need to be at least 10 char length.")

    datapoint_hash: str = Field(..., min_length=10, strip_whitespace=True)


class RequestConfig(Model):
    """ definition of the request_config object in manifest """
    version: int = 0
    shape_type: Optional[ShapeTypes]
    min_points: Optional[int]
    max_points: Optional[int]
    min_shapes_per_image: Optional[int]
    max_shapes_per_image: Optional[int]
    restrict_to_coords: Optional[bool]
    minimum_selection_area_per_shape: Optional[int]
    multiple_choice_max_choices: Optional[int] = 1
    multiple_choice_min_choices: Optional[int] = 1


class InternalConfig(Model):
    """ discarded from incoming manifests """
    exchange: Optional[Dict[str, Union[str, int, float]]]
    reco: Optional[Dict[str, Union[str, int, float]]]
    repo: Optional[Dict[str, Union[str, int, float]]]
    other: Optional[Dict[str, Union[str, int, float]]]
    # Accept one layer of nested
    mitl: Optional[Dict[str, Union[str, int, float, Dict[str, Union[str, int, float]]]]]

    class Config:
        arbitrary_types_allowed = True


class NestedManifest(Model):
    """ The nested manifest description for multi_challenge jobs """
    # We will set a default dynamic value for job_id
    job_id: Optional[UUID]
    validate_job_id = validator('job_id', always=True, allow_reuse=True)(validate_uuid)

    request_type: BaseJobTypesEnum
    validate_request_type = validator('request_type', allow_reuse=True, \
            always=True)(RequestTypeValidator(multi_challenge=False).validate)
    requester_restricted_answer_set: Optional[Dict[str, Dict[str, str]]]

    @validator('requester_restricted_answer_set', always=True)
    def validate_requester_restricted_answer_set(cls, value, values, **kwargs):
        """image_label_area_select should always have a single RAS set"""

        # validation runs before other params, so need to handle missing case
        if "request_type" not in values:
            raise ValidationError("request_type missing")
        if values['request_type'] == BaseJobTypesEnum.image_label_area_select:
            if not value or len(value.keys()) == 0:
                value = {'label': {}}
                values['requester_restricted_answer_set'] = value
        return value

    requester_description: Optional[str]
    requester_max_repeats: int = 100
    requester_min_repeats: int = 1
    requester_question: Optional[Dict[str, str]]
    requester_question_example: Optional[Union[HttpUrl, List[HttpUrl]]]

    @validator('requester_question_example')
    def validate_requester_question_example(cls, value, values, **kwargs):
        # validation runs before other params, so need to handle missing case
        if not ("request_type" in values):
            raise ValidationError("request_type missing")

        # based on https://github.com/hCaptcha/hmt-basemodels/issues/27#issuecomment-590706643
        supports_lists = [
            BaseJobTypesEnum.image_label_area_select, BaseJobTypesEnum.image_label_binary
        ]

        if isinstance(value, list) and not values['request_type'] in supports_lists:
            raise ValidationError("Lists are not allowed in this challenge type")
        return value

    unsafe_content: bool = False
    requester_accuracy_target: float = 0.1

    request_config: Optional[RequestConfig]

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri: Optional[HttpUrl]
    groundtruth: Optional[str]

    @validator('groundtruth', always=True)
    def validate_groundtruth(cls, v, values, **kwargs):
        if "groundtruth_uri" in values and "groundtruth" in values:
            raise ValidationError("Specify only groundtruth_uri or groundtruth, not both.")
        return v

    # Configuration id -- XXX LEGACY
    confcalc_configuration_id: Optional[str]
    webhook: Optional[Webhook]

    class Config:
        arbitrary_types_allowed = True


class Manifest(Model):
    """ The manifest description. """
    job_mode: Literal["batch", "online", "instant_delivery"]
    
    # We will set a default dynamic value for job_api_key
    job_api_key: Optional[UUID]
    validate_job_api_key = validator('job_api_key', always=True, allow_reuse=True)(validate_uuid)

    # We will set a default dynamic value for job_id
    job_id: Optional[UUID]
    validate_job_id = validator('job_id', always=True, allow_reuse=True)(validate_uuid)

    job_total_tasks: Optional[int]
    multi_challenge_manifests: Optional[List[NestedManifest]]
    request_type: BaseJobTypesEnum
    validate_request_type = validator('request_type', allow_reuse=True, \
            always=True)(RequestTypeValidator().validate)

    requester_restricted_answer_set: Optional[Dict[str, Dict[str, str]]]

    @validator('requester_restricted_answer_set', always=True)
    def validate_requester_restricted_answer_set(cls, value, values, **kwargs):
        """image_label_area_select should always have a single RAS set"""
        # validation runs before other params, so need to handle missing case
        if not ("request_type" in values):
            raise ValidationError("request_type missing")

        if values['request_type'] == BaseJobTypesEnum.image_label_area_select:
            if not value or len(value.keys()) == 0:
                value = {'label': {}}
                values['requester_restricted_answer_set'] = value
        return value

    requester_description: Optional[str]
    requester_max_repeats: int = 100
    requester_min_repeats: int = 1
    requester_question: Optional[Dict[str, str]]

    requester_question_example: Optional[Union[HttpUrl, List[HttpUrl]]]

    @validator('requester_question_example')
    def validate_requester_question_example(cls, value, values, **kwargs):
        # validation runs before other params, so need to handle missing case
        if not ("request_type" in values):
            raise ValidationError("request_type missing")

        # based on https://github.com/hCaptcha/hmt-basemodels/issues/27#issuecomment-590706643
        supports_lists = [
            BaseJobTypesEnum.image_label_area_select, BaseJobTypesEnum.image_label_binary
        ]

        if isinstance(value, list) and not (values['request_type'] in supports_lists):
            raise ValidationError("Lists are not allowed in this challenge type")
        return value

    unsafe_content: bool = False
    task_bid_price: Decimal
    oracle_stake: Decimal
    expiration_date: Optional[int]
    requester_accuracy_target: float = 0.1
    manifest_smart_bounty_addr: Optional[str]
    hmtoken_addr: Optional[str]
    minimum_trust_server: float = 0.1
    minimum_trust_client: float = 0.1
    recording_oracle_addr: str
    reputation_oracle_addr: str
    reputation_agent_addr: str
    requester_pgp_public_key: Optional[str]
    ro_uri: Optional[str]
    repo_uri: Optional[str]
    batch_result_delivery_webhook: Optional[HttpUrl]
    online_result_delivery_webhook: Optional[HttpUrl]
    instant_result_delivery_webhook: Optional[HttpUrl]

    request_config: Optional[RequestConfig]

    # If taskdata is directly provided
    taskdata: Optional[List[TaskData]]

    # If taskdata is separately stored
    taskdata_uri: Optional[HttpUrl]

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri: Optional[HttpUrl]
    groundtruth: Optional[str]

    @validator('groundtruth', always=True)
    def validate_groundtruth(cls, value, values):
        if "groundtruth_uri" in values and "groundtruth" in values:
            raise ValidationError("Specify only groundtruth_uri or groundtruth, not both.")
        return value

    # internal config options for param tests etc.
    internal_config: Optional[InternalConfig]

    # Configuration id -- XXX LEGACY
    confcalc_configuration_id: Optional[str]
    restricted_audience: Optional[Dict[str, Union[float, List[Dict[str, Dict[str, float]]]]]]

    validate_taskdata_uri = validator('taskdata_uri', allow_reuse=True, always=True)(validator_taskdata_uri)
    validate_taskdata = validator('taskdata', allow_reuse=True, always=True)(validator_taskdata_uri)
    webhook: Optional[Webhook]

    class Config:
        arbitrary_types_allowed = True


def validate_groundtruth_uri(manifest: dict):
    """
    Validate groundtruth_uri 
    Returns entries count if succeeded
    """
    request_type = manifest.get('request_type', '')
    uri_key = "groundtruth_uri"
    uri = manifest.get(uri_key)
    if uri is None:
        return
    try:
        response = requests.get(uri, timeout=1)
        response.raise_for_status()

        entries_count = 0
        data = response.json()
        if isinstance(data, dict):
            for k, v in data.items():
                entries_count += 1
                validate_groundtruth_entry(k, v, request_type)
        else:
            for v in data:
                entries_count += 1
                validate_groundtruth_entry("", v, request_type)

    except (ValidationError, RequestException) as e:
        raise ValidationError(f"{uri_key} validation failed: {e}", Manifest) from e

    if entries_count == 0:
        raise ValidationError(f"fetched {uri_key} is empty", Manifest)

def validate_taskdata_uri(manifest: dict):
    """
    Validate taskdata_uri 
    Returns entries count if succeeded
    """
    uri_key = "taskdata_uri"
    uri = manifest.get(uri_key)
    if uri is None:
        return
    try:
        response = requests.get(uri, timeout=1)
        response.raise_for_status()

        entries_count = 0
        data = response.json()
        for v in data:
            entries_count += 1
            validate_taskdata_entry(v)
    except (ValidationError, RequestException) as e:
        raise ValidationError(f"{uri_key} validation failed: {e}", Manifest) from e

    if entries_count == 0:
        raise ValidationError(f"fetched {uri_key} is empty", Manifest)

def validate_manifest_uris(manifest: dict):
    """ Fetch & validate manifest's remote objects """
    validate_taskdata_uri(manifest)
    validate_groundtruth_uri(manifest)
