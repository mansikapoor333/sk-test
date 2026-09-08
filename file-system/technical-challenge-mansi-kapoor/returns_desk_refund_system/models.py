"""Typed data models for orders and return requests.

Kept separate from the service so parsing/representation can evolve
independently of the decision/workflow logic (per requirements.txt).
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Optional



@dataclass(frozen=True)
class OrderItem:
    """A single line item that was purchased on an order."""

    item_id: str
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class Order:
    """An existing order that a customer may request a return against."""

    order_id: str
    buyer_email: str
    items: List[OrderItem]

    def find_item(self, item_id: str) -> Optional[OrderItem]:
        return next((item for item in self.items if item.item_id == item_id), None)


@dataclass
class ReturnLineItem:
    """A quantity of a specific order item being requested for return."""

    item_id: str
    quantity: int


@dataclass
class RefundDecision:
    """The outcome of running a return request through the refund policy."""

    decision: str  # "AUTO_REFUND" or "MANUAL_REVIEW"
    refund_amount: Decimal


@dataclass
class ReturnRequest:
    """A return request moving through the Returns Desk workflow."""

    return_id: str
    order_id: str
    items: List[ReturnLineItem]
    actor: str
    status: str
    reason: str
    decision: Optional[RefundDecision] = None
    history: List[Dict] = field(default_factory=list)
