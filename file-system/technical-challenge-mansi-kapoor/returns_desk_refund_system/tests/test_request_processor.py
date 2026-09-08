from decimal import Decimal

import pytest

from returns_desk_refund_system import (
    ERROR_RESULT,
    normalize_email,
    process_return_requests,
)


class TestProcessReturnRequestsStage1Sample:
    """Locks in the exact Stage 1 sample from readme.md."""

    def test_readme_sample_input_output(self):
        requests = [
            ("r1", "o100", "Alice@Example.com ", "addr_1", "card_A", 120.00, "DAMAGED"),
            ("r2", "o101", "bob@example.com", "addr_2", "card_B", 80.00, "CHANGED_MIND"),
            ("r3", "o102", "cathy@example.com", "addr_3", "card_C", 35.50, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("120.00"), "AUTO_REFUND"),
            ("r2", Decimal("0.00"), "MANUAL_REVIEW"),
            ("r3", Decimal("35.50"), "AUTO_REFUND"),
        ]


class TestProcessReturnRequestsDecisionByReason:
    """Covers requirements.txt section 4 (Stage 1 policy) and section 7
    (missing reason -> MANUAL_REVIEW)."""

    @pytest.mark.parametrize(
        "reason, expected_amount, expected_decision",
        [
            ("DAMAGED", Decimal("50.00"), "AUTO_REFUND"),
            ("NOT_RECEIVED", Decimal("0.00"), "MANUAL_REVIEW"),
            ("CHANGED_MIND", Decimal("0.00"), "MANUAL_REVIEW"),
            (None, Decimal("0.00"), "MANUAL_REVIEW"),
            ("", Decimal("0.00"), "MANUAL_REVIEW"),
            ("SOME_UNKNOWN_REASON", Decimal("0.00"), "MANUAL_REVIEW"),
        ],
        ids=[
            "damaged-auto-refund",
            "not-received-manual-review",
            "changed-mind-manual-review",
            "reason-none-manual-review",
            "reason-blank-manual-review",
            "unrecognized-reason-manual-review",
        ],
    )
    def test_decision_by_reason(self, reason, expected_amount, expected_decision):
        requests = [("r1", "o100", "alice@example.com", "addr_1", "card_A", 50.00, reason)]

        [result] = process_return_requests(requests)

        assert result == ("r1", expected_amount, expected_decision)


class TestProcessReturnRequestsMissingRequiredFields:
    """Covers requirements.txt section 7 (Edge cases) — missing required
    fields produce the literal string "ERROR" at that position."""

    @pytest.mark.parametrize(
        "request_id, buyer_email, shipping_address_id, payment_fingerprint, order_total",
        [
            (None, "alice@example.com", "addr_1", "card_A", 50.00),
            ("r1", None, "addr_1", "card_A", 50.00),
            ("r1", "alice@example.com", None, "card_A", 50.00),
            ("r1", "alice@example.com", "addr_1", None, 50.00),
            ("r1", "alice@example.com", "addr_1", "card_A", None),
            ("", "alice@example.com", "addr_1", "card_A", 50.00),
            ("r1", "  ", "addr_1", "card_A", 50.00),
        ],
        ids=[
            "missing-request-id",
            "missing-buyer-email",
            "missing-shipping-address-id",
            "missing-payment-fingerprint",
            "missing-order-total",
            "blank-request-id",
            "blank-buyer-email",
        ],
    )
    def test_missing_required_field_returns_error(
        self, request_id, buyer_email, shipping_address_id, payment_fingerprint, order_total
    ):
        requests = [
            (
                request_id,
                "o100",
                buyer_email,
                shipping_address_id,
                payment_fingerprint,
                order_total,
                "DAMAGED",
            )
        ]

        results = process_return_requests(requests)

        assert results == [ERROR_RESULT]

    def test_batch_preserves_order_and_count_with_mixed_valid_and_error_requests(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 120.00, "DAMAGED"),
            (None, "o101", "bob@example.com", "addr_2", "card_B", 80.00, "CHANGED_MIND"),
            ("r3", "o102", "cathy@example.com", "addr_3", "card_C", 35.50, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("120.00"), "AUTO_REFUND"),
            ERROR_RESULT,
            ("r3", Decimal("35.50"), "AUTO_REFUND"),
        ]


class TestProcessReturnRequestsDataHandling:
    """Covers requirements.txt section 5 (Data handling)."""

    def test_buyer_email_casing_and_whitespace_does_not_affect_outcome(self):
        requests = [("r1", "o100", " Alice@Example.com ", "addr_1", "card_A", 10.00, "DAMAGED")]

        [result] = process_return_requests(requests)

        assert result == ("r1", Decimal("10.00"), "AUTO_REFUND")

    def test_order_total_is_treated_as_precise_decimal(self):
        requests = [("r1", "o100", "alice@example.com", "addr_1", "card_A", "35.50", "DAMAGED")]

        [result] = process_return_requests(requests)

        assert result[1] == Decimal("35.50")
        assert isinstance(result[1], Decimal)

    def test_empty_batch_returns_empty_list(self):
        assert process_return_requests([]) == []

    def test_non_numeric_order_total_returns_error(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", "not-a-number", "DAMAGED")
        ]

        results = process_return_requests(requests)

        assert results == [ERROR_RESULT]


