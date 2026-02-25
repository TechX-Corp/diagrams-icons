"""GitHub Actions plugin — fetches workflow run data from GitHub API."""

import uuid
from datetime import datetime
from typing import Any

from services.connectors.base import PluginManifest
from services.connectors.cicd.base_plugin import CICDPlugin


class GitHubActionsPlugin(CICDPlugin):
    """Config keys: token, repos, workflow_names"""

    @property
    def source_system(self) -> str:
        return "github_actions"

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="github_actions", version="1.0.0", plugin_type="connector",
            capabilities=["changes"], required_secrets=["token"],
        )

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        return []

    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "change_id": f"chg-ghactions-{raw_event.get('id', uuid.uuid4().hex[:8])}",
            "source_system": "github_actions",
            "source_change_id": str(raw_event.get("id", "")),
            "service_canonical_id": raw_event.get("service_canonical_id", ""),
            "environment": raw_event.get("environment", "production"),
            "version": raw_event.get("head_sha", "")[:12],
            "timestamp_start": raw_event.get("created_at", ""),
            "timestamp_end": raw_event.get("updated_at", ""),
            "actor": raw_event.get("actor", {}).get("login", ""),
            "pipeline": raw_event.get("name", ""),
            "status": {"success": "succeeded", "failure": "failed", "cancelled": "rolled_back",
                       "": "started", None: "started"}.get(raw_event.get("conclusion", ""), "started"),
            "commit_sha": raw_event.get("head_sha", ""),
            "metadata": {"run_id": raw_event.get("id"), "repo": raw_event.get("repository", {}).get("full_name")},
        }

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
