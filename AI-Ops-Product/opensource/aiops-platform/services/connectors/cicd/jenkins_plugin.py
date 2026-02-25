"""Jenkins CI/CD plugin — fetches build/deploy data from Jenkins REST API."""

import uuid
from datetime import datetime
from typing import Any

from services.connectors.base import PluginManifest
from services.connectors.cicd.base_plugin import CICDPlugin


class JenkinsPlugin(CICDPlugin):
    """Connects to Jenkins via its REST API.

    Config keys: base_url, api_token, username, jobs
    """

    @property
    def source_system(self) -> str:
        return "jenkins"

    def manifest(self) -> PluginManifest:
        return PluginManifest(
            name="jenkins",
            version="1.0.0",
            plugin_type="connector",
            capabilities=["changes"],
            required_secrets=["api_token"],
        )

    def _fetch_raw_changes(self, since: datetime) -> list[dict[str, Any]]:
        # TODO: GET {base_url}/job/{job_name}/api/json?tree=builds[...]
        return []

    def normalize_change(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        return {
            "change_id": f"chg-jenkins-{raw_event.get('number', uuid.uuid4().hex[:8])}",
            "source_system": "jenkins",
            "source_change_id": str(raw_event.get("id", "")),
            "service_canonical_id": raw_event.get("service_canonical_id", ""),
            "environment": raw_event.get("environment", "production"),
            "version": raw_event.get("displayName", ""),
            "timestamp_start": raw_event.get("timestamp_start", ""),
            "timestamp_end": raw_event.get("timestamp_end", ""),
            "actor": raw_event.get("user", "jenkins"),
            "pipeline": raw_event.get("fullDisplayName", ""),
            "status": self._map_status(raw_event.get("result", "")),
            "commit_sha": raw_event.get("lastBuiltRevision", {}).get("SHA1", ""),
            "metadata": {
                "jenkins_job": raw_event.get("fullDisplayName", ""),
                "build_number": raw_event.get("number"),
                "duration_ms": raw_event.get("duration"),
            },
        }

    def health_check(self) -> dict[str, Any]:
        return {"healthy": False, "message": "Not connected (stub)"}

    @staticmethod
    def _map_status(jenkins_result: str) -> str:
        return {"SUCCESS": "succeeded", "FAILURE": "failed", "ABORTED": "rolled_back",
                "UNSTABLE": "failed", "": "started"}.get(jenkins_result, "started")
