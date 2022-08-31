import logging
import requests
from schematics.exceptions import ValidationError

logger = logging.getLogger(__name__)

class URIRequestError(ValidationError):
    """ Raises when URL is invalid.  """
    pass


def check_valid_image(name: str, uri: str) -> None:
    """
    Checks whether a content from URI is a valid image.

    Parameters:
        name(str): name referenced for URI value
        uri(str): URI where content must be fetched
    Raises:
        ValidationError: invalid image
    """
    try:
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(uri)

        if 'content-type' in r.headers and r.headers["content-type"] not in image_formats:
            msg = f'URI has an invalid image for "{name}": {uri}'
            logger.error(msg)
            raise ValidationError(msg)

    except requests.exceptions.RequestException as e:
        msg = f'Error when validating image from URI "{uri}": {e}'
        logger.error(msg)
        raise URIRequestError(msg)
