from enum import Enum
from uuid import UUID
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    conint,
    confloat,
    field_validator,
    model_validator,
)


class RestrictedAudienceBrowserEnum(str, Enum):
    mobile = "mobile"
    tablet = "tablet"
    desktop = "desktop"
    modern_browser = "modern_browser"


class RestrictedAudienceConfidenceEnum(str, Enum):
    minimum_client_confidence = "minimum_client_confidence"


class RestrictedAudienceScore(BaseModel):
    score: confloat(ge=0, le=1)


class RestrictedAudience(BaseModel):
    lang: Optional[List[Dict[str, RestrictedAudienceScore]]] = None
    country: Optional[List[Dict[str, RestrictedAudienceScore]]] = None
    sitekey: Optional[List[Dict[str, RestrictedAudienceScore]]] = None
    serverdomain: Optional[List[Dict[str, RestrictedAudienceScore]]] = None
    browser: Optional[List[Dict[RestrictedAudienceBrowserEnum, RestrictedAudienceScore]]] = None
    confidence: Optional[List[Dict[RestrictedAudienceConfidenceEnum, RestrictedAudienceScore]]] = None
    reason: Optional[List[Dict[str, RestrictedAudienceScore]]] = None
    roles: Optional[List[Dict[str, RestrictedAudienceScore]]] = None

    min_difficulty: Optional[conint(ge=0, le=4, strict=True)] = None
    min_user_score: Optional[confloat(ge=0, le=1)] = None
    max_user_score: Optional[confloat(ge=0, le=1)] = None

    launch_group_id: Optional[conint(ge=0, strict=True)] = None
    interests: Optional[List[conint(strict=True)]] = None

    def dict(self, **kwargs):
        kwargs["exclude_unset"] = True
        return super().model_dump(**kwargs)

    def json(self, **kwargs):
        kwargs["exclude_unset"] = True
        return super().model_dump_json(**kwargs)

    def to_primitive(self, **kwargs):
        kwargs["exclude_unset"] = True
        return self.model_dump(**kwargs)

    @model_validator(mode="before")
    def validate_score_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        for entry, value in values.items():
            if value is None:
                continue
            if entry in ["lang", "country", "browser", "sitekey", "serverdomain", "confidence"]:
                if isinstance(value, list):
                    for restriction in value:
                        if len(restriction) > 1:
                            raise ValueError("only 1 element per list item is allowed")
                        key = next(iter(restriction))
                        if entry in ["lang", "country", "sitekey"]:
                            if str(key) != str(key).lower():
                                raise ValueError("use lowercase")
        return values

    @field_validator("sitekey")
    def validate_sitekey(cls, value):
        if value is not None:
            for restriction in value:
                for sitekey in restriction:
                    try:
                        UUID(sitekey)
                    except:
                        raise ValueError("invalid sitekey")
        return value
