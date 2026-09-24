from security.output_validator import OutputValidator


def test_safe_output():

    validator = OutputValidator()

    result = validator.validate(
        "Binary search works on a sorted collection."
    )

    assert result.pii_detected is False
    assert result.secret_detected is False
    assert result.injection_detected is False


def test_output_email_detection():

    validator = OutputValidator()

    result = validator.validate(
        "The customer email is customer@example.com"
    )

    assert result.pii_detected is True
    assert "email" in result.detected_pii


def test_output_phone_detection():

    validator = OutputValidator()

    result = validator.validate(
        "Customer phone: 9876543210"
    )

    assert result.pii_detected is True
    assert "phone" in result.detected_pii


def test_output_secret_detection():

    validator = OutputValidator()

    result = validator.validate(
        "api_key=abcdefghijklmnopqrstuvwxyz123456"
    )

    assert result.secret_detected is True
    assert "SECRET_EXPOSURE" in result.indicators


def test_output_password_detection():

    validator = OutputValidator()

    result = validator.validate(
        "password=SuperSecret123!"
    )

    assert result.secret_detected is True
    assert result.pii_detected is True


def test_output_multiple_sensitive_items():

    validator = OutputValidator()

    result = validator.validate(
        "Email: customer@example.com "
        "Phone: 9876543210 "
        "password=SuperSecret123!"
    )

    assert result.pii_detected is True
    assert result.secret_detected is True

    assert "email" in result.detected_pii
    assert "phone" in result.detected_pii