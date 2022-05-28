from uuid import UUID

from schematics.models import Model, ValidationError
from schematics.types import BaseType, ListType, StringType, DictType, IntType, FloatType


class ScoreType(BaseType):
    def validate_score(self, value):
        if value is None:
            return value

        if not isinstance(value, dict):
            raise ValidationError("value must be a dict")

        if len(value) != 1:
            raise ValidationError("invalid number of keys")

        score = value.get("score")
        if score is None:
            raise ValidationError("score missing")

        if not isinstance(score, (float, int)):
            raise ValidationError("invalid score value type")
        
        if score > 1 or score < 0:
            raise ValidationError("invalid score value")


class RestrictedAudience(Model):
    lang = ListType(DictType(ScoreType), required=False)
    country = ListType(DictType(ScoreType), required=False)
    browser = ListType(DictType(ScoreType), required=False)
    sitekey = ListType(DictType(ScoreType), required=False)
    serverdomain = ListType(DictType(ScoreType), required=False)
    confidence = ListType(DictType(ScoreType), required=False)
    reason = ListType(DictType(ScoreType), required=False)

    min_difficulty = IntType(required=False, min_value=0, max_value=4)
    min_user_score = FloatType(required=False, min_value=0, max_value=1)
    max_user_score = FloatType(required=False, min_value=0, max_value=1)

    launch_group_id = IntType(required=False, min_value=0)

    class Options:
        serialize_when_none=False

    def keys_iterator(self, value):
        if isinstance(value, list):
            for restriction in value:
                if len(restriction) != 1:
                    raise ValidationError("exactly 1 element is required")
                yield next(iter(restriction))

    def keys_single_check(self, value):
        for key in self.keys_iterator(value):
            continue

    def keys_lowercase_check(self, value):
        for key in self.keys_iterator(value):
            if key != key.lower():
                raise ValidationError("use lowercase")

    def keys_uuid_check(self, value):
        for key in self.keys_iterator(value):
            if key != key.lower():
                raise ValidationError("use lowercase")
            try:
                UUID(key)
            except:
                raise ValidationError("invalid uuid")

    def keys_choices_check(self, value, choices):
        for key in self.keys_iterator(value):
            if key not in choices:
                raise ValidationError(f"{key} not allowed. Use {choices}")

    def validate_lang(self, data, value):
        self.keys_lowercase_check(value)
        return value

    def validate_country(self, data, value):
        self.keys_lowercase_check(value)
        return value

    def validate_browser(self, data, value):
        self.keys_choices_check(value, choices=["tablet", "mobile", "desktop", "modern_browser"])
        return value

    def validate_sitekey(self, data, value):
        self.keys_uuid_check(value)
        return value

    def validate_serverdomain(self, data, value):
        self.keys_single_check(value)
        return value

    def validate_confidence(self, data, value):
        self.keys_choices_check(value, choices=["minimum_client_confidence"])
        return value