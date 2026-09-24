class BinaryMetrics:
    """
    Binary classification metrics for adversarial
    security evaluation.

    expected:
        Ground-truth malicious/benign labels.

    predicted:
        Model/governance predicted malicious/benign labels.
    """

    @staticmethod
    def calculate(
        expected,
        predicted=None
    ):
        """
        Calculate binary classification metrics.

        Supports:

            BinaryMetrics.calculate(
                expected,
                predicted
            )

        where both are lists of booleans.

        Also supports:

            BinaryMetrics.calculate(results)

        where results contain:
            expected_malicious
            predicted_malicious
        """

        # ==================================================
        # SUPPORT RESULT-DICTIONARY FORMAT
        # ==================================================

        if predicted is None:

            results = expected

            expected = [
                result["expected_malicious"]
                for result in results
            ]

            predicted = [
                result["predicted_malicious"]
                for result in results
            ]

        # ==================================================
        # VALIDATE INPUT
        # ==================================================

        if len(expected) != len(predicted):

            raise ValueError(
                "Expected and predicted "
                "must have the same length."
            )

        total = len(expected)

        # ==================================================
        # EMPTY DATASET
        # ==================================================

        if total == 0:

            return {
                "total": 0,

                "true_positive": 0,
                "true_negative": 0,
                "false_positive": 0,
                "false_negative": 0,

                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,

                "f1": 0.0,
                "f1_score": 0.0,

                "attack_detection_rate": 0.0,
                "false_positive_rate": 0.0,
            }

        # ==================================================
        # CONFUSION MATRIX
        # ==================================================

        true_positive = 0
        true_negative = 0
        false_positive = 0
        false_negative = 0

        for actual, prediction in zip(
            expected,
            predicted
        ):

            actual = bool(actual)
            prediction = bool(prediction)

            # ----------------------------------------------
            # True Positive
            # Actual attack + predicted attack
            # ----------------------------------------------

            if actual and prediction:

                true_positive += 1

            # ----------------------------------------------
            # True Negative
            # Actual benign + predicted benign
            # ----------------------------------------------

            elif not actual and not prediction:

                true_negative += 1

            # ----------------------------------------------
            # False Positive
            # Actual benign + predicted attack
            # ----------------------------------------------

            elif not actual and prediction:

                false_positive += 1

            # ----------------------------------------------
            # False Negative
            # Actual attack + predicted benign
            # ----------------------------------------------

            elif actual and not prediction:

                false_negative += 1

        # ==================================================
        # ACCURACY
        # ==================================================

        accuracy = (
            (
                true_positive
                + true_negative
            )
            / total
        )

        # ==================================================
        # PRECISION
        # ==================================================

        precision_denominator = (
            true_positive
            + false_positive
        )

        precision = (
            true_positive
            / precision_denominator
            if precision_denominator
            else 0.0
        )

        # ==================================================
        # RECALL
        # ==================================================

        recall_denominator = (
            true_positive
            + false_negative
        )

        recall = (
            true_positive
            / recall_denominator
            if recall_denominator
            else 0.0
        )

        # ==================================================
        # F1 SCORE
        # ==================================================

        f1_denominator = (
            precision
            + recall
        )

        f1_score = (
            (
                2
                * precision
                * recall
            )
            / f1_denominator
            if f1_denominator
            else 0.0
        )

        # ==================================================
        # ATTACK DETECTION RATE
        #
        # For malicious/attack classification,
        # this is equivalent to recall.
        # ==================================================

        attack_detection_rate = recall

        # ==================================================
        # FALSE POSITIVE RATE
        # ==================================================

        fpr_denominator = (
            true_negative
            + false_positive
        )

        false_positive_rate = (
            false_positive
            / fpr_denominator
            if fpr_denominator
            else 0.0
        )

        # ==================================================
        # FINAL METRICS
        # ==================================================

        rounded_f1 = round(
            f1_score,
            4
        )

        return {

            # ----------------------------------------------
            # Dataset
            # ----------------------------------------------

            "total": total,

            # ----------------------------------------------
            # Confusion matrix
            # ----------------------------------------------

            "true_positive": (
                true_positive
            ),

            "true_negative": (
                true_negative
            ),

            "false_positive": (
                false_positive
            ),

            "false_negative": (
                false_negative
            ),

            # ----------------------------------------------
            # Standard classification metrics
            # ----------------------------------------------

            "accuracy": round(
                accuracy,
                4
            ),

            "precision": round(
                precision,
                4
            ),

            "recall": round(
                recall,
                4
            ),

            # ----------------------------------------------
            # F1
            #
            # Both names are intentionally provided.
            # Existing tests use "f1".
            # Newer code can use "f1_score".
            # ----------------------------------------------

            "f1": rounded_f1,

            "f1_score": rounded_f1,

            # ----------------------------------------------
            # Security-specific metrics
            # ----------------------------------------------

            "attack_detection_rate": round(
                attack_detection_rate,
                4
            ),

            "false_positive_rate": round(
                false_positive_rate,
                4
            ),
        }


# ======================================================
# BACKWARD COMPATIBILITY
# ======================================================

SecurityMetrics = BinaryMetrics