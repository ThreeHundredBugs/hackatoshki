from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from github import Github, GithubException
from github.Commit import Commit
from github.Organization import Organization
from github.Repository import Repository

from core.config import settings
from handlers.github_changes_handler import GitHubChangesHandler
from models.events import Alert, OpsgenieEvent, Source


class MockCommitList(list):
    """Mock list with totalCount attribute."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.totalCount = len(self)


@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock settings for testing."""
    monkeypatch.setattr(settings, "github_token", "test-token")


@pytest.fixture
def handler(mock_settings: None) -> GitHubChangesHandler:
    """GitHubChangesHandler instance for testing."""
    return GitHubChangesHandler()


@pytest.fixture
def sample_event() -> OpsgenieEvent:
    """Sample Opsgenie event with health check alert."""
    return OpsgenieEvent(
        action="Create",
        integrationId="test-integration",
        integrationName="Test Integration",
        source=Source(name="Test Source", type="API"),
        alert=Alert(
            alertId="test-alert-id",
            message="Test Alert",
            tags=["test"],
            tinyId="1234",
            alias="test-alias",
            createdAt=int(datetime.now().timestamp()),
            updatedAt=int(datetime.now().timestamp()),
            username="test-user",
            userId="test-user-id",
            entity="test-entity",
            description="""Alerts Firing:
- Message: URL https://report.improvado.io/-/health/report-loader-db/, already crashed for 10m

Labels:
- alertname = HealthCheckIsNot200
- group = production
- host = report.improvado.io
- k8s_cluster_name = lisbon""",
        ),
    )


@pytest.mark.asyncio
async def test_handle_success(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test successful handling of an event with recent changes."""
    # Mock GitHub client
    with patch("services.github.service.Github") as mock_github:
        # Mock organization
        mock_org = MagicMock(spec=Organization)
        mock_github.return_value.get_organization.return_value = mock_org

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_org.get_repo.return_value = mock_repo

        # Mock commit
        mock_commit = MagicMock(spec=Commit)
        mock_commit.commit.message = "Test commit"
        mock_commit.html_url = "https://github.com/improvado/report-loader-db/commit/abc123"
        mock_repo.get_commits.return_value = MockCommitList([mock_commit])

        result = await handler.handle(sample_event)

    assert result["status"] == "processed"
    assert result["handler"] == "github_changes"
    assert result["alert_info"]["service"] == "report-loader-db"
    assert result["alert_info"]["environment"] == "production"
    assert result["github_changes"]["status"] == "success"
    assert result["github_changes"]["last_commit"] == "Test commit"


@pytest.mark.asyncio
async def test_handle_no_changes(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handling of an event with no recent changes."""
    # Mock GitHub client
    with patch("services.github.service.Github") as mock_github:
        # Mock organization
        mock_org = MagicMock(spec=Organization)
        mock_github.return_value.get_organization.return_value = mock_org

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_org.get_repo.return_value = mock_repo

        # Mock empty commits list
        mock_repo.get_commits.return_value = MockCommitList([])

        result = await handler.handle(sample_event)

    assert result["status"] == "processed"
    assert result["github_changes"]["status"] == "success"
    assert result["github_changes"]["message"] == "No commits found in the last 24 hours"
    assert result["github_changes"]["last_commit"] is None


@pytest.mark.asyncio
async def test_handle_repo_not_found(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handling of a non-existent repository."""
    # Mock GitHub client
    with patch("services.github.service.Github") as mock_github:
        # Mock organization
        mock_org = MagicMock(spec=Organization)
        mock_github.return_value.get_organization.return_value = mock_org

        # Mock repository not found
        mock_org.get_repo.side_effect = GithubException(404, {"message": "Not Found"})

        result = await handler.handle(sample_event)

    assert result["status"] == "processed"
    assert result["github_changes"]["status"] == "error"
    assert "Repository report-loader-db not found" in result["github_changes"]["message"]


@pytest.mark.asyncio
async def test_handle_invalid_description(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handling of event with invalid description format."""
    # Modify event to have invalid description
    sample_event.alert.description = "Invalid description without URL"

    result = await handler.handle(sample_event)

    assert result["status"] == "error"
    assert "Could not find URL in description" in result["error"]


@pytest.mark.asyncio
async def test_handle_github_api_error(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handling of GitHub API errors."""
    # Mock GitHub client
    with patch("services.github.service.Github") as mock_github:
        # Mock organization
        mock_org = MagicMock(spec=Organization)
        mock_github.return_value.get_organization.return_value = mock_org

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_org.get_repo.return_value = mock_repo

        # Mock API error
        mock_repo.get_commits.side_effect = GithubException(500, {"message": "Internal Server Error"})

        result = await handler.handle(sample_event)

    assert result["status"] == "processed"
    assert result["github_changes"]["status"] == "error"
    assert "Error checking changes" in result["github_changes"]["message"]


@pytest.mark.asyncio
async def test_handle_rate_limit(
    handler: GitHubChangesHandler,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handling of GitHub API rate limit."""
    # Mock GitHub client
    with patch("services.github.service.Github") as mock_github:
        # Mock organization
        mock_org = MagicMock(spec=Organization)
        mock_github.return_value.get_organization.return_value = mock_org

        # Mock repository
        mock_repo = MagicMock(spec=Repository)
        mock_org.get_repo.return_value = mock_repo

        # Mock rate limit error
        mock_repo.get_commits.side_effect = GithubException(
            403,
            {
                "message": "API rate limit exceeded",
                "documentation_url": "https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting",
            },
        )

        result = await handler.handle(sample_event)

    assert result["status"] == "processed"
    assert result["github_changes"]["status"] == "error"
    assert "API rate limit exceeded" in result["github_changes"]["message"]


@pytest.mark.asyncio
async def test_handler_initialization_without_token(
    monkeypatch: pytest.MonkeyPatch,
    sample_event: OpsgenieEvent,
) -> None:
    """Test handler initialization without GitHub token."""
    # Remove GitHub token from settings
    monkeypatch.setattr(settings, "github_token", None)
    
    # Create handler without token
    handler = GitHubChangesHandler()
    
    # Verify that handler is created but service is not initialized
    assert handler.github_service is None
    
    # Verify that trying to handle an event raises an error
    result = await handler.handle(sample_event)
    assert result["status"] == "error"
    assert "GitHub token is not configured" in result["error"] 