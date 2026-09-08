"""Domain-specific exceptions for the Returns Desk service."""


class ReturnDeskError(Exception):
    """Base class for all Returns Desk errors."""


class OrderNotFoundError(ReturnDeskError):
    """Raised when a return is submitted against an order that doesn't exist."""


class InvalidReturnItemsError(ReturnDeskError):
    """Raised when requested return items aren't part of the order, or exceed
    the quantity available to return."""


class InvalidReturnReasonError(ReturnDeskError):
    """Raised when a return is submitted with a reason outside of
    reasons.RETURN_REASONS."""


class ReturnNotFoundError(ReturnDeskError):
    """Raised when an operation references a return_id that doesn't exist."""


class InvalidStatusTransitionError(ReturnDeskError):
    """Raised when a return is moved to a status it cannot legally reach from
    its current status (see status.VALID_TRANSITIONS)."""


class MissingRequiredFieldError(ReturnDeskError):
    """Raised when a raw return request tuple is missing a required field
    (see request_processor.REQUIRED_FIELDS and requirements.txt, section 7)."""
