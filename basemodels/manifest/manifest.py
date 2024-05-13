import json
import uuid
from datetime import datetime

import requests
from pydantic_core import InitErrorDetails
from pydantic_core.core_schema import ValidationInfo
from requests.exceptions import RequestException
from typing_extensions import Literal
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from uuid import UUID, uuid4
from .data.groundtruth import validate_groundtruth_entry
from .data.requester_question_example import validate_requester_example_image
from .data.requester_restricted_answer_set import validate_requester_restricted_answer_set_uris
from .data.taskdata import validate_taskdata_entry, Entity
from pydantic import BaseModel, field_validator, ValidationError, HttpUrl, AnyHttpUrl, model_validator, ConfigDict
from pydantic.fields import Field
from basemodels.manifest.restricted_audience import RestrictedAudience
from basemodels.constants import JOB_TYPES_FOR_CONTENT_TYPE_VALIDATION, BaseJobTypesEnum
from basemodels.helpers import raise_validation_error


# A validator function for UUID fields
def validate_uuid(cls, value):
    return value or uuid.uuid4()


# Return a request type validator function
class RequestTypeValidator(object):
    def __init__(self, multi_challenge: bool = True):
        self.multi_challenge = multi_challenge

    def validate(cls, value, validation_info: ValidationInfo):
        """
        validate request types for all types of challenges
        multi_challenge should always have multi_challenge_manifests
        """
        values = validation_info.data
        if value == BaseJobTypesEnum.multi_challenge:
            if not cls.multi_challenge:
                raise ValueError("multi_challenge request is not allowed here.")
            if "multi_challenge_manifests" not in values:
                raise ValueError("multi_challenge requires multi_challenge_manifests.")
        elif value in [BaseJobTypesEnum.image_label_multiple_choice, BaseJobTypesEnum.image_label_area_select]:
            if values.get("multiple_choice_min_choices", 1) > values.get("multiple_choice_max_choices", 1):
                raise ValueError("multiple_choice_min_choices cannot be greater than multiple_choice_max_choices")
        return value


# Shape types enum
class ShapeTypes(str, Enum):
    point = "point"
    bounding_box = "bounding_box"
    polygon = "polygon"


class Model(BaseModel):
    def to_primitive(self):
        return self.model_dump()

    def check(self, return_new=False):
        validated_obj = self.__class__.model_validate(self.model_dump())
        # For compatibility with tests
        if return_new:
            return validated_obj


class Webhook(Model):
    """Model for webhook configuration"""

    webhook_id: UUID
    chunk_completed: Optional[List[str]] = None
    job_completed: Optional[List[str]] = None

    # States that might be interesting later
    # job_skipped: List[str] = None
    # job_inserted : List[str] = None
    # job_activated : List[str] = None


class TaskData(BaseModel):
    """objects within taskdata list in Manifest"""

    task_key: UUID
    datapoint_uri: Optional[AnyHttpUrl] = None
    entities: Optional[List[Entity]] = None
    polygon: Optional[List[int]] = None
    datapoint_text: Optional[Dict[str, str]] = None
    datapoint_hash: str = Field(..., min_length=10, json_schema_extra={"strip_whitespace": True})

    @field_validator("datapoint_uri")
    def validate_datapoint_uri(cls, value):
        if value and len(str(value)) < 10:
            raise ValueError("datapoint_uri need to be at least 10 char length.")
        return value

    @model_validator(mode='before')
    def validate_datapoint_text(cls, values: Dict[str, Any]):
        """
        Validate datapoint_uri.

        Raise error if no datapoint_text and no value for URI.
        """
        if not values.get("datapoint_uri") and not values.get("datapoint_text"):
            raise ValueError("datapoint_uri is missing.")
        return values


