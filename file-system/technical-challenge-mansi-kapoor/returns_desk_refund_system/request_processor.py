"""Stateless batch entry point matching the tuple contract from readme.md
and the edge cases captured in requirements.txt (section 7).

Input:
    list of (request_id, order_id, buyer_email, shipping_address_id,
             payment_fingerprint, order_total, reason)

Output:
    list where each entry is either:
      - (request_id, refund_amount, decision) on success, or
      - the literal string "ERROR" if the request is missing a required
        field (request_id, buyer_email, shipping_address_id,
        payment_fingerprint, or order_total)

Stage 1 policy: DAMAGED -> auto-refund the full order_total; otherwise ->
manual review with no immediate refund.

Stage 2 policy (readme.md): buyer emails that differ only by casing,
surrounding whitespace, or dots in the local part are treated as the same
buyer. Each buyer may receive at most `daily_auto_refund_cap` (default
$200.00) in auto-refunds across a single `process_return_requests` call
(one call == one day's worth of requests, per readme.md). Once a buyer's
cap is reached, requests that would otherwise auto-refund are given as much
refund as remains under the cap and routed to MANUAL_REVIEW instead;
further requests past the cap get refund_amount = 0.00.

The per-request base decision (Stage 1) and the cross-request cap
adjustment (Stage 2) are kept as separate steps so future stages can add or
swap either independently. Kept separate from ReturnDeskService, which
models a stateful per-order return workflow against pre-registered Order
data; this function instead works directly off the order_total carried in
each raw tuple.
"""

from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Tuple, Union

from .decisions import REFUND_DECISIONS
from .exceptions import MissingRequiredFieldError
from .reasons import RETURN_REASONS

ReturnRequestTuple = Tuple[Any, Any, Any, Any, Any, Any, Any]
ReturnResultTuple = Tuple[Any, Decimal, str]

# Fields that must be present (non-None, non-blank) for a request to be
# processed. Note: order_id and reason are intentionally excluded — a
# missing reason is a valid case (see requirements.txt, section 7).
REQUIRED_FIELDS = (
    "request_id",
    "buyer_email",
    "shipping_address_id",
    "payment_fingerprint",
    "order_total",
)

_FIELD_NAMES = (
    "request_id",
    "order_id",
    "buyer_email",
    "shipping_address_id",
    "payment_fingerprint",
    "order_total",
    "reason",
)

ERROR_RESULT = "ERROR"

# Stage 2: max auto-refund dollars a single (normalized) buyer email may
# receive within one process_return_requests call ("day").
DEFAULT_DAILY_AUTO_REFUND_CAP = Decimal("200.00")


def process_return_requests(
    requests: List[ReturnRequestTuple],
    daily_auto_refund_cap: Decimal = DEFAULT_DAILY_AUTO_REFUND_CAP,
) -> List[Union[ReturnResultTuple, str]]:
    """Evaluate a batch of raw return request tuples.

    Requests are processed in order; a running per-buyer auto-refund total
    is tracked across the batch (Stage 2's daily cap), so request order
    matters for which requests get capped. A request missing a required
    field is represented by the literal string "ERROR" at that position
    instead of a result tuple, and does not affect any buyer's running
    total.
    """
    results: List[Union[ReturnResultTuple, str]] = []
    auto_refunded_today: Dict[str, Decimal] = {}

    for raw_request in requests:
        try:
            fields = _parse(raw_request)
        except MissingRequiredFieldError:
            results.append(ERROR_RESULT)
            continue

        refund_amount, decision = _base_decision(fields)
        if decision == REFUND_DECISIONS["AUTO_REFUND"]:
            refund_amount, decision = _apply_daily_cap(
                buyer_email=fields["buyer_email"],
                refund_amount=refund_amount,
                auto_refunded_today=auto_refunded_today,
                daily_cap=daily_auto_refund_cap,
            )

        results.append((fields["request_id"], refund_amount, decision))

    return results


def _parse(raw_request: ReturnRequestTuple) -> Dict[str, Any]:
    values = dict(zip(_FIELD_NAMES, raw_request))

    for field_name in REQUIRED_FIELDS:
        if _is_blank(values.get(field_name)):
            raise MissingRequiredFieldError(f"'{field_name}' is required but missing.")

    return {
        "request_id": values["request_id"],
        "order_id": values.get("order_id"),
        "buyer_email": normalize_email(values["buyer_email"]),
        "shipping_address_id": values["shipping_address_id"],
        "payment_fingerprint": values["payment_fingerprint"],
        "order_total": _parse_decimal_or_raise(values["order_total"]),
        "reason": None if _is_blank(values.get("reason")) else values["reason"],
    }


def _base_decision(fields: Dict[str, Any]) -> Tuple[Decimal, str]:
    """Stage 1 policy, before any cross-request adjustments are applied."""
    if fields["reason"] == RETURN_REASONS["DAMAGED"]:
        return fields["order_total"], REFUND_DECISIONS["AUTO_REFUND"]
    return Decimal("0.00"), REFUND_DECISIONS["MANUAL_REVIEW"]


def _apply_daily_cap(
    buyer_email: str,
    refund_amount: Decimal,
    auto_refunded_today: Dict[str, Decimal],
    daily_cap: Decimal,
) -> Tuple[Decimal, str]:
    """Cap a would-be auto-refund against the buyer's remaining daily total.

    Mutates `auto_refunded_today` to record what was actually auto-refunded.
    """
    already_refunded = auto_refunded_today.get(buyer_email, Decimal("0.00"))
    remaining = daily_cap - already_refunded

    if remaining <= Decimal("0.00"):
        return Decimal("0.00"), REFUND_DECISIONS["MANUAL_REVIEW"]

    if refund_amount <= remaining:
        auto_refunded_today[buyer_email] = already_refunded + refund_amount
        return refund_amount, REFUND_DECISIONS["AUTO_REFUND"]

    auto_refunded_today[buyer_email] = daily_cap
    return remaining, REFUND_DECISIONS["MANUAL_REVIEW"]


def normalize_email(raw_email: Any) -> str:
    """Normalize an email for buyer-identity comparisons (Stage 2).

    Trims whitespace, lowercases, and strips dots from the local part
    (before the "@") so e.g. "Alice.B@Example.com " and "aliceb@example.com"
    are treated as the same buyer. The domain is left as-is aside from
    trimming/lowercasing.
    """
    email = str(raw_email).strip().lower()
    local, separator, domain = email.partition("@")
    local = local.replace(".", "")
    return f"{local}{separator}{domain}"


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def _parse_decimal_or_raise(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation:
        raise MissingRequiredFieldError("'order_total' could not be parsed as a decimal.")
