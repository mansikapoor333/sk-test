from decimal import Decimal

from returns_desk_refund_system import (
    Order,
    OrderItem,
    RETURN_REASONS,
    RefundDecisionEngine,
    ReturnLineItem,
    ReturnRequest,
)


def make_order() -> Order:
    return Order(
        order_id="o100",
        buyer_email="alice@example.com",
        items=[OrderItem(item_id="item_1", sku="SKU-1", quantity=1, unit_price=Decimal("20.00"))],
    )


def make_return_request(reason: str) -> ReturnRequest:
    return ReturnRequest(
        return_id="ret_1",
        order_id="o100",
        items=[ReturnLineItem(item_id="item_1", quantity=1)],
        actor="customer",
        status="requested",
        reason=reason,
    )


class TestRefundDecisionEngine:
    def test_engine_with_no_rules_defaults_to_manual_review(self):
        engine = RefundDecisionEngine(rules=[])
        order = make_order()
        return_request = make_return_request(RETURN_REASONS["DAMAGED"])

        decision = engine.decide(return_request, order)

        assert decision.decision == "MANUAL_REVIEW"
        assert decision.refund_amount == Decimal("0.00")
