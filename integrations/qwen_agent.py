import json
import urllib.request
from typing import Any, Dict

from models.schemas import ActionRequest


class QwenAgent:

    def __init__(
        self,
        governance_gateway,
        model: str = "qwen3:8b",
        ollama_url: str = "http://localhost:11434"
    ):
        self.gateway = governance_gateway
        self.model = model
        self.ollama_url = ollama_url.rstrip("/")

    # ==================================================
    # QWEN REQUEST
    # ==================================================

    def ask(self, prompt: str) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 128
            }
        }

        data = json.dumps(
            payload
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.ollama_url}/api/generate",
            data=data,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        return result.get(
            "response",
            ""
        )

    # ==================================================
    # GOVERNED QWEN REQUEST
    #
    # USER
    #   ↓
    # PRE-QWEN GOVERNANCE
    #   ↓
    # ALLOW / APPROVAL / BLOCK
    #   ↓
    # QWEN
    # ==================================================

    def propose_action(
        self,
        instruction: str,
        request_id: str,
        agent_id: str = "qwen-agent"
    ) -> Dict[str, Any]:

        # ==================================================
        # 1. PRE-QWEN GOVERNANCE
        # ==================================================

        governance_gate = (
            self.gateway.process_qwen_request(
                request_id=request_id,
                user_id=agent_id,
                role="AGENT",
                prompt=instruction,
                parameters={
                    "model": self.model,
                    "source": "QWEN_UI"
                }
            )
        )

        # ==================================================
        # 2. BLOCKED BEFORE QWEN
        # ==================================================

        if (
            governance_gate["decision"]
            == "BLOCK"
        ):

            return {
                "status": "BLOCKED",
                "agent_id": agent_id,
                "request_id": request_id,
                "qwen_response": None,
                "proposed_action": None,
                "governance": governance_gate,
                "stage": "PRE_QWEN_GOVERNANCE"
            }

        # ==================================================
        # 3. PENDING APPROVAL BEFORE QWEN
        # ==================================================

        if (
            governance_gate["decision"]
            == "APPROVAL"
        ):

            return {
                "status": "PENDING_APPROVAL",
                "agent_id": agent_id,
                "request_id": request_id,
                "qwen_response": None,
                "proposed_action": None,
                "governance": governance_gate,
                "stage": "PRE_QWEN_GOVERNANCE"
            }

        # ==================================================
        # 4. QWEN IS ALLOWED TO PROCESS REQUEST
        # ==================================================

        response = self.ask(
            instruction_prompt(instruction)
        )

        # ==================================================
        # 5. PARSE QWEN RESPONSE
        # ==================================================

        result = self._parse_response(
            response
        )

        # ==================================================
        # 6. NORMAL ANSWER
        # ==================================================

        if result["type"] == "answer":

            return {
                "status": "ANSWER",
                "agent_id": agent_id,
                "request_id": request_id,
                "qwen_response": response,
                "answer": result["answer"],

                "governance": {
                    **governance_gate,

                    "stage": (
                        "PRE_QWEN_GOVERNANCE"
                    ),

                    "qwen_allowed": True,

                    "execution_required": False,

                    "decision": "ALLOW"
                }
            }

        # ==================================================
        # 7. QWEN PROPOSED ACTION
        # ==================================================

        action_request = ActionRequest(
            action_id=(
                f"QWEN-{request_id}"
            ),

            request_id=request_id,

            agent_id=agent_id,

            tool=result["tool"],

            resource=result.get(
                "resource"
            ),

            parameters=result.get(
                "parameters",
                {}
            )
        )

        # ==================================================
        # 8. SECOND GOVERNANCE GATE
        #
        # QWEN ACTION
        #    ↓
        # ACTION GOVERNANCE
        #    ↓
        # ALLOW / APPROVAL / BLOCK
        # ==================================================

        action_governance = (
            self.gateway.process_action(
                action_request=action_request,
                role="AGENT"
            )
        )

        return {
            "status": "GOVERNED",
            "agent_id": agent_id,
            "request_id": request_id,

            "qwen_response": response,

            "proposed_action": {
                "tool": result["tool"],
                "resource": result.get(
                    "resource"
                ),
                "parameters": result.get(
                    "parameters",
                    {}
                )
            },

            "governance": action_governance,

            "pre_qwen_governance": (
                governance_gate
            ),

            "stage": "ACTION_GOVERNANCE"
        }

    # ==================================================
    # RESPONSE PARSER
    # ==================================================

    @staticmethod
    def _parse_response(
        response: str
    ) -> Dict[str, Any]:

        response = response.strip()

        # ==================================================
        # REMOVE MARKDOWN FENCES
        # ==================================================

        if response.startswith("```"):

            lines = response.splitlines()

            if (
                lines
                and lines[0].startswith("```")
            ):
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            response = "\n".join(
                lines
            ).strip()

        # ==================================================
        # HELPER — PARSE ACTION OBJECT
        # ==================================================

        def parse_action(data):

            if not isinstance(data, dict):
                return None

            if data.get("type") != "action":
                return None

            tool = data.get(
                "tool",
                "none"
            )

            if tool == "none":
                return None

            return {
                "type": "action",
                "tool": tool,
                "resource": data.get(
                    "resource"
                ),
                "parameters": data.get(
                    "parameters",
                    {}
                )
            }

        # ==================================================
        # PARSE OUTER JSON
        # ==================================================

        try:

            data = json.loads(
                response
            )

            if not isinstance(
                data,
                dict
            ):
                raise ValueError(
                    "Qwen response is not a JSON object."
                )

            response_type = data.get(
                "type",
                "answer"
            )

            # ==================================================
            # DIRECT ACTION
            # ==================================================

            if response_type == "action":

                action = parse_action(
                    data
                )

                if action:
                    return action

            # ==================================================
            # NORMAL ANSWER
            # ==================================================

            if response_type == "answer":

                answer = data.get(
                    "answer",
                    ""
                )

                # --------------------------------------------------
                # IMPORTANT FIX:
                # Qwen sometimes puts ACTION JSON inside "answer"
                # --------------------------------------------------

                if isinstance(
                    answer,
                    str
                ):

                    nested = answer.strip()

                    if nested.startswith("```"):

                        nested_lines = (
                            nested.splitlines()
                        )

                        if (
                            nested_lines
                            and nested_lines[0].startswith("```")
                        ):
                            nested_lines = nested_lines[1:]

                        if (
                            nested_lines
                            and nested_lines[-1].strip() == "```"
                        ):
                            nested_lines = (
                                nested_lines[:-1]
                            )

                        nested = "\n".join(
                            nested_lines
                        ).strip()

                    try:

                        nested_data = json.loads(
                            nested
                        )

                        nested_action = parse_action(
                            nested_data
                        )

                        if nested_action:

                            return nested_action

                    except (
                        json.JSONDecodeError,
                        ValueError
                    ):
                        pass

                # --------------------------------------------------
                # Genuine normal answer
                # --------------------------------------------------

                return {
                    "type": "answer",
                    "answer": answer
                }

            # ==================================================
            # UNKNOWN TYPE
            # ==================================================

            return {
                "type": "answer",
                "answer": data.get(
                    "answer",
                    response
                )
            }

        except (
            json.JSONDecodeError,
            ValueError
        ):

            return {
                "type": "answer",
                "answer": response
            }

