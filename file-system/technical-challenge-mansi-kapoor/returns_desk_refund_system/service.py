"""ReturnDeskService: coordinates the lifecycle of return requests against a
known set of orders.

Covers: submitting a return, and deciding whether it should be auto-refunded
or sent to manual review. Approve/receive/refund/reject/close status
transitions are expected to be added next, reusing status.VALID_TRANSITIONS
to enforce legal moves.
"""

import itertools
from typing import Any, Dict, Iterable, List, Optional, Union

from .exceptions import (
    InvalidReturnItemsError,
    InvalidReturnReasonError,
    OrderNotFoundError,
    ReturnNotFoundError,
)
from .models import Order, RefundDecision, ReturnLineItem, ReturnRequest
from .reasons import RETURN_REASONS
from .refund_policy import RefundDecisionEngine
from .status import RETURN_STATUSES

# A caller may describe an item to return as:
#   - a bare item_id string (implies quantity=1)
#   - a dict like {"item_id": ..., "quantity": ...}
#   - an already-built ReturnLineItem
ReturnItemInput = Union[str, Dict[str, Any], ReturnLineItem]


class ReturnDeskService:
    """Coordinates return requests submitted against a set of known orders."""

    def __init__(
        self,
        orders: Dict[str, Order],
        decision_engine: Optional[RefundDecisionEngine] = None,
    ):
        self._orders: Dict[str, Order] = orders
        self._returns: Dict[str, ReturnRequest] = {}
        self._id_counter = itertools.count(1)
        self._decision_engine = decision_engine or RefundDecisionEngine()

    def submit_return(
        self,
        order_id: str,
        items: Iterable[ReturnItemInput],
        reason: str,
        actor: str = "customer",
    ) -> ReturnRequest:
        """A customer (or other actor) submits a return request.

        Validates that the order exists, the reason is recognized, and every
        requested item is part of the order and available to return (i.e.
        hasn't already been fully claimed by another non-rejected return).
        On success, creates and stores a new ReturnRequest in REQUESTED
        status.
        """
        order = self._get_order_or_raise(order_id)
        self._validate_reason_or_raise(reason)
        line_items = self._validate_items_or_raise(order, items)

        return_request = ReturnRequest(
            return_id=self._generate_return_id(order_id),
            order_id=order_id,
            items=line_items,
            actor=actor,
            status=RETURN_STATUSES["REQUESTED"],
            reason=reason,
        )
        return_request.history.append({"status": return_request.status, "actor": actor})
        self._returns[return_request.return_id] = return_request
        return return_request

    def evaluate_return(self, return_id: str) -> RefundDecision:
        """Decide whether a return should be auto-refunded now or sent to
        manual review, per the refund policy (see refund_policy.py).

        The resulting RefundDecision is cached on the ReturnRequest (so
        repeated calls / later status transitions can reuse it) and
        returned to the caller.
        """
        return_request = self._get_return_or_raise(return_id)
        order = self._get_order_or_raise(return_request.order_id)

        decision = self._decision_engine.decide(return_request, order)
        return_request.decision = decision
        return decision

    def get_return(self, return_id: str) -> Optional[ReturnRequest]:
        return self._returns.get(return_id)

    def _get_order_or_raise(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order '{order_id}' does not exist.")
        return order

    def _get_return_or_raise(self, return_id: str) -> ReturnRequest:
        return_request = self._returns.get(return_id)
        if return_request is None:
            raise ReturnNotFoundError(f"Return '{return_id}' does not exist.")
        return return_request

    @staticmethod
    def _validate_reason_or_raise(reason: str) -> None:
        if reason not in RETURN_REASONS.values():
            valid = ", ".join(sorted(RETURN_REASONS.values()))
            raise InvalidReturnReasonError(
                f"Reason '{reason}' is not recognized. Valid reasons: {valid}."
            )

    def _validate_items_or_raise(
        self, order: Order, items: Iterable[ReturnItemInput]
    ) -> List[ReturnLineItem]:
        items = list(items)
        if not items:
            raise InvalidReturnItemsError("At least one item must be specified for a return.")

        already_requested = self._quantity_already_in_flight(order.order_id)
        line_items: List[ReturnLineItem] = []
        for raw_item in items:
            item_id, quantity = self._parse_item(raw_item)

            order_item = order.find_item(item_id)
            if order_item is None:
                raise InvalidReturnItemsError(
                    f"Item '{item_id}' is not part of order '{order.order_id}'."
                )
            if quantity <= 0:
                raise InvalidReturnItemsError(
                    f"Return quantity for item '{item_id}' must be positive."
                )

            remaining = order_item.quantity - already_requested.get(item_id, 0)
            if quantity > remaining:
                raise InvalidReturnItemsError(
                    f"Cannot return {quantity} of item '{item_id}'; only {remaining} remaining."
                )

            line_items.append(ReturnLineItem(item_id=item_id, quantity=quantity))
            already_requested[item_id] = already_requested.get(item_id, 0) + quantity

        return line_items

    @staticmethod
    def _parse_item(raw_item: ReturnItemInput) -> (str, int):
        if isinstance(raw_item, ReturnLineItem):
            return raw_item.item_id, raw_item.quantity
        if isinstance(raw_item, dict):
            return raw_item["item_id"], raw_item.get("quantity", 1)
        return raw_item, 1  # bare item_id string

    def _quantity_already_in_flight(self, order_id: str) -> Dict[str, int]:
        """Sum quantities already requested for this order across returns
        that haven't been rejected (a rejected return frees the item back up)."""
        totals: Dict[str, int] = {}
        for existing in self._returns.values():
            if existing.order_id != order_id or existing.status == RETURN_STATUSES["REJECTED"]:
                continue
            for line_item in existing.items:
                totals[line_item.item_id] = totals.get(line_item.item_id, 0) + line_item.quantity
        return totals

    def _generate_return_id(self, order_id: str) -> str:
        return f"ret_{order_id}_{next(self._id_counter)}"
