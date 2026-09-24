import json
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

# audit/audit_logger.py
#        ↑
# parents[1] = AI-Governance project root

BASE_DIR = Path(__file__).resolve().parents[1]

DEFAULT_LOG_FILE = (
    BASE_DIR / "logs" / "audit.jsonl"
)


class AuditLogger:
    """
    Centralized audit logger for the
    Unified AI Governance & Security Platform.

    All components use the same absolute
    audit log location.
    """

    def __init__(self, log_file=None):

        # ----------------------------------------------------
        # Use one centralized project-level log file
        # ----------------------------------------------------

        if log_file is None:

            self.log_file = DEFAULT_LOG_FILE

        else:

            supplied_path = Path(log_file)

            # If caller gives a relative path,
            # resolve it from project root.
            if supplied_path.is_absolute():

                self.log_file = supplied_path

            else:

                self.log_file = (
                    BASE_DIR / supplied_path
                )

        # ----------------------------------------------------
        # Create logs directory
        # ----------------------------------------------------

        self.log_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    # ========================================================
    # WRITE AUDIT EVENT
    # ========================================================

    def log(
        self,
        event_type,
        request_id,
        decision=None,
        entity_type=None,
        entity_id=None,
        action=None,
        resource=None,
        risk_score=None,
        risk_level=None,
        threats=None,
        violated_policies=None,
        permission=None,
        approval_id=None,
        execution_status=None,
        reasons=None,
        metadata=None
    ):

        event = {

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "event_type":
                event_type,

            "request_id":
                request_id,

            "entity": {
                "type": entity_type,
                "id": entity_id
            },

            "action":
                action,

            "resource":
                resource,

            "decision":
                decision,

            "risk": {
                "score": risk_score,
                "level": risk_level
            },

            "threats":
                threats or [],

            "violated_policies":
                violated_policies or [],

            "permission":
                permission,

            "approval_id":
                approval_id,

            "execution_status":
                execution_status,

            "reasons":
                reasons or [],

            "metadata":
                metadata or {}
        }

        # ----------------------------------------------------
        # Append event to centralized JSONL file
        # ----------------------------------------------------

        with open(
            self.log_file,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False
                )
                + "\n"
            )

        return event

    # ========================================================
    # READ ALL EVENTS
    # ========================================================

    def read_all(self):

        if not self.log_file.exists():

            return []

        events = []

        with open(
            self.log_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line_number, line in enumerate(
                file,
                start=1
            ):

                line = line.strip()

                if not line:
                    continue

                try:

                    event = json.loads(line)

                    events.append(event)

                except json.JSONDecodeError:

                    # Ignore malformed lines instead
                    # of breaking the entire dashboard.
                    continue

        return events

    # ========================================================
    # FIND BY REQUEST ID
    # ========================================================

    def find_by_request(
        self,
        request_id
    ):

        events = self.read_all()

        return [
            event
            for event in events
            if event.get(
                "request_id"
            ) == request_id
        ]

    # ========================================================
    # FIND BY DECISION
    # ========================================================

    def find_by_decision(
        self,
        decision
    ):

        events = self.read_all()

        return [
            event
            for event in events
            if event.get(
                "decision"
            ) == decision
        ]

    # ========================================================
    # FIND BY EVENT TYPE
    # ========================================================

    def find_by_event_type(
        self,
        event_type
    ):

        events = self.read_all()

        return [
            event
            for event in events
            if event.get(
                "event_type"
            ) == event_type
        ]

    # ========================================================
    # COUNT EVENTS
    # ========================================================

    def count(self):

        return len(
            self.read_all()
        )

    # ========================================================
    # CLEAR LOG
    # ========================================================

    def clear(self):

        if self.log_file.exists():

            self.log_file.unlink()

    # ========================================================
    # LOG FILE PATH
    # ========================================================

    def get_log_file(self):

        return str(
            self.log_file
        )