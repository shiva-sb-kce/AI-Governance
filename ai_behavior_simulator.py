import time
import uuid
import requests


BASE_URL = "http://127.0.0.1:8000"


class AIBehaviorSimulator:

    def __init__(self):
        self.gateway_url = (
            f"{BASE_URL}/behavior/ingest"
        )

    def send_behavior(
        self,
        agent_id,
        role,
        tool,
        resource=None,
        parameters=None,
    ):

        request_id = (
            f"AI-{uuid.uuid4().hex[:8].upper()}"
        )

        payload = {
            "request_id": request_id,
            "agent_id": agent_id,
            "role": role,
            "tool": tool,
            "resource": resource,
            "parameters": parameters or {},
        }

        print()
        print("=" * 60)
        print("AI BEHAVIOR OBSERVED")
        print("=" * 60)

        print(f"Agent    : {agent_id}")
        print(f"Action   : {tool}")
        print(f"Resource : {resource}")
        print(f"Request  : {request_id}")

        try:

            response = requests.post(
                self.gateway_url,
                json=payload,
                timeout=10,
            )

            response.raise_for_status()

            result = response.json()

            governance = result.get(
                "governance",
                {},
            )

            print()
            print(
                f"Decision : "
                f"{governance.get('decision', '-')}"
            )

            print(
                f"Risk     : "
                f"{governance.get('risk_score', '-')}"
            )

            print(
                f"Execution: "
                f"{governance.get('executed', False)}"
            )

            return result

        except requests.RequestException as exc:

            print(
                f"Gateway error: {exc}"
            )

            return None


def main():

    simulator = AIBehaviorSimulator()

    print()
    print("=" * 60)
    print("UNIFIED AI GOVERNANCE")
    print("AI BEHAVIOR SIMULATOR")
    print("=" * 60)

    print()
    print(
        "Simulating an external AI agent..."
    )

    time.sleep(1)

    # ---------------------------------------------------------
    # BEHAVIOR 1: SAFE READ
    # ---------------------------------------------------------

    simulator.send_behavior(
        agent_id="research-agent",
        role="AGENT",
        tool="read_file",
        resource="demo.txt",
        parameters={},
    )

    time.sleep(3)

    # ---------------------------------------------------------
    # BEHAVIOR 2: DANGEROUS COMMAND
    # ---------------------------------------------------------

    simulator.send_behavior(
        agent_id="system-agent",
        role="AGENT",
        tool="execute_command",
        resource="system",
        parameters={
            "command": "whoami"
        },
    )

    time.sleep(3)

    # ---------------------------------------------------------
    # BEHAVIOR 3: WRITE FILE
    # ---------------------------------------------------------

    simulator.send_behavior(
        agent_id="report-agent",
        role="ADMIN",
        tool="write_file",
        resource="auto_behavior_report.txt",
        parameters={
            "content":
                "Automatically generated AI report."
        },
    )

    print()
    print("=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
    