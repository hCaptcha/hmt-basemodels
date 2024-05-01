import enum
import typing
from pydantic import BaseModel


class Pipeline(str, enum.Enum):
    FaceBlurPipeline = "FaceBlurPipeline"
    OCRThinFilterPipeline = "OCRThinFilterPipeline"
    UploadPipeline = "UploadPipeline"


class Preprocess(BaseModel):
    pipeline: Pipeline
    config: typing.Optional[dict] = None

    def to_dict(self):
        p = {"pipeline": self.pipeline.value}
        if self.config is not None:
            p["config"] = self.config
        return p
