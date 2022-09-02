import logging

import requests
from pydantic import BaseModel
from pydantic.errors import UrlError

logger = logging.getLogger(__name__)


class ImageValidationError(Exception):
    """ Raises when image is not valid.  """
    pass


def check_valid_image(name: str, uri: str) -> None:
    """
    Checks whether a content from URI is a valid image.

    Parameters:
        name(str): name referenced for URI value
        uri(str): URI where content must be fetched
    Raises:
        URIRequestError: invalid image
    """
    try:
        image_formats = {"image/png", "image/jpeg", "image/jpg"}
        r = requests.head(uri)

        if r.headers.get('content-type', '') not in image_formats:
            msg = f'URI has an invalid image for "{name}": {uri}'
            logger.error(msg)
            raise ImageValidationError(msg)

    except requests.exceptions.RequestException as e:
        msg = f'Error when validating image from URI "{uri}": {e}'
        logger.error(msg)
        raise ImageValidationError(msg)
