"""Tests for CI/CD plugin framework and unified registry."""

from datetime import datetime, timezone

from services.connectors.base import ConnectorPlugin, PluginManifest
from services.connectors.registry import PluginRegistry
from services.connectors.cicd.jenkins_plugin import JenkinsPlugin
from services.connectors.cicd.gitlab_ci_plugin import GitLabCIPlugin
from services.connectors.cicd.github_actions_plugin import GitHubActionsPlugin
from services.connectors.cicd.argocd_plugin import ArgoCDPlugin
from services.connectors.cicd.azure_devops_plugin import AzureDevOpsPlugin


def test_all_plugins_implement_interface():
    """All plugin stubs must be valid ConnectorPlugin subclasses."""
    plugins = [JenkinsPlugin, GitLabCIPlugin, GitHubActionsPlugin, ArgoCDPlugin, AzureDevOpsPlugin]
    for cls in plugins:
        plugin = cls({"enabled": True})
        assert isinstance(plugin, ConnectorPlugin)
        manifest = plugin.manifest()
        assert isinstance(manifest, PluginManifest)
        assert manifest.plugin_type == "connector"
        assert "changes" in manifest.capabilities


def test_plugin_source_systems_are_unique():
    plugins = [JenkinsPlugin({}), GitLabCIPlugin({}), GitHubActionsPlugin({}),
               ArgoCDPlugin({}), AzureDevOpsPlugin({})]
    systems = [p.source_system for p in plugins]
    assert len(systems) == len(set(systems))


def test_plugin_fetch_returns_list():
    plugin = JenkinsPlugin({"base_url": "http://localhost:8080"})
    result = plugin.fetch_changes(since=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert isinstance(result, list)


def test_plugin_normalize_produces_change_event():
    plugin = JenkinsPlugin({})
    raw = {
        "number": 100, "id": "build-100",
        "service_canonical_id": "ent:service:api-service",
        "environment": "production", "displayName": "2.14.0",
        "timestamp_start": "2026-02-25T11:15:00Z",
        "timestamp_end": "2026-02-25T11:22:00Z",
        "user": "deploy-bot", "fullDisplayName": "api-service/main #100",
        "result": "SUCCESS", "lastBuiltRevision": {"SHA1": "abc123"},
    }
    change = plugin.normalize_change(raw)
    assert change["source_system"] == "jenkins"
    assert change["status"] == "succeeded"
    assert "change_id" in change


def test_plugin_health_check():
    plugin = ArgoCDPlugin({"server_url": "http://localhost:8080"})
    result = plugin.health_check()
    assert "healthy" in result
    assert "message" in result


def test_plugin_manifest():
    plugin = JenkinsPlugin({})
    m = plugin.manifest()
    assert m.name == "jenkins"
    assert m.version == "1.0.0"
    assert "api_token" in m.required_secrets


def test_registry_load_connectors():
    registry = PluginRegistry()
    registry.load_from_config({
        "jenkins": {"enabled": True},
        "argocd": {"enabled": True},
        "gitlab_ci": {"enabled": False},
    })
    assert registry.connector_count == 2
    assert registry.get_connector("jenkins") is not None
    assert registry.get_connector("argocd") is not None
    assert registry.get_connector("gitlab_ci") is None


def test_registry_load_observability_connectors():
    registry = PluginRegistry()
    registry.load_from_config({
        "dynatrace": {"enabled": True},
        "solarwinds": {"enabled": True},
        "splunk": {"enabled": True},
    })
    assert registry.connector_count == 3
    dt = registry.get_connector("dynatrace")
    assert dt is not None
    assert "entities" in dt.manifest().capabilities


def test_registry_load_processors():
    registry = PluginRegistry()
    registry.load_from_config({
        "blast_radius": {"enabled": True},
        "noise_reducer": {"enabled": True},
    })
    assert registry.processor_count == 2


def test_registry_health_check_all():
    registry = PluginRegistry()
    registry.load_from_config({"jenkins": {"enabled": True}})
    results = registry.health_check_all()
    assert "jenkins" in results


def test_registry_manifests():
    registry = PluginRegistry()
    registry.load_from_config({
        "dynatrace": {"enabled": True},
        "jenkins": {"enabled": True},
        "blast_radius": {"enabled": True},
    })
    manifests = registry.manifests()
    assert len(manifests) == 3
    names = {m["name"] for m in manifests}
    assert "dynatrace" in names
    assert "jenkins" in names
    assert "blast_radius" in names


def test_discover_capabilities():
    plugin = JenkinsPlugin({})
    caps = plugin.discover_capabilities()
    assert caps == ["changes"]

    from services.connectors.dynatrace import DynatraceConnector
    dt = DynatraceConnector({})
    caps = dt.discover_capabilities()
    assert "entities" in caps
    assert "relations" in caps
