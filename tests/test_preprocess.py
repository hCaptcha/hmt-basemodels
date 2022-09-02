import unittest

from schematics.exceptions import DataError

from basemodels.manifest.data.preprocess import Preprocess


class PipelineTest(unittest.TestCase):
    def test_preprocess(self):
        config = {}
        p = Preprocess({"pipeline": "FaceBlurPipeline", "config": config})

        self.assertEqual(p.pipeline, "FaceBlurPipeline")
        self.assertEqual(p.config, config)

        p = Preprocess({"pipeline": "FaceBlurPipeline"})

        self.assertIsNone(p.config)


    def test_preprocess_raise(self):
        with self.assertRaises(DataError):
            Preprocess().validate()

        with self.assertRaises(DataError):
            Preprocess({"pipeline": ""}).validate()

        with self.assertRaises(DataError):
            Preprocess({"pipeline": "FaceBlurPipeline", "config": 1}).validate()


    def test_preprocess_to_dict(self):
        config = { "radius": 3 }
        p = Preprocess({"pipeline": "FaceBlurPipeline", "config": config})

        self.assertEqual(p.to_dict(), { "pipeline": "FaceBlurPipeline", "config": config })

        p = Preprocess({"pipeline": "FaceBlurPipeline"})

        self.assertEqual(p.to_dict(), { "pipeline": "FaceBlurPipeline" })



