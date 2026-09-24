from collections import Counter

from audit.audit_logger import AuditLogger


class DashboardService:

    def __init__(self, audit_logger=None):
        self.audit_logger = (
            audit_logger
            or AuditLogger()
        )

    def get_events(self):
        return self.audit_logger.read_all()

    def get_request_history(self, request_id):
        return (
            self.audit_logger.find_by_request(
                request_id
            )
        )

    def get_summary(self):

        events = self.get_events()

        decisions = Counter()
        threats = Counter()
        entities = Counter()
        actions = Counter()

        risk_scores = []

        for event in events:

            decision = event.get(
                "decision"
            )

            if decision:
                decisions[decision] += 1

            entity = event.get(
                "entity",
                {}
            )

            entity_type = entity.get(
                "type"
            )

            if entity_type:
                entities[entity_type] += 1

            action = event.get(
                "action"
            )

            if action:
                actions[action] += 1

            for threat in event.get(
                "threats",
                []
            ):
                threats[threat] += 1

            risk = event.get(
                "risk",
                {}
            )

            score = risk.get(
                "score"
            )

            if isinstance(
                score,
                (int, float)
            ):
                risk_scores.append(score)

        total_events = len(events)

        average_risk = (
            round(
                sum(risk_scores)
                / len(risk_scores),
                2
            )
            if risk_scores
            else 0
        )

        return {
            "total_events": total_events,

            "decisions": {
                "ALLOW": decisions.get(
                    "ALLOW",
                    0
                ),
                "BLOCK": decisions.get(
                    "BLOCK",
                    0
                ),
                "APPROVAL": decisions.get(
                    "APPROVAL",
                    0
                ),
                "MONITOR": decisions.get(
                    "MONITOR",
                    0
                ),
            },

            "average_risk": average_risk,

            "threats": dict(
                threats
            ),

            "entities": dict(
                entities
            ),

            "actions": dict(
                actions
            ),
        }

    def get_recent_events(
        self,
        limit=20
    ):

        events = self.get_events()

        return events[
            -limit:
        ][::-1]