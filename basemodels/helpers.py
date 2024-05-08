from typing import Tuple, Optional, Any

from pydantic_core import InitErrorDetails, ValidationError


def raise_validation_error(location: Tuple[str, ...], error_message: str, input_data: Optional[Any] = None):
    """Helper function to raise validation error."""
    error_details = InitErrorDetails(
        loc=location,
        ctx={"error": error_message},
        type="value_error",
        input=input_data
    )
    raise ValidationError.from_exception_data(error_message, [error_details])
