from decimal import Decimal

import pytest

from returns_desk_refund_system import (
    InvalidReturnItemsError,
    InvalidReturnReasonError,
    Order,
    OrderItem,
    OrderNotFoundError,
    RETURN_REASONS,
    RETURN_STATUSES,
    RefundDecisionEngine,
    ReturnDeskService,
    ReturnLineItem,
    ReturnNotFoundError,
)


@pytest.fixture
def order() -> Order:
    return Order(
        order_id="o100",
        buyer_email="alice@example.com",
        items=[
            OrderItem(item_id="item_1", sku="SKU-1", quantity=2, unit_price=Decimal("20.00")),
            OrderItem(item_id="item_2", sku="SKU-2", quantity=1, unit_price=Decimal("15.00")),
        ],
    )


@pytest.fixture
def service(order) -> ReturnDeskService:
    return ReturnDeskService(orders={order.order_id: order})


class TestSubmitReturn:
    """Covers ReturnDeskService.submit_return."""

    @pytest.mark.parametrize(
        "items, reason, actor, expected_quantity",
        [
            ([{"item_id": "item_1", "quantity": 1}], RETURN_REASONS["DAMAGED"], "customer", 1),
            (["item_2"], RETURN_REASONS["CHANGED_MIND"], "customer", 1),
            (["item_1"], RETURN_REASONS["DAMAGED"], "support_agent", 1),
            (
                [ReturnLineItem(item_id="item_1", quantity=2)],
                RETURN_REASONS["DAMAGED"],
                "customer",
                2,
            ),
        ],
        ids=[
            "dict-item-damaged",
            "bare-item-id-default-quantity",
            "custom-actor",
            "return-line-item-instance",
        ],
    )
    def test_submit_return_success(self, service, items, reason, actor, expected_quantity):
        result = service.submit_return(order_id="o100", items=items, reason=reason, actor=actor)

        assert result.status == RETURN_STATUSES["REQUESTED"]
        assert result.order_id == "o100"
        assert result.reason == reason
        assert result.actor == actor
        assert result.decision is None
        assert result.items[0].quantity == expected_quantity
        assert service.get_return(result.return_id) is result

    @pytest.mark.parametrize(
        "order_id, items, reason, expected_exception",
        [
            ("does_not_exist", ["item_1"], RETURN_REASONS["DAMAGED"], OrderNotFoundError),
            ("o100", ["item_1"], "NOT_A_REASON", InvalidReturnReasonError),
            ("o100", ["not_in_order"], RETURN_REASONS["DAMAGED"], InvalidReturnItemsError),
            ("o100", [], RETURN_REASONS["DAMAGED"], InvalidReturnItemsError),
            (
                "o100",
                [{"item_id": "item_1", "quantity": 0}],
                RETURN_REASONS["DAMAGED"],
                InvalidReturnItemsError,
            ),
            (
                "o100",
                [{"item_id": "item_1", "quantity": 3}],
                RETURN_REASONS["DAMAGED"],
                InvalidReturnItemsError,
            ),
        ],
        ids=[
            "unknown-order",
            "invalid-reason",
            "item-not-in-order",
            "empty-items",
            "non-positive-quantity",
            "exceeds-purchased-quantity",
        ],
    )
    def test_submit_return_validation_errors(
        self, service, order_id, items, reason, expected_exception
    ):
        with pytest.raises(expected_exception):
            service.submit_return(order_id=order_id, items=items, reason=reason)

    def test_second_return_respects_quantity_already_in_flight(self, service):
        service.submit_return(
            order_id="o100",
            items=[{"item_id": "item_1", "quantity": 2}],
            reason=RETURN_REASONS["DAMAGED"],
        )

        with pytest.raises(InvalidReturnItemsError):
            service.submit_return(
                order_id="o100",
                items=[{"item_id": "item_1", "quantity": 1}],
                reason=RETURN_REASONS["DAMAGED"],
            )

    def test_rejected_return_frees_up_item_for_resubmission(self, service):
        first = service.submit_return(
            order_id="o100",
            items=[{"item_id": "item_1", "quantity": 2}],
            reason=RETURN_REASONS["DAMAGED"],
        )
        first.status = RETURN_STATUSES["REJECTED"]

        second = service.submit_return(
            order_id="o100",
            items=[{"item_id": "item_1", "quantity": 2}],
            reason=RETURN_REASONS["DAMAGED"],
        )
        assert second.items[0].quantity == 2


class TestEvaluateReturn:
    """Covers ReturnDeskService.evaluate_return."""

    @pytest.mark.parametrize(
        "items, reason, expected_decision, expected_amount",
        [
            (
                [{"item_id": "item_1", "quantity": 1}],
                RETURN_REASONS["DAMAGED"],
                "AUTO_REFUND",
                Decimal("20.00"),
            ),
            (
                [{"item_id": "item_1", "quantity": 2}, {"item_id": "item_2", "quantity": 1}],
                RETURN_REASONS["DAMAGED"],
                "AUTO_REFUND",
                Decimal("55.00"),
            ),
            (
                [{"item_id": "item_1", "quantity": 1}],
                RETURN_REASONS["CHANGED_MIND"],
                "MANUAL_REVIEW",
                Decimal("0.00"),
            ),
            (
                [{"item_id": "item_2", "quantity": 1}],
                RETURN_REASONS["NOT_RECEIVED"],
                "MANUAL_REVIEW",
                Decimal("0.00"),
            ),
        ],
        ids=[
            "damaged-single-item-auto-refund",
            "damaged-multiple-items-sums-value",
            "changed-mind-manual-review",
            "not-received-manual-review",
        ],
    )
    def test_evaluate_return_decision(
        self, service, items, reason, expected_decision, expected_amount
    ):
        return_request = service.submit_return(order_id="o100", items=items, reason=reason)

        decision = service.evaluate_return(return_request.return_id)

        assert decision.decision == expected_decision
        assert decision.refund_amount == expected_amount
        assert return_request.decision is decision

    def test_evaluate_return_raises_for_unknown_return_id(self, service):
        with pytest.raises(ReturnNotFoundError):
            service.evaluate_return("does_not_exist")
