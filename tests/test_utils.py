import unittest

from pydantic.errors import UrlError
from schematics.exceptions import ValidationError

from basemodels.pydantic import TaskData
from basemodels.manifest.data.taskdata import TaskDataEntry
from basemodels.manifest.utils import (
    check_valid_image as schematicsImageChecker,
    URIRequestError as SchematicsRequestError
)

from basemodels.pydantic.utils import (
    check_valid_image as pydanticImageChecker,
    URIRequestError as PydanticRequestError
)


class TestSchemaitcsUtils(unittest.TestCase):
    """Tests for Schematics utils functions """

    def test_error_when_checking_valid_image(self):
        """ Tests URI when there is no response. """
        invalid_uri = 'https://some-domain.com/123/cat.png'

        with self.assertRaises(SchematicsRequestError):
            schematicsImageChecker('key', invalid_uri)

    def test_non_image_when_checking_valid_image(self):
        """ Tests URI when it returns 2xx response but not an image. """
        wrong_uri = 'https://storagecapturedev.blob.core.windows.net/captcha-poc/validation_poc/jsons/ground_truth4.json'
        with self.assertRaises(ValidationError) as e:
            schematicsImageChecker('key', wrong_uri)

    def test_check_valid_image(self):
        """ Tests when URI returns a valid image. """
        uri = 'https://s3-us-west-2.amazonaws.com/temple-gates.hcaptcha.com/great-success.0.png'
        schematicsImageChecker('borat', uri)


class TestPydanticUtils(unittest.TestCase):
    """Tests for Pydantic utils functions """

    def test_error_when_checking_valid_image(self):
        """ Tests URI when there is no response. """
        invalid_uri = 'https://some-domain.com/123/cat.png'

        with self.assertRaises(PydanticRequestError):
            pydanticImageChecker('key', invalid_uri)

    def test_non_image_when_checking_valid_image(self):
        """ Tests URI when it returns 2xx response but not an image. """
        wrong_uri = 'https://storagecapturedev.blob.core.windows.net/captcha-poc/validation_poc/jsons/ground_truth4.json'
        with self.assertRaises(UrlError):
            pydanticImageChecker('key', wrong_uri)

    def test_check_valid_image(self):
        """ Tests when URI returns a valid image. """
        uri = 'https://s3-us-west-2.amazonaws.com/temple-gates.hcaptcha.com/great-success.0.png'
        pydanticImageChecker('borat', uri)
