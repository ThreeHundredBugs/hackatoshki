from typing import Any

import pytest

from alert_parser import AlertInfo, extract_service_from_url, parse_alert_info


# Test data constants
URL_VARIATIONS = [
    (
        "https://report.improvado.io/-/health/report-loader-db/",
        "report-loader-db",
    ),
    (
        "https://api.example.com/health/auth-service/",
        "auth-service",
    ),
    (
        "https://dashboard.test.com/_health/metrics-collector",
        "metrics-collector",
    ),
]


@pytest.fixture
def sample_description() -> str:
    """Sample alert description with labels."""
    return """Alerts Firing:

- Message: URL https://report.improvado.io/-/health/report-loader-db/, already crashed for 10m

Labels:
- alertname = HealthCheckIsNot200
- __replica__ = replica-0
- cluster = mimir/grafana-agent
- destinations = opsgenie
- doc = https://www.notion.so/improvado-home/Health-Check-Devs-ae872f0f8fd448ad98879f86efd81b57
- grafana = https://grafana.ops.improvado.io/d/000000010/health-checks-dashboard
- group = production
- host = report.improvado.io
- instance = https://report.improvado.io/-/health/report-loader-db/
- job = blackbox
- k8s_cluster_name = lisbon
- priority = P1
- service = all
- tags = lisbon,production,report.improvado.io
- team = devops-team"""


@pytest.fixture
def sample_labels() -> dict[str, str]:
    """Sample alert labels."""
    return {
        "alertname": "HealthCheckIsNot200",
        "__replica__": "replica-0",
        "cluster": "mimir/grafana-agent",
        "group": "production",
        "host": "report.improvado.io",
        "k8s_cluster_name": "lisbon",
        "priority": "P1",
        "service": "all",
    }


@pytest.fixture
def alert_info() -> AlertInfo:
    """Sample AlertInfo object."""
    return AlertInfo(
        service_name="test-service",
        environment="production",
        domain="test.com",
        health_endpoint="https://test.com/health",
        cluster="test-cluster",
    )


def test_alert_info_creation(alert_info: AlertInfo) -> None:
    """Test AlertInfo object creation."""
    assert alert_info.service_name == "test-service"
    assert alert_info.environment == "production"
    assert alert_info.domain == "test.com"
    assert alert_info.health_endpoint == "https://test.com/health"
    assert alert_info.cluster == "test-cluster"


def test_alert_info_str(alert_info: AlertInfo) -> None:
    """Test AlertInfo string representation."""
    expected = (
        "AlertInfo(service=test-service, "
        "env=production, "
        "domain=test.com, "
        "health_endpoint=https://test.com/health, "
        "cluster=test-cluster)"
    )
    assert str(alert_info) == expected


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "https://report.improvado.io/-/health/report-loader-db/",
            "report-loader-db",
        ),
        (
            "https://api.example.com/health/auth-service",
            "auth-service",
        ),
        (
            "https://dashboard.test.com/_health/metrics-collector/",
            "metrics-collector",
        ),
        # Test URLs without service name
        ("https://example.com/health", None),
        ("https://example.com/", None),
        # Test invalid URLs
        ("not-a-url", None),
        ("", None),
    ],
)
def test_extract_service_from_url(url: str, expected: Any) -> None:
    """Test service name extraction from various URL formats."""
    assert extract_service_from_url(url) == expected


def test_extract_service_handles_none() -> None:
    """Test that None input is handled gracefully."""
    with pytest.raises(AttributeError):
        extract_service_from_url(None)  # type: ignore


def test_parse_alert_info_success(
    sample_description: str, sample_labels: dict[str, str]
) -> None:
    """Test successful parsing of alert information."""
    info = parse_alert_info(sample_description, sample_labels)

    assert info.service_name == "report-loader-db"
    assert info.environment == "production"
    assert info.domain == "report.improvado.io"
    assert (
        info.health_endpoint
        == "https://report.improvado.io/-/health/report-loader-db/"
    )
    assert info.cluster == "lisbon"


def test_parse_alert_info_missing_url(sample_labels: dict[str, str]) -> None:
    """Test handling of description without URL."""
    description = "Alert without URL"
    with pytest.raises(ValueError, match="Could not find URL in description"):
        parse_alert_info(description, sample_labels)


def test_parse_alert_info_invalid_url(sample_labels: dict[str, str]) -> None:
    """Test handling of invalid URL in description."""
    description = "URL https://example.com/no-service-name"
    with pytest.raises(
        ValueError, match="Could not extract service name from URL:"
    ):
        parse_alert_info(description, sample_labels)


@pytest.fixture
def empty_labels() -> dict[str, str]:
    """Empty labels dictionary."""
    return {}


def test_parse_alert_info_missing_labels(empty_labels: dict[str, str]) -> None:
    """Test handling of missing labels."""
    description = "URL https://example.com/-/health/test-service/"
    info = parse_alert_info(description, empty_labels)

    assert info.service_name == "test-service"
    assert info.environment == "unknown"
    assert info.domain == "unknown"
    assert info.health_endpoint == "https://example.com/-/health/test-service/"
    assert info.cluster == "unknown"


@pytest.mark.parametrize("url,service", URL_VARIATIONS)
def test_url_format_variations(url: str, service: str) -> None:
    """Test different URL format variations."""
    assert extract_service_from_url(url) == service 