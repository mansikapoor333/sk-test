"""Refund decision policy for return requests.

Stage 1 policy (see readme.md):
    - reason == DAMAGED: auto-refund the value of the items being returned.
    - otherwise: no immediate refund, route to manual review.

Implemented as a small ordered rule chain (rather than one if/else) so new
reasons, thresholds, or cross-request signals can be layered in later
without rewriting existing rules — per the extensibility requirement in
requirements.txt.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from .decisions import REFUND_DECISIONS
from .models import Order, RefundDecision, ReturnRequest
from .reasons import RETURN_REASONS


class RefundRule(ABC):
    """A single rule that may decide a return's refund outcome.

    Return None to defer to the next rule in the chain.
    """

    @abstractmethod
    def evaluate(self, return_request: ReturnRequest, order: Order) -> Optional[RefundDecision]:
        raise NotImplementedError


class DamagedItemsAutoRefundRule(RefundRule):
    """Auto-refund the value of the returned items when reason is DAMAGED."""

    def evaluate(self, return_request: ReturnRequest, order: Order) -> Optional[RefundDecision]:
        if return_request.reason != RETURN_REASONS["DAMAGED"]:
            return None

        refund_amount = self._returned_items_value(return_request, order)
        return RefundDecision(
            decision=REFUND_DECISIONS["AUTO_REFUND"], refund_amount=refund_amount
        )

    @staticmethod
    def _returned_items_value(return_request: ReturnRequest, order: Order) -> Decimal:
        total = Decimal("0.00")
        for line_item in return_request.items:
            order_item = order.find_item(line_item.item_id)
            if order_item is not None:
                total += order_item.unit_price * line_item.quantity
        return total


class DefaultManualReviewRule(RefundRule):
    """Fallback rule: route to manual review with no immediate refund."""

    def evaluate(self, return_request: ReturnRequest, order: Order) -> Optional[RefundDecision]:
        return RefundDecision(
            decision=REFUND_DECISIONS["MANUAL_REVIEW"], refund_amount=Decimal("0.00")
        )


class RefundDecisionEngine:
    """Runs an ordered chain of rules and returns the first decision reached.

    Rules are checked in order; the first one to return a non-None
    RefundDecision wins. A custom rule list can be supplied to
    override/extend the default Stage 1 policy.
    """

    def __init__(self, rules: Optional[List[RefundRule]] = None):
        self._rules: List[RefundRule] = (
            rules
            if rules is not None
            else [DamagedItemsAutoRefundRule(), DefaultManualReviewRule()]
        )

    def decide(self, return_request: ReturnRequest, order: Order) -> RefundDecision:
        for rule in self._rules:
            decision = rule.evaluate(return_request, order)
            if decision is not None:
                return decision
        return RefundDecision(
            decision=REFUND_DECISIONS["MANUAL_REVIEW"], refund_amount=Decimal("0.00")
        )
