"""GitLab CI plugin — fetches pipeline/deployment data from GitLab API."""

import uuid
from datetime import datetime
from typing import Any

from services.connectors.base import PluginManifest
from services.connectors.cicd.base_plugin import CICDPlugin


class GitLabCIPlugin(CICDPlugin):
    """Config keys: base_url, private_token, project_ids"""

    @property
    def source_system(self) -> str:
        return "gitlab_ci"

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="gitlab_ci", version="1.0.0", plugin_type="connector",
            capabilities=["changes"], required_secrets=["private_token"],
        )

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        return []

    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "change_id": f"chg-gitlab-{raw_event.get('id', uuid.uuid4().hex[:8])}",
            "source_system": "gitlab_ci",
            "source_change_id": str(raw_event.get("id", "")),
            "service_canonical_id": raw_event.get("service_canonical_id", ""),
            "environment": raw_event.get("environment", "production"),
            "version": raw_event.get("sha", "")[:12],
            "timestamp_start": raw_event.get("created_at", ""),
            "timestamp_end": raw_event.get("finished_at", ""),
            "actor": raw_event.get("user", {}).get("username", ""),
            "pipeline": raw_event.get("ref", ""),
            "status": {"success": "succeeded", "failed": "failed", "canceled": "rolled_back",
                       "running": "started"}.get(raw_event.get("status", ""), "started"),
            "commit_sha": raw_event.get("sha", ""),
            "metadata": {"pipeline_id": raw_event.get("id"), "project_id": raw_event.get("project_id")},
        }

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
