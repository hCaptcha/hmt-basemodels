from enum import Enum

JOB_TYPES_FOR_CONTENT_TYPE_VALIDATION = [
    "image_label_binary",
    "image_label_multiple_choice",
    "text_free_entry",
    "image_label_area_adjust",
    "image_label_area_select",
    "image_label_single_polygon",
    "image_label_multiple_polygons",
    "image_label_semantic_segmentation_one_option",
    "image_label_semantic_segmentation_multiple_options",
    "image_label_text",
]

SUPPORTED_CONTENT_TYPES = [
    "image/jpeg",
    "image/jpg",
    "image/png",
]


# Base job types
class BaseJobTypesEnum(str, Enum):
    image_label_binary = "image_label_binary"
    image_label_multiple_choice = "image_label_multiple_choice"
    text_free_entry = "text_free_entry"
    text_label_multiple_span_select = "text_label_multiple_span_select"
    text_multiple_choice_one_option = "text_multiple_choice_one_option"
    text_multiple_choice_multiple_options = "text_multiple_choice_multiple_options"
    image_label_area_adjust = "image_label_area_adjust"
    image_label_area_select = "image_label_area_select"
    image_label_single_polygon = "image_label_single_polygon"
    image_label_multiple_polygons = "image_label_multiple_polygons"
    image_label_semantic_segmentation_one_option = "image_label_semantic_segmentation_one_option"
    image_label_semantic_segmentation_multiple_options = "image_label_semantic_segmentation_multiple_options"
    image_label_text = "image_label_text"
    image_drag_drop = "image_drag_drop"
    multi_challenge = "multi_challenge"
