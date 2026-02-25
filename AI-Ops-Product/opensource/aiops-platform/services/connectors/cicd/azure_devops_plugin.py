"""Azure DevOps plugin — fetches pipeline/release data from Azure DevOps API."""

import uuid
from datetime import datetime
from typing import Any

from services.connectors.base import PluginManifest
from services.connectors.cicd.base_plugin import CICDPlugin


class AzureDevOpsPlugin(CICDPlugin):
    """Config keys: organization, project, pat, pipeline_ids"""

    @property
    def source_system(self) -> str:
        return "azure_devops"

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="azure_devops", version="1.0.0", plugin_type="connector",
            capabilities=["changes"], required_secrets=["pat"],
        )

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        return []

    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "change_id": f"chg-azdo-{raw_event.get('id', uuid.uuid4().hex[:8])}",
            "source_system": "azure_devops",
            "source_change_id": str(raw_event.get("id", "")),
            "service_canonical_id": raw_event.get("service_canonical_id", ""),
            "environment": raw_event.get("environment", "production"),
            "version": raw_event.get("buildNumber", ""),
            "timestamp_start": raw_event.get("startTime", ""),
            "timestamp_end": raw_event.get("finishTime", ""),
            "actor": raw_event.get("requestedFor", {}).get("uniqueName", ""),
            "pipeline": raw_event.get("definition", {}).get("name", ""),
            "status": {"succeeded": "succeeded", "failed": "failed", "canceled": "rolled_back",
                       "": "started"}.get(raw_event.get("result", ""), "started"),
            "commit_sha": raw_event.get("sourceVersion", ""),
            "metadata": {"build_id": raw_event.get("id"), "source_branch": raw_event.get("sourceBranch")},
        }

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
