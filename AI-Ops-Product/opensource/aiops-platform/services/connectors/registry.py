"""Unified Plugin Registry — manages all Tier 1 and Tier 2 plugins."""

import importlib
import logging
from typing import Any

from services.connectors.base import ConnectorPlugin, ProcessorPlugin

logger = logging.getLogger(__name__)

# Built-in connector class paths
BUILTIN_CONNECTORS: dict[str, str] = {
    "dynatrace": "services.connectors.dynatrace.connector:DynatraceConnector",
    "solarwinds": "services.connectors.solarwinds.connector:SolarWindsConnector",
    "splunk": "services.connectors.splunk.connector:SplunkConnector",
    "opensearch": "services.connectors.opensearch.connector:OpenSearchConnector",
    "influxdb": "services.connectors.influxdb.connector:InfluxDBConnector",
    "jira": "services.connectors.jira.connector:JiraConnector",
    "confluence": "services.connectors.confluence.connector:ConfluenceConnector",
    "jenkins": "services.connectors.cicd.jenkins_plugin:JenkinsPlugin",
    "gitlab_ci": "services.connectors.cicd.gitlab_ci_plugin:GitLabCIPlugin",
    "github_actions": "services.connectors.cicd.github_actions_plugin:GitHubActionsPlugin",
    "argocd": "services.connectors.cicd.argocd_plugin:ArgoCDPlugin",
    "azure_devops": "services.connectors.cicd.azure_devops_plugin:AzureDevOpsPlugin",
}

BUILTIN_PROCESSORS: dict[str, str] = {
    "blast_radius": "services.processors.blast_radius:BlastRadiusProcessor",
    "noise_reducer": "services.processors.noise_reducer:NoiseReducerProcessor",
    "change_scorer": "services.processors.change_scorer:ChangeScorerProcessor",
}


class PluginRegistry:
    """Manages plugin lifecycle: registration, loading, and access."""

    def __init__(self) -> None:
        self._connectors: dict[str, ConnectorPlugin] = {}
        self._processors: dict[str, ProcessorPlugin] = {}

    def load_from_config(self, config: dict[str, dict[str, Any]]) -> None:
        """Load plugins from config. Each key is a plugin name."""
        for name, plugin_conf in config.items():
            if not plugin_conf.get("enabled", True):
                logger.info("Skipping disabled plugin: %s", name)
                continue

            class_path = plugin_conf.get("class")
            if not class_path:
                class_path = BUILTIN_CONNECTORS.get(name) or BUILTIN_PROCESSORS.get(name)
            if not class_path:
                logger.warning("Unknown plugin '%s' and no class path provided", name)
                continue

            try:
                cls = self._import_class(class_path)
                instance = cls(plugin_conf)
                if isinstance(instance, ProcessorPlugin):
                    self._processors[name] = instance
                elif isinstance(instance, ConnectorPlugin):
                    self._connectors[name] = instance
                logger.info("Loaded plugin: %s (%s)", name, class_path)
            except Exception:
                logger.exception("Failed to load plugin: %s", name)

    def register_connector(self, name: str, plugin: ConnectorPlugin) -> None:
        self._connectors[name] = plugin

    def register_processor(self, name: str, plugin: ProcessorPlugin) -> None:
        self._processors[name] = plugin

    def get_connector(self, name: str) -> ConnectorPlugin | None:
        return self._connectors.get(name)

    def get_processor(self, name: str) -> ProcessorPlugin | None:
        return self._processors.get(name)

    def get_all_connectors(self) -> dict[str, ConnectorPlugin]:
        return {k: v for k, v in self._connectors.items() if v.enabled}

    def get_all_processors(self) -> dict[str, ProcessorPlugin]:
        return dict(self._processors)

    def health_check_all(self) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for name, p in self._connectors.items():
            results[name] = p.health_check()
        for name, p in self._processors.items():
            results[name] = p.health_check()
        return results

    def manifests(self) -> list[dict[str, Any]]:
        return (
            [p.manifest().to_dict() for p in self._connectors.values()]
            + [p.manifest().to_dict() for p in self._processors.values()]
        )

    @staticmethod
    def _import_class(class_path: str) -> type:
        module_path, class_name = class_path.rsplit(":", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    @property
    def connector_count(self) -> int:
        return len(self._connectors)

    @property
    def processor_count(self) -> int:
        return len(self._processors)

    @property
    def plugin_count(self) -> int:
        return self.connector_count + self.processor_count
