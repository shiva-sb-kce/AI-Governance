from pathlib import Path
import json

from models.schemas import Decision
from security.output_validator import OutputValidator


class SecureExecutor:

    def __init__(
        self,
        sandbox_dir="sandbox",
        output_validator=None
    ):
        self.sandbox_dir = Path(sandbox_dir)

        self.sandbox_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_validator = (
            output_validator
            or OutputValidator()
        )

    # ==================================================
    # MAIN EXECUTION ENTRY
    # ==================================================

    def execute(
        self,
        action_request,
        governance_result
    ):

        # ----------------------------------------------
        # SECURITY BOUNDARY
        # ----------------------------------------------

        if governance_result.decision != Decision.ALLOW:

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": (
                    "Execution denied because governance "
                    "decision is not ALLOW."
                )
            }

        # ----------------------------------------------
        # Dispatch supported tools
        # ----------------------------------------------

        tool = action_request.tool

        if tool == "read_file":

            execution_result = self._read_file(
                action_request
            )

        elif tool == "write_file":

            execution_result = self._write_file(
                action_request
            )

        else:

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": (
                    f"Tool '{tool}' is not enabled "
                    "for local execution."
                )
            }

        # ----------------------------------------------
        # If execution itself failed/blocked,
        # don't perform output validation.
        # ----------------------------------------------

        if not execution_result.get(
            "executed",
            False
        ):

            return execution_result

        # ----------------------------------------------
        # OUTPUT SECURITY
        # ----------------------------------------------

        output = execution_result.get(
            "result"
        )

        # write_file doesn't normally return content.
        # There is nothing sensitive to validate.
        if output is None:

            return execution_result

        validation = (
            self.output_validator.validate(
                self._serialize_output(output)
            )
        )

        # ----------------------------------------------
        # BLOCK unsafe output
        # ----------------------------------------------

        if not self._output_is_valid(
            validation
        ):

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": (
                    "Output security validation failed."
                ),
                "output_blocked": True,
                "output_security": (
                    self._validation_details(
                        validation
                    )
                )
            }

        # ----------------------------------------------
        # Safe output
        # ----------------------------------------------

        execution_result[
            "output_validated"
        ] = True

        execution_result[
            "output_security"
        ] = self._validation_details(
            validation
        )

        return execution_result

    # ==================================================
    # OUTPUT HELPERS
    # ==================================================

    @staticmethod
    def _serialize_output(output):

        if isinstance(output, str):
            return output

        try:
            return json.dumps(
                output,
                ensure_ascii=False,
                default=str
            )

        except Exception:
            return str(output)

    @staticmethod
    def _output_is_valid(
        validation
    ):

        # Supports dictionary-style validator
        # results.

        if isinstance(
            validation,
            dict
        ):

            return validation.get(
                "valid",
                not (
                    validation.get(
                        "pii_detected",
                        False
                    )
                    or validation.get(
                        "secret_detected",
                        False
                    )
                    or validation.get(
                        "injection_detected",
                        False
                    )
                )
            )

        # Supports InspectionResult objects.

        if getattr(
            validation,
            "secret_detected",
            False
        ):
            return False

        if getattr(
            validation,
            "pii_detected",
            False
        ):
            return False

        if getattr(
            validation,
            "injection_detected",
            False
        ):
            return False

        return True

    @staticmethod
    def _validation_details(
        validation
    ):

        if isinstance(
            validation,
            dict
        ):

            return validation

        return {
            "valid": not (
                getattr(
                    validation,
                    "secret_detected",
                    False
                )
                or getattr(
                    validation,
                    "pii_detected",
                    False
                )
                or getattr(
                    validation,
                    "injection_detected",
                    False
                )
            ),

            "secret_detected": getattr(
                validation,
                "secret_detected",
                False
            ),

            "pii_detected": getattr(
                validation,
                "pii_detected",
                False
            ),

            "injection_detected": getattr(
                validation,
                "injection_detected",
                False
            ),

            "jailbreak_detected": getattr(
                validation,
                "jailbreak_detected",
                False
            ),

            "severity": getattr(
                validation,
                "severity",
                0
            ),

            "reasons": getattr(
                validation,
                "reasons",
                []
            ),

            "indicators": getattr(
                validation,
                "indicators",
                []
            )
        }

    # ==================================================
    # PATH SECURITY
    # ==================================================

    def _safe_path(
        self,
        resource
    ):

        if not resource:
            return None

        requested = Path(resource)

        # ----------------------------------------------
        # Absolute path protection
        # ----------------------------------------------

        if requested.is_absolute():
            return None

        # ----------------------------------------------
        # Path traversal protection
        # ----------------------------------------------

        if ".." in requested.parts:
            return None

        safe_path = (
            self.sandbox_dir / requested
        )

        resolved = safe_path.resolve()

        # ----------------------------------------------
        # Final sandbox boundary check
        # ----------------------------------------------

        try:

            resolved.relative_to(
                self.sandbox_dir.resolve()
            )

        except ValueError:

            return None

        return resolved

    # ==================================================
    # READ FILE
    # ==================================================

    def _read_file(
        self,
        action_request
    ):

        path = self._safe_path(
            action_request.resource
        )

        if path is None:

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": "Unsafe file path."
            }

        if not path.exists():

            return {
                "executed": False,
                "status": "FAILED",
                "reason": "File does not exist."
            }

        if not path.is_file():

            return {
                "executed": False,
                "status": "FAILED",
                "reason": "Resource is not a file."
            }

        try:

            content = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            return {
                "executed": False,
                "status": "FAILED",
                "reason": (
                    "File is not valid UTF-8 text."
                )
            }

        return {
            "executed": True,
            "status": "SUCCESS",
            "tool": "read_file",
            "resource": action_request.resource,
            "result": content
        }

    # ==================================================
    # WRITE FILE
    # ==================================================

    def _write_file(
        self,
        action_request
    ):

        path = self._safe_path(
            action_request.resource
        )

        if path is None:

            return {
                "executed": False,
                "status": "BLOCKED",
                "reason": "Unsafe file path."
            }

        content = (
            action_request.parameters.get(
                "content"
            )
        )

        if content is None:

            return {
                "executed": False,
                "status": "FAILED",
                "reason": "Missing file content."
            }

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        try:

            path.write_text(
                str(content),
                encoding="utf-8"
            )

        except OSError as exc:

            return {
                "executed": False,
                "status": "FAILED",
                "reason": (
                    f"File write failed: {exc}"
                )
            }

        return {
            "executed": True,
            "status": "SUCCESS",
            "tool": "write_file",
            "resource": action_request.resource
        }