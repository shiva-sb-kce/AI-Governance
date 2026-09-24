from datetime import datetime, timezone
from typing import List, Optional

from models.schemas import AuditEvent


class AuditService:

    def __init__(self):
        self._events: List[AuditEvent] = []

    # --------------------------------------------------
    # CREATE AUDIT EVENT
    # --------------------------------------------------

    def log_event(
        self,
        request_id: str,
        entity_type,
        entity_id: str,
        action: Optional[str],
        risk_score: int,
        risk_level,
        decision,
        threats=None,
        policies=None,
        approval_status=None,
        details=None
    ) -> AuditEvent:

        event = AuditEvent(
            audit_id=self._generate_audit_id(),
            request_id=request_id,
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),

            entity_type=entity_type,
            entity_id=entity_id,

            action=action,

            risk_score=risk_score,
            risk_level=risk_level,

            threats=threats or [],
            policies=policies or [],

            decision=decision,

            approval_status=(
                approval_status
                if approval_status is not None
                else "NOT_REQUIRED"
            ),

            details=details or {}
        )

        self._events.append(event)

        return event

    # --------------------------------------------------
    # GET ALL EVENTS
    # --------------------------------------------------

    def get_events(self) -> List[AuditEvent]:
        return list(
            reversed(self._events)
        )

    # --------------------------------------------------
    # GET RECENT EVENTS
    # --------------------------------------------------

    def get_recent(
        self,
        limit: int = 15
    ) -> List[AuditEvent]:

        if limit < 1:
            limit = 1

        return self.get_events()[:limit]

    # --------------------------------------------------
    # GET BY REQUEST ID
    # --------------------------------------------------

    def get_by_request(
        self,
        request_id: str
    ) -> List[AuditEvent]:

        return [
            event
            for event in self._events
            if event.request_id == request_id
        ]

    # --------------------------------------------------
    # GET BY DECISION
    # --------------------------------------------------

    def get_by_decision(
        self,
        decision
    ) -> List[AuditEvent]:

        return [
            event
            for event in self._events
            if event.decision == decision
        ]

    # --------------------------------------------------
    # CLEAR EVENTS
    # --------------------------------------------------

    def clear(self):
        self._events.clear()

    # --------------------------------------------------
    # ID GENERATOR
    # --------------------------------------------------

    @staticmethod
    def _generate_audit_id():

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S%f"
        )

        return f"AUD-{timestamp}"