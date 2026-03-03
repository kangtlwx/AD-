from app.main import is_request_authorized


def test_is_request_authorized_requires_configured_secret() -> None:
    assert not is_request_authorized({"X-Webhook-Secret": "demo"}, "")


def test_is_request_authorized_validates_header_value() -> None:
    headers = {"X-Webhook-Secret": "expected-secret"}
    assert is_request_authorized(headers, "expected-secret")
    assert not is_request_authorized(headers, "wrong-secret")
