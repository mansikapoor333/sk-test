"""Return status vocabulary and the state machine describing valid transitions.

Kept as a plain dict (rather than an enum) so it's trivial to inspect/serialize
and to extend with new statuses as the Returns Desk grows.
"""

RETURN_STATUSES = {
    "REQUESTED": "requested",
    "APPROVED": "approved",
    "RECEIVED": "received",
    "REFUNDED": "refunded",
    "REJECTED": "rejected",
    "CLOSED": "closed",
}

# Which statuses a return may move to next, from a given status.
VALID_TRANSITIONS = {
    RETURN_STATUSES["REQUESTED"]: {RETURN_STATUSES["APPROVED"], RETURN_STATUSES["REJECTED"]},
    RETURN_STATUSES["APPROVED"]: {RETURN_STATUSES["RECEIVED"], RETURN_STATUSES["REJECTED"]},
    RETURN_STATUSES["RECEIVED"]: {RETURN_STATUSES["REFUNDED"], RETURN_STATUSES["REJECTED"]},
    RETURN_STATUSES["REFUNDED"]: {RETURN_STATUSES["CLOSED"]},
    RETURN_STATUSES["REJECTED"]: {RETURN_STATUSES["CLOSED"]},
    RETURN_STATUSES["CLOSED"]: set(),
}