class TestNormalizeEmail:
    """Covers request_processor.normalize_email (Stage 2)."""

    @pytest.mark.parametrize(
        "raw_email, expected",
        [
            ("alice@example.com", "alice@example.com"),
            ("Alice@Example.com", "alice@example.com"),
            (" alice@example.com ", "alice@example.com"),
            ("alice.b@example.com", "aliceb@example.com"),
            ("Al.ice.B@Example.com ", "aliceb@example.com"),
            ("a.l.i.c.e@example.com", "alice@example.com"),
        ],
        ids=[
            "already-normalized",
            "casing",
            "whitespace",
            "dots-in-local-part",
            "casing-whitespace-and-dots-combined",
            "many-dots",
        ],
    )
    def test_normalize_email(self, raw_email, expected):
        assert normalize_email(raw_email) == expected

    def test_normalize_email_does_not_strip_dots_from_domain(self):
        assert normalize_email("Alice@Sub.Example.com") == "alice@sub.example.com"


class TestProcessReturnRequestsStage2Sample:
    """Locks in the exact Stage 2 sample from readme.md (daily cap = $200)."""

    def test_readme_stage_2_sample(self):
        requests = [
            ("r1", "o200", "Alice@Example.com ", "addr_1", "card_A", 120.00, "DAMAGED"),
            ("r2", "o201", "alice@example.com", "addr_4", "card_D", 90.00, "DAMAGED"),
            ("r3", "o202", "alice@example.com", "addr_5", "card_E", 50.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("120.00"), "AUTO_REFUND"),
            ("r2", Decimal("80.00"), "MANUAL_REVIEW"),
            ("r3", Decimal("0.00"), "MANUAL_REVIEW"),
        ]


class TestProcessReturnRequestsDailyCap:
    """Covers requirements.txt / readme.md Stage 2 — per-buyer daily
    auto-refund cap."""

    def test_requests_under_cap_are_all_auto_refunded(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 50.00, "DAMAGED"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 50.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("50.00"), "AUTO_REFUND"),
            ("r2", Decimal("50.00"), "AUTO_REFUND"),
        ]

    def test_request_exactly_at_cap_boundary_is_fully_auto_refunded(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 200.00, "DAMAGED"),
        ]

        [result] = process_return_requests(requests)

        assert result == ("r1", Decimal("200.00"), "AUTO_REFUND")

    def test_request_exceeding_cap_refunds_remaining_amount_and_flags_review(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 150.00, "DAMAGED"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 100.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("150.00"), "AUTO_REFUND"),
            ("r2", Decimal("50.00"), "MANUAL_REVIEW"),
        ]

    def test_request_after_cap_fully_reached_gets_zero_refund(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 200.00, "DAMAGED"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 10.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("200.00"), "AUTO_REFUND"),
            ("r2", Decimal("0.00"), "MANUAL_REVIEW"),
        ]

    def test_cap_is_tracked_per_normalized_buyer_not_raw_email(self):
        requests = [
            ("r1", "o100", "Alice.B@Example.com", "addr_1", "card_A", 150.00, "DAMAGED"),
            ("r2", "o101", " aliceb@example.com ", "addr_2", "card_B", 100.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("150.00"), "AUTO_REFUND"),
            ("r2", Decimal("50.00"), "MANUAL_REVIEW"),
        ]

    def test_cap_is_independent_per_buyer(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 200.00, "DAMAGED"),
            ("r2", "o101", "bob@example.com", "addr_2", "card_B", 200.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("200.00"), "AUTO_REFUND"),
            ("r2", Decimal("200.00"), "AUTO_REFUND"),
        ]

    def test_manual_review_requests_do_not_consume_the_cap(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 300.00, "CHANGED_MIND"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 200.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ("r1", Decimal("0.00"), "MANUAL_REVIEW"),
            ("r2", Decimal("200.00"), "AUTO_REFUND"),
        ]

    def test_request_missing_a_required_field_does_not_consume_the_cap(self):
        requests = [
            (None, "o100", "alice@example.com", "addr_1", "card_A", 150.00, "DAMAGED"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 150.00, "DAMAGED"),
        ]

        results = process_return_requests(requests)

        assert results == [
            ERROR_RESULT,
            ("r2", Decimal("150.00"), "AUTO_REFUND"),
        ]

    def test_custom_daily_auto_refund_cap(self):
        requests = [
            ("r1", "o100", "alice@example.com", "addr_1", "card_A", 60.00, "DAMAGED"),
            ("r2", "o101", "alice@example.com", "addr_2", "card_B", 60.00, "DAMAGED"),
        ]

        results = process_return_requests(requests, daily_auto_refund_cap=Decimal("100.00"))

        assert results == [
            ("r1", Decimal("60.00"), "AUTO_REFUND"),
            ("r2", Decimal("40.00"), "MANUAL_REVIEW"),
        ]
