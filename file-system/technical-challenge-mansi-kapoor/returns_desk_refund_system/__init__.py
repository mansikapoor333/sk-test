"""Returns Desk Refund System.

Public API surface for the package.
"""

from .decisions import REFUND_DECISIONS
from .exceptions import (
    InvalidReturnItemsError,
    InvalidReturnReasonError,
    InvalidStatusTransitionError,
    MissingRequiredFieldError,
    OrderNotFoundError,
    ReturnDeskError,
    ReturnNotFoundError,
)
from .models import Order, OrderItem, RefundDecision, ReturnLineItem, ReturnRequest
from .reasons import RETURN_REASONS
from .refund_policy import (
    DamagedItemsAutoRefundRule,
    DefaultManualReviewRule,
    RefundDecisionEngine,
    RefundRule,
)
from .request_processor import (
    DEFAULT_DAILY_AUTO_REFUND_CAP,
    ERROR_RESULT,
    REQUIRED_FIELDS,
    normalize_email,
    process_return_requests,
)
from .service import ReturnDeskService
from .status import RETURN_STATUSES, VALID_TRANSITIONS

__all__ = [
    "ReturnDeskService",
    "Order",
    "OrderItem",
    "ReturnLineItem",
    "ReturnRequest",
    "RefundDecision",
    "RETURN_STATUSES",
    "VALID_TRANSITIONS",
    "RETURN_REASONS",
    "REFUND_DECISIONS",
    "RefundRule",
    "RefundDecisionEngine",
    "DamagedItemsAutoRefundRule",
    "DefaultManualReviewRule",
    "process_return_requests",
    "REQUIRED_FIELDS",
    "ERROR_RESULT",
    "DEFAULT_DAILY_AUTO_REFUND_CAP",
    "normalize_email",
    "ReturnDeskError",
    "OrderNotFoundError",
    "InvalidReturnItemsError",
    "InvalidReturnReasonError",
    "ReturnNotFoundError",
    "InvalidStatusTransitionError",
    "MissingRequiredFieldError",
]
