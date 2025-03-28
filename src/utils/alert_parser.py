import re
from typing import Optional
from urllib.parse import urlparse

import structlog

logger = structlog.get_logger()


service_name_to_repo_map = {
    'report-laoder-db': 'rtbmedia'
}

class AlertInfo:
    """Structured information extracted from alert."""
    
    def __init__(
        self,
        service_name: str,
        environment: str,
        domain: str,
        health_endpoint: str,
        cluster: str,
    ) -> None:
        self.service_name = service_name
        self.environment = environment
        self.domain = domain
        self.health_endpoint = health_endpoint
        self.cluster = cluster

    def __str__(self) -> str:
        return (
            f"AlertInfo(service={self.service_name}, "
            f"env={self.environment}, "
            f"domain={self.domain}, "
            f"health_endpoint={self.health_endpoint}, "
            f"cluster={self.cluster})"
        )


def extract_service_from_url(url: str) -> Optional[str]:
    """Extract service name from health check URL.
    
    Args:
        url: Health check URL
        
    Returns:
        Service name if found, None otherwise
    """
    # Remove trailing slash if exists
    url = url.rstrip('/')
    
    # Extract path from URL
    path = urlparse(url).path
    
    # Look for health check patterns
    patterns = [
        r'/-/health/([^/]+)/?$',  # Matches /-/health/service-name/
        r'/health/([^/]+)/?$',    # Matches /health/service-name/
        r'/_health/([^/]+)/?$',   # Matches /_health/service-name/
    ]
    
    for pattern in patterns:
        if match := re.search(pattern, path):
            return match.group(1)
    
    return None


def parse_alert_info(description: str, labels: dict[str, str]) -> AlertInfo:
    """Parse alert information from description and labels.
    
    Args:
        description: Alert description
        labels: Alert labels
        
    Returns:
        AlertInfo object with extracted information
        
    Raises:
        ValueError: If required information cannot be extracted
    """
    # Extract URL from description
    url_match = re.search(r'URL (https?://[^\s,]+)', description)
    if not url_match:
        raise ValueError("Could not find URL in description")
    
    url = url_match.group(1)
    service_name = extract_service_from_url(url)

    if not service_name:
        raise ValueError(f"Could not extract service name from URL: {url}")
    
    service_name = service_name_to_repo_map.get(service_name, service_name)
    
    # Extract other information from labels
    environment = labels.get('group', 'unknown')
    domain = labels.get('host', 'unknown')
    cluster = labels.get('k8s_cluster_name', 'unknown')
    
    return AlertInfo(
        service_name=service_name,
        environment=environment,
        domain=domain,
        health_endpoint=url,
        cluster=cluster,
    ) 