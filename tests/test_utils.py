import unittest

from basemodels.utils import check_valid_image, ImageValidationError



class TestBaseModelUtils(unittest.TestCase):
    """Tests for basemodel utility functions"""

    def test_error_when_checking_valid_image(self):
        """ Tests URI when there is no response. """
        invalid_uri = 'https://some-domain.com/123/cat.png'

        with self.assertRaises(ImageValidationError):
            check_valid_image('key', invalid_uri)

    def test_non_image_when_checking_valid_image(self):
        """ Tests URI when it returns 2xx response but not an image. """
        wrong_uri = 'https://storagecapturedev.blob.core.windows.net/captcha-poc/validation_poc/jsons/ground_truth4.json'
        with self.assertRaises(ImageValidationError) as e:
            check_valid_image('key', wrong_uri)

    def test_check_valid_image(self):
        """ Tests when URI returns a valid image. """
        uri = 'https://s3-us-west-2.amazonaws.com/temple-gates.hcaptcha.com/great-success.0.png'
        check_valid_image('borat', uri)