class RequestConfig(Model):
    """definition of the request_config object in manifest"""

    version: int = 0
    shape_type: Optional[ShapeTypes] = None
    min_points: Optional[int] = None
    max_points: Optional[int] = None
    min_shapes_per_image: Optional[int] = None
    max_shapes_per_image: Optional[int] = None
    restrict_to_coords: Optional[bool] = None
    minimum_selection_area_per_shape: Optional[int] =None
    multiple_choice_max_choices: Optional[int] = 1
    multiple_choice_min_choices: Optional[int] = 1
    overlap_threshold: Optional[float] = None
    answer_type: Optional[str] = "str"
    max_value: Optional[float] = None
    min_value: Optional[float] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    sig_figs: Optional[int] = None
    keep_answers_order: Optional[bool] = None
    ignore_case: Optional[bool] = False
    enable_hold_time: Optional[bool] = False


class InternalConfig(Model):
    """discarded from incoming manifests"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    exchange: Optional[Dict[str, Union[str, int, float]]] = None
    reco: Optional[Dict[str, Union[str, int, float]]] = None
    repo: Optional[Dict[str, Union[str, int, float]]] = None
    other: Optional[Dict[str, Union[str, int, float]]] = None
    # Accept one layer of nested
    mitl: Optional[Dict[str, Union[str, int, float, Dict[str, Union[str, int, float]]]]] = None


class NestedManifest(Model):
    """The nested manifest description for multi_challenge jobs"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # We will set a default dynamic value for job_id
    job_id: Optional[UUID] = None
    validate_job_id = field_validator("job_id")(validate_uuid)

    request_type: BaseJobTypesEnum
    requester_restricted_answer_set: Optional[Dict[str, Dict[str, str]]] = None

    @field_validator("request_type")
    def validate_request_type(cls, value, validation_info: ValidationInfo):
        request_validator = RequestTypeValidator(multi_challenge=False)
        return request_validator.validate(value, validation_info)

    @field_validator("requester_restricted_answer_set")
    def validate_requester_restricted_answer_set(cls, value, validation_info: ValidationInfo, **kwargs):
        """image_label_area_select should always have a single RAS set"""

        # validation runs before other params, so need to handle missing case
        values = validation_info.data
        if "request_type" not in values:
            raise ValueError("request_type missing")
        if values["request_type"] == BaseJobTypesEnum.image_label_area_select:
            if not value or len(value.keys()) == 0:
                value = {"label": {}}
                values["requester_restricted_answer_set"] = value
        if values["request_type"] == BaseJobTypesEnum.image_label_multiple_choice:
            if not value or len(value.keys()) <= 1:
                raise ValueError(
                    "image_label_multiple_choice needs at least 2+ options in requester_restricted_answer_set"
                )
            elif len(value.keys()) > 4:
                raise ValueError(
                    "image_label_multiple_choice can not handle more than 4 options requester_restricted_answer_set"
                )
        return value

    requester_description: Optional[str] = None
    requester_max_repeats: int = 100
    requester_min_repeats: int = 1
    requester_question: Optional[Dict[str, str]] = None
    requester_question_example: Optional[Union[HttpUrl, List[HttpUrl]]] = None

    @field_validator("requester_question_example")
    def validate_requester_question_example(cls, value, validation_info: ValidationInfo, **kwargs):
        # validation runs before other params, so need to handle missing case
        values = validation_info.data
        if not ("request_type" in values):
            raise ValueError("request_type missing")

        # based on https://github.com/hCaptcha/hmt-basemodels/issues/27#issuecomment-590706643
        supports_lists = [BaseJobTypesEnum.image_label_area_select, BaseJobTypesEnum.image_label_binary]

        if isinstance(value, list) and not values["request_type"] in supports_lists:
            raise ValueError("Lists are not allowed in this challenge type")
        return value

    unsafe_content: bool = False
    requester_accuracy_target: float = 0.1

    request_config: Optional[RequestConfig] = None

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri: Optional[HttpUrl] = None
    groundtruth: Optional[str] = None

    @field_validator("groundtruth")
    def validate_groundtruth(cls, v, validation_info: ValidationInfo, **kwargs):
        values = validation_info.data
        if "groundtruth_uri" in values and "groundtruth" in values:
            raise ValueError("Specify only groundtruth_uri or groundtruth, not both.")
        return v

    # Configuration id -- XXX LEGACY
    confcalc_configuration_id: Optional[str] = None
    webhook: Optional[Webhook] = None


