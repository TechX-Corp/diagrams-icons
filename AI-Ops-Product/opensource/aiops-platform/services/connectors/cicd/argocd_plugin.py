"""ArgoCD plugin — fetches sync/deployment data from ArgoCD API."""

import uuid
from datetime import datetime
from typing import Any

from services.connectors.base import PluginManifest
from services.connectors.cicd.base_plugin import CICDPlugin


class ArgoCDPlugin(CICDPlugin):
    """Config keys: server_url, auth_token, applications"""

    @property
    def source_system(self) -> str:
        return "argocd"

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="argocd", version="1.0.0", plugin_type="connector",
            capabilities=["changes"], required_secrets=["auth_token"],
        )

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        return []

    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "change_id": f"chg-argocd-{raw_event.get('id', uuid.uuid4().hex[:8])}",
            "source_system": "argocd",
            "source_change_id": raw_event.get("id", ""),
            "service_canonical_id": raw_event.get("service_canonical_id", ""),
            "environment": raw_event.get("destination", {}).get("namespace", "production"),
            "version": raw_event.get("sync", {}).get("revision", "")[:12],
            "timestamp_start": raw_event.get("startedAt", ""),
            "timestamp_end": raw_event.get("finishedAt", ""),
            "actor": raw_event.get("initiatedBy", {}).get("username", "argocd-controller"),
            "pipeline": raw_event.get("appName", ""),
            "status": {"Succeeded": "succeeded", "Failed": "failed", "Running": "started",
                       "Terminating": "rolled_back"}.get(raw_event.get("phase", ""), "started"),
            "commit_sha": raw_event.get("sync", {}).get("revision", ""),
            "metadata": {"argocd_app": raw_event.get("appName"), "health_status": raw_event.get("health", {}).get("status")},
        }

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}
