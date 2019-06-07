import uuid
from schematics.models import Model, ValidationError
from schematics.types import StringType, DecimalType, BooleanType, IntType, DictType, ListType, URLType, FloatType, \
    UUIDType, ModelType, BooleanType, UnionType


class TaskData(Model):
    """ objects within taskdata list in Manifest """
    task_key = UUIDType(required=True)
    datapoint_uri = URLType(required=True, min_length=10)
    datapoint_hash = StringType(required=True, min_length=10)


class RequestConfig(Model):
    """ definition of the request_config object in manifest """
    version = IntType(default=0)
    shape_type = StringType(
        choices=["point", "bounding_box", "polygon"], required=True)
    min_points = IntType()
    max_points = IntType()
    min_shapes_per_image = IntType()
    max_shapes_per_image = IntType()
    restrict_to_coords = BooleanType()
    minimum_selection_area_per_shape = IntType()


class NestedManifest(Model):
    """ The nested manifest description for multi_challenge jobs """
    job_id = UUIDType(default=uuid.uuid4)

    requester_restricted_answer_set = DictType(DictType(StringType))

    def validate_requester_restricted_answer_set(self, data, value):
        """image_label_area_select should always have a single RAS set"""
        if data['request_type'] == 'image_label_area_select':
            if not value or len(value.keys()) == 0:
                value = {'label': {}}
                data['requester_restricted_answer_set'] = value
        return value

    requester_description = StringType()
    requester_max_repeats = IntType(default=100)
    requester_min_repeats = IntType(default=1)
    requester_question = DictType(StringType)

    requester_question_example = UnionType((URLType, ListType), field=URLType)

    def validate_requester_question_example(self, data, value):
        if data['request_type'] != 'image_label_binary' and isinstance(
                value, list):
            raise ValidationError(
                "Lists are not allowed in this challenge type")
        return value

    unsafe_content = BooleanType(default=False)
    requester_accuracy_target = FloatType(default=.1)
    request_type = StringType(
        required=True,
        choices=[
            "image_label_binary",
            "image_label_multiple_choice_one_option",
            "image_label_multiple_choice_multiple_options",
            "text_free_entry",
            "text_multiple_choice_one_option",
            "text_multiple_choice_multiple_options",
            "image_label_area_adjust",
            "image_label_area_select",
            "image_label_area_select_one_option",  # legacy
            "image_label_area_select_multiple_options",  # legacy
            "image_label_single_polygon",
            "image_label_multiple_polygons",
            "image_label_semantic_segmentation_one_option",
            "image_label_semantic_segmentation_multiple_options",
        ])

    request_config = ModelType(RequestConfig, required=False)

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri = URLType(required=False)
    groundtruth = StringType(required=False)

    def validate_groundtruth(self, data, value):
        if data.get('groundtruth_uri') and data.get('groundtruth'):
            raise ValidationError(
                "Specify only groundtruth_uri or groundtruth, not both.")
        return value

    # Configuration id
    confcalc_configuration_id = StringType(required=False)



class Manifest(Model):
    """ The manifest description. """
    job_mode = StringType(
        required=True, choices=["batch", "online", "instant_delivery"])
    job_api_key = UUIDType(default=uuid.uuid4)
    job_id = UUIDType(default=uuid.uuid4)
    job_total_tasks = IntType()

    requester_restricted_answer_set = DictType(DictType(StringType))

    def validate_requester_restricted_answer_set(self, data, value):
        """image_label_area_select should always have a single RAS set"""
        if data['request_type'] == 'image_label_area_select':
            if not value or len(value.keys()) == 0:
                value = {'label': {}}
                data['requester_restricted_answer_set'] = value
        return value

    requester_description = StringType()
    requester_max_repeats = IntType(default=100)
    requester_min_repeats = IntType(default=1)
    requester_question = DictType(StringType)

    requester_question_example = UnionType((URLType, ListType), field=URLType)

    def validate_requester_question_example(self, data, value):
        if data['request_type'] != 'image_label_binary' and isinstance(
                value, list):
            raise ValidationError(
                "Lists are not allowed in this challenge type")
        return value

    unsafe_content = BooleanType(default=False)
    task_bid_price = DecimalType(required=True)
    oracle_stake = DecimalType(required=True)
    expiration_date = IntType()
    requester_accuracy_target = FloatType(default=.1)
    manifest_smart_bounty_addr = StringType()
    minimum_trust_server = FloatType(default=.1)
    minimum_trust_client = FloatType(default=.1)
    recording_oracle_addr = StringType(required=True)
    reputation_oracle_addr = StringType(required=True)
    reputation_agent_addr = StringType(required=True)
    requester_pgp_public_key = StringType()
    ro_uri = StringType()
    repo_uri = StringType()

    batch_result_delivery_webhook = URLType()
    online_result_delivery_webhook = URLType()
    instant_result_delivery_webhook = URLType()

    multi_challenge_manifests = ListType(ModelType(NestedManifest), required=False)

    request_type = StringType(
        required=True,
        choices=[
            "image_label_binary",
            "image_label_multiple_choice_one_option",
            "image_label_multiple_choice_multiple_options",
            "text_free_entry",
            "text_multiple_choice_one_option",
            "text_multiple_choice_multiple_options",
            "image_label_area_adjust",
            "image_label_area_select",
            "image_label_area_select_one_option",  # legacy
            "image_label_area_select_multiple_options",  # legacy
            "image_label_single_polygon",
            "image_label_multiple_polygons",
            "image_label_semantic_segmentation_one_option",
            "image_label_semantic_segmentation_multiple_options",
            "multi_challenge",
        ])


    def validate_request_type(self, data, value):
        """multi_challenge should always have multi_challenge_manifests"""
        if data['request_type'] == 'multi_challenge':
            if not data.get('multi_challenge_manifests'):
                raise ValidationError(
                    "multi_challenge requires multi_challenge_manifests.")
        return value

    request_config = ModelType(RequestConfig, required=False)

    # If taskdata is directly provided
    taskdata = ListType(ModelType(TaskData))

    # If taskdata is separately stored
    taskdata_uri = URLType()

    # Groundtruth data is stored as a URL or optionally as an inlined json-serialized stringtype
    groundtruth_uri = URLType(required=False)
    groundtruth = StringType(required=False)

    def validate_groundtruth(self, data, value):
        if data.get('groundtruth_uri') and data.get('groundtruth'):
            raise ValidationError(
                "Specify only groundtruth_uri or groundtruth, not both.")
        return value

    # Configuration id
    confcalc_configuration_id = StringType(required=False)

    restricted_audience = DictType(ListType(DictType(DictType(FloatType))))

    def validate_taskdata_uri(self, data, value):
        if data.get('taskdata') and len(
                data.get('taskdata')) > 0 and data.get('taskdata_uri'):
            raise ValidationError(
                u'Specify only one of taskdata {} or taskdata_uri {}'.format(
                    data.get('taskdata'), data.get('taskdata_uri')))
        return value

    validate_taskdata = validate_taskdata_uri
