from evaluation.evaluator import SecurityEvaluator
from evaluation.metrics import BinaryMetrics
from evaluation.adversarial_scenarios import (
    ADVERSARIAL_SCENARIOS
)


class EvaluationReport:

    @staticmethod
    def generate():

        evaluator = SecurityEvaluator()

        results = evaluator.evaluate_adversarial(
            ADVERSARIAL_SCENARIOS
        )

        expected = [
            result["expected_malicious"]
            for result in results
        ]

        predicted = [
            result["predicted_malicious"]
            for result in results
        ]

        metrics = BinaryMetrics.calculate(
            expected,
            predicted
        )

        return {
            "total_scenarios": metrics["total"],

            "correct": (
                metrics["true_positive"]
                + metrics["true_negative"]
            ),

            "incorrect": (
                metrics["false_positive"]
                + metrics["false_negative"]
            ),

            "true_positive": (
                metrics["true_positive"]
            ),

            "true_negative": (
                metrics["true_negative"]
            ),

            "false_positive": (
                metrics["false_positive"]
            ),

            "false_negative": (
                metrics["false_negative"]
            ),

            "accuracy": metrics["accuracy"],

            "precision": metrics["precision"],

            "recall": metrics["recall"],

            "f1": metrics["f1"],

            "attack_detection_rate": (
                metrics["attack_detection_rate"]
            ),

            "false_positive_rate": (
                metrics["false_positive_rate"]
            ),

            "status": (
                "STRONG"
                if metrics["false_negative"] == 0
                else "REVIEW_REQUIRED"
            )
        }