class Manifest(Model):
    """The manifest description."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_mode: Literal["batch", "online", "instant_delivery"]

    # We will set a default dynamic value for job_api_key
    job_api_key: Optional[UUID] = None

    # We will set a default dynamic value for job_id
    job_id: UUID = Field(default_factory=uuid4)

    job_total_tasks: int
    multi_challenge_manifests: Optional[List[NestedManifest]] = None
    request_type: BaseJobTypesEnum
    network: Optional[str] = None
    only_sign_results: bool = False
    public_results: bool = False

    requester_restricted_answer_set: Optional[Dict[str, Dict[str, str]]] = None

    requester_description: Optional[str] = None
    requester_max_repeats: int = 100
    requester_min_repeats: int = 1
    requester_question: Dict[str, str]

    requester_question_example: Optional[Union[HttpUrl, List[HttpUrl]]] = None
    requester_example_extra_fields: Optional[Union[Dict[str, str], List[Union[Dict[str, str]]]]] = None

    unsafe_content: bool = False
    task_bid_price: float
    oracle_stake: float
    expiration_date: Optional[int] = None
    start_date: Optional[int] = None
    requester_accuracy_target: float = 0.1
    manifest_smart_bounty_addr: Optional[str] = None
    hmtoken_addr: Optional[str] = None
    minimum_trust_server: float = 0.1
    minimum_trust_client: float = 0.1
    recording_oracle_addr: Optional[str] = None
    reputation_oracle_addr: Optional[str] = None
    reputation_agent_addr: Optional[str] = None
    requester_pgp_public_key: Optional[str] = None
    ro_uri: Optional[str] = None
    repo_uri: Optional[str] = None
    batch_result_delivery_webhook: Optional[AnyHttpUrl] = None
    online_result_delivery_webhook: Optional[AnyHttpUrl] = None
    instant_result_delivery_webhook: Optional[AnyHttpUrl] = None

    request_config: Optional[RequestConfig] = None

    # If taskdata is directly provided
    taskdata: Optional[List[TaskData]] = None

    # If taskdata is separately stored
    taskdata_uri: Optional[AnyHttpUrl] = None

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri: Optional[AnyHttpUrl] = None
    groundtruth: Optional[str] = None

    # internal config options for param tests etc.
    internal_config: Optional[InternalConfig] = None

    # Configuration id
    confcalc_configuration_id: Optional[str] = None
    restricted_audience: Optional[RestrictedAudience] = {}

    webhook: Optional[Webhook] = None

    rejected_uri: Optional[AnyHttpUrl] = None
    rejected_count: Optional[int] = None

    is_verification: bool = False

    # #### Validators

    @model_validator(mode="before")
    def validate(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        start_date = values.get("start_date")
        expiration_date = values.get("expiration_date")
        # validate at least taskdata or taskdata_uri is present
        taskdata = values.get("taskdata")
        taskdata_uri = values.get("taskdata_uri")
        if taskdata is not None and len(taskdata) > 0 and taskdata_uri is not None:
            raise ValueError("Specify only one of taskdata {} or taskdata_uri {}".format(taskdata, taskdata_uri))
        if taskdata is None and taskdata_uri is None:
            raise ValueError("No taskdata or taskdata_uri found in manifest")

        if not start_date and not expiration_date:
            # Timestamps are not passed
            return values
        has_both_dates = bool(start_date) and bool(expiration_date)
        if not has_both_dates:
            raise ValueError("You must specify both start_date and expiration_date")

        if not start_date < expiration_date:
            raise ValueError("start_date must be before expiration_date")

        duration = datetime.utcfromtimestamp(expiration_date) - datetime.utcfromtimestamp(start_date)
        if 7 < duration.days:
            raise ValueError("Max job duration is 7 days.")

        return values

    @field_validator("requester_min_repeats")
    def validate_min_repeats(cls, v, validation_info: ValidationInfo):
        """min repeats are required to be at least 4 if ilmc"""
        values = validation_info.data
        if values["request_type"] == "image_label_multiple_choice":
            return max(v, 4)
        return v

    @field_validator("groundtruth")
    def validate_groundtruth(cls, value, validation_info: ValidationInfo):
        values = validation_info.data
        if "groundtruth_uri" in values and "groundtruth" in values:
            raise ValueError("Specify only groundtruth_uri or groundtruth, not both.")
        return value

    @field_validator("requester_restricted_answer_set")
    def validate_requester_restricted_answer_set(cls, value, validation_info: ValidationInfo, **kwargs):
        """image_label_area_select should always have a single RAS set"""
        # validation runs before other params, so need to handle missing case
        values = validation_info.data
        if not ("request_type" in values):
            raise ValueError("request_type missing")

        if values["request_type"] == BaseJobTypesEnum.image_label_area_select:
            if not value or len(value.keys()) == 0:
                value = {"label": {}}
                values["requester_restricted_answer_set"] = value

        if values["request_type"] == BaseJobTypesEnum.image_label_multiple_choice:
            if not value or len(value.keys()) <= 1:
                raise ValueError(
                    "image_label_multiple_choice needs at least 2+ options in requester_restricted_answer_set"
                )
            elif len(value.keys()) > 4:
                raise ValueError(
                    "image_label_multiple_choice can not handle more than 4 options requester_restricted_answer_set"
                )
        return value

    @field_validator("requester_question_example")
    def validate_requester_question_example(cls, value, validation_info: ValidationInfo, **kwargs):
        # validation runs before other params, so need to handle missing case
        values = validation_info.data
        if not ("request_type" in values):
            raise ValueError("request_type missing")

        # based on https://github.com/hCaptcha/hmt-basemodels/issues/27#issuecomment-590706643
        supports_lists = [
            BaseJobTypesEnum.image_label_area_select,
            BaseJobTypesEnum.image_label_binary,
        ]

        if isinstance(value, list) and not (values["request_type"] in supports_lists):
            raise ValueError("Lists are not allowed in this challenge type")
        return value

    @field_validator("request_type")
    def validate_request_type(cls, value, validation_info: ValidationInfo):
        request_validator = RequestTypeValidator()
        return request_validator.validate(value, validation_info)

    validate_job_api_key = field_validator("job_api_key")(validate_uuid)
    validate_job_id = field_validator("job_id")(validate_uuid)

    def to_primitive(self):
        """Override primitive function to make it serializable."""
        d = json.loads(self.model_dump_json())
        if isinstance(self.restricted_audience, RestrictedAudience):
            d["restricted_audience"] = self.restricted_audience.to_primitive()
        return d


def validate_groundtruth_uri(manifest: dict):
    """
    Validate groundtruth_uri
    Returns entries count if succeeded
    """
    request_type = manifest.get("request_type", "")
    validate_image_content_type = request_type in JOB_TYPES_FOR_CONTENT_TYPE_VALIDATION
    uri_key = "groundtruth_uri"
    uri = manifest.get(uri_key)
    if uri is None:
        return
    entries_count = 0
    try:
        response = requests.get(uri, timeout=(3.5, 5))
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            for k, v in data.items():
                entries_count += 1
                validate_groundtruth_entry(k, v, request_type, validate_image_content_type)
                validate_image_content_type = False
        else:
            for v in data:
                entries_count += 1
                validate_groundtruth_entry("", v, request_type, validate_image_content_type)
                validate_image_content_type = False

    except ValidationError as e:
        raise_validation_error(
            location=("groundtruth_uri",),
            error_message=f"Validation failed for {uri}: {e.title}",
            input_data={"groundtruth_uri": uri}
        )
    except RequestException as e:
        raise_validation_error(
            location=("groundtruth_uri",),
            error_message=f"Validation failed for {uri}: {e}",
            input_data={"groundtruth_uri": uri}
        )

    if entries_count == 0:
        raise_validation_error(
            location=("groundtruth_uri",),
            error_message=f"fetched {uri} is empty"f"fetched {uri} is empty",
            input_data={"groundtruth_uri": uri}
        )


def validate_taskdata_uri(manifest: dict):
    """
    Validate taskdata_uri
    Returns entries count if succeeded
    """
    request_type = manifest.get("request_type", "")
    validate_image_content_type = request_type in JOB_TYPES_FOR_CONTENT_TYPE_VALIDATION
    uri_key = "taskdata_uri"
    uri = manifest.get(uri_key)
    if uri is None:
        return
    entries_count = 0
    try:
        response = requests.get(uri, timeout=(3.5, 5))
        response.raise_for_status()
        data = response.json()
        for v in data:
            entries_count += 1
            validate_taskdata_entry(v, validate_image_content_type)
            validate_image_content_type = False  # We want to validate only first entry for content type

    except ValidationError as e:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"Validation failed for {uri}: {e.title}",
            input_data={"taskdata_uri": uri}
        )
    except RequestException as e:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"Validation failed for {uri}: {e}",
            input_data={"taskdata_uri": uri}
        )

    if entries_count == 0:
        raise_validation_error(
            location=("taskdata_uri",),
            error_message=f"fetched {uri} is empty"f"fetched {uri} is empty",
            input_data={"taskdata_uri": uri}
        )


def validate_manifest_example_images(manifest: dict):
    """Fetch and validate the example resources."""
    question_example = manifest.get("requester_question_example")
    req_res_answer_set = manifest.get("requester_restricted_answer_set", {})
    if question_example:
        # some jobs might not have requester_question_example
        validate_requester_example_image(question_example)
    if req_res_answer_set:
        validate_requester_restricted_answer_set_uris(req_res_answer_set)


def fetch_data_from_uri(data_uri: str):
    """Fetch data from a given uri."""
    try:
        response = requests.get(data_uri, timeout=(3.5, 5))
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise_validation_error(
            location=("taskdata_uri", "groundtruth_uri",),
            error_message=f"Failed to fetch data from {data_uri}: {e}"
        )


def validate_manifest_uris(manifest: dict):
    """Fetch & validate manifest's remote objects"""
    validate_taskdata_uri(manifest)
    validate_groundtruth_uri(manifest)


def validate_is_verification(manifest: dict):
    """Check for verification jobs."""

    request_type = manifest.get("request_type")
    if request_type == BaseJobTypesEnum.image_drag_drop:
        task_key = "task_key"
    else:
        task_key = "datapoint_uri"

    taskdata_uri = manifest.get("taskdata_uri")
    gt_uri = manifest.get("groundtruth_uri")

    if not gt_uri or not taskdata_uri:
        raise_validation_error(
            location=("taskdata_uri", "groundtruth_uri",),
            error_message="Manifest is missing either of groundtruth or taskdata"
        )

    taskdata = fetch_data_from_uri(taskdata_uri)
    groundtruth = fetch_data_from_uri(gt_uri)

    task_keys = {task.get(task_key) for task in taskdata}
    gt_keys = set(groundtruth.keys())

    if gt_keys != task_keys:
        raise_validation_error(
            location=("taskdata_uri", "groundtruth_uri",),
            error_message="All taskdata entries dont have corresponding groundtruth entry",
            input_data={"taskdata_uri": taskdata_uri, "groundtruth_uri": gt_uri}
        )
