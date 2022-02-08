from schematics.models import Model
from schematics.types import StringType, DictType, UnionType, IntType, FloatType

class Preprocess(Model):
    pipeline = StringType(required=True,choices=["FaceBlurPipeline", "OCRThinFilterPipeline", "UploadPipeline"])
    config = DictType(UnionType([FloatType, IntType, StringType]))

    def to_dict(self):
        p = { "pipeline": self.pipeline }
        if self.config is not None:
            p["config"] = self.config
        return p