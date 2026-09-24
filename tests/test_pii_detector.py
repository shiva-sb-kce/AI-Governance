from security.pii_detector import PIIDetector


def test_email_detection():
    detector = PIIDetector()

    result = detector.detect(
        "Contact me at student@example.com"
    )

    assert result["detected"] is True
    assert "email" in result["types"]


def test_phone_detection():
    detector = PIIDetector()

    result = detector.detect(
        "My phone number is 9876543210"
    )

    assert result["detected"] is True
    assert "phone" in result["types"]


def test_aadhaar_detection():
    detector = PIIDetector()

    result = detector.detect(
        "Aadhaar: 2345 6789 0123"
    )

    assert result["detected"] is True
    assert "aadhaar" in result["types"]


def test_credit_card_detection():
    detector = PIIDetector()

    result = detector.detect(
        "Card: 4111 1111 1111 1111"
    )

    assert result["detected"] is True
    assert "credit_card" in result["types"]


def test_api_key_detection():
    detector = PIIDetector()

    result = detector.detect(
        "api_key=abcdefghijklmnopqrstuvwxyz123456"
    )

    assert result["detected"] is True
    assert "api_key" in result["types"]


def test_password_detection():
    detector = PIIDetector()

    result = detector.detect(
        "password=SuperSecret123!"
    )

    assert result["detected"] is True
    assert "password" in result["types"]


def test_secret_detection():
    detector = PIIDetector()

    result = detector.detect(
        "private_key=ABCDEF1234567890"
    )

    assert result["detected"] is True
    assert "secret" in result["types"]


def test_safe_text():
    detector = PIIDetector()

    result = detector.detect(
        "Explain the difference between Python lists and tuples."
    )

    assert result["detected"] is False
    assert result["types"] == []