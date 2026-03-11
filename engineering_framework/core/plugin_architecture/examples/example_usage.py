"""Plugin Architecture Example."""
from engineering_framework.core.plugin_architecture.core import DefaultPluginRegistry, PluginBase

class MetricsPlugin(PluginBase):
    _name = "metrics"
    _version = "1.0.0"

    def initialize(self, config):
        print(f"Metrics plugin initialized: port={config.get('metrics_port', 9090)}")

registry = DefaultPluginRegistry()
registry.register(MetricsPlugin())
registry.initialize_all({"metrics_port": 8080})