# ==================================================
# QWEN PROMPT
# ==================================================

def instruction_prompt(
    instruction: str
) -> str:

    return f"""
You are Qwen3:8B, a local AI agent operating
under a security governance system.

The user's request has already passed the
pre-Qwen security governance gate.

User request:
{instruction}

Now determine what the user wants.

==================================================
CASE 1 — NORMAL QUESTION
==================================================

If the user is asking an informational question
and no computer, file, system, database, email,
or external action is required, answer directly.

Return ONLY valid JSON:

{{
    "type": "answer",
    "answer": "Your answer here"
}}

==================================================
CASE 2 — ACTION REQUEST
==================================================

If the user wants an action performed using a tool,
DO NOT execute the action yourself.

Instead propose the action for the Governance Engine.

Return ONLY valid JSON:

{{
    "type": "action",
    "tool": "read_file",
    "resource": "demo.txt",
    "parameters": {{}}
}}

Allowed tools:

- read_file
- write_file
- delete_file
- execute_command
- send_email
- database_read
- database_write

==================================================
EXAMPLES
==================================================

User:
"What is machine learning?"

Return:

{{
    "type": "answer",
    "answer": "Machine learning is a branch of artificial intelligence..."
}}

User:
"Read demo.txt"

Return:

{{
    "type": "action",
    "tool": "read_file",
    "resource": "demo.txt",
    "parameters": {{}}
}}

User:
"Execute the system command whoami"

Return:

{{
    "type": "action",
    "tool": "execute_command",
    "resource": "whoami",
    "parameters": {{}}
}}

User:
"Write hello into report.txt"

Return:

{{
    "type": "action",
    "tool": "write_file",
    "resource": "report.txt",
    "parameters": {{
        "content": "hello"
    }}
}}

IMPORTANT:

Return ONLY valid JSON.

Do not use markdown.

Do not use code fences.

Do not execute any action yourself.
"""