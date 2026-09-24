from evaluation.evaluator import SecurityEvaluator
from evaluation.metrics import BinaryMetrics
from evaluation.adversarial_scenarios import (
    ADVERSARIAL_SCENARIOS
)


def main():

    print("=" * 60)
    print("UNIFIED AI GOVERNANCE")
    print("SECURITY EVALUATION")
    print("=" * 60)

    # ----------------------------------------------
    # Create evaluator
    # ----------------------------------------------

    evaluator = SecurityEvaluator()

    # ----------------------------------------------
    # Evaluate adversarial scenarios
    # ----------------------------------------------

    print("\nRunning adversarial evaluation...\n")

    results = evaluator.evaluate_adversarial(
        ADVERSARIAL_SCENARIOS
    )

    # ----------------------------------------------
    # Extract labels
    # ----------------------------------------------

    expected = [
        result["expected_malicious"]
        for result in results
    ]

    predicted = [
        result["predicted_malicious"]
        for result in results
    ]

    # ----------------------------------------------
    # Calculate metrics
    # ----------------------------------------------

    metrics = BinaryMetrics.calculate(
        expected,
        predicted
    )

    # ----------------------------------------------
    # Print scenario results
    # ----------------------------------------------

    print("-" * 60)
    print("SCENARIO RESULTS")
    print("-" * 60)

    for result in results:

        status = (
            "PASS"
            if result["correct"]
            else "FAIL"
        )

        print(
            f'{result["scenario_id"]:20} '
            f'{status:5} '
            f'Expected={result["expected_malicious"]!s:5} '
            f'Predicted={result["predicted_malicious"]!s:5} '
            f'Risk={result["risk_score"]}'
        )

    # ----------------------------------------------
    # Print metrics
    # ----------------------------------------------

    print("\n" + "=" * 60)
    print("SECURITY METRICS")
    print("=" * 60)

    print(
        f'Total Scenarios        : '
        f'{metrics["total"]}'
    )

    print(
        f'True Positives         : '
        f'{metrics["true_positive"]}'
    )

    print(
        f'True Negatives         : '
        f'{metrics["true_negative"]}'
    )

    print(
        f'False Positives        : '
        f'{metrics["false_positive"]}'
    )

    print(
        f'False Negatives        : '
        f'{metrics["false_negative"]}'
    )

    print(
        f'Accuracy               : '
        f'{metrics["accuracy"]:.4f}'
    )

    print(
        f'Precision              : '
        f'{metrics["precision"]:.4f}'
    )

    print(
        f'Recall                 : '
        f'{metrics["recall"]:.4f}'
    )

    print(
        f'F1 Score               : '
        f'{metrics["f1"]:.4f}'
    )

    print(
        f'Attack Detection Rate : '
        f'{metrics["attack_detection_rate"]:.4f}'
    )

    print(
        f'False Positive Rate    : '
        f'{metrics["false_positive_rate"]:.4f}'
    )

    print("=" * 60)

    # ----------------------------------------------
    # Final status
    # ----------------------------------------------

    if metrics["false_negative"] == 0:

        print(
            "\nSECURITY STATUS: STRONG"
        )

    else:

        print(
            "\nSECURITY STATUS: REVIEW REQUIRED"
        )


if __name__ == "__main__":
    main()