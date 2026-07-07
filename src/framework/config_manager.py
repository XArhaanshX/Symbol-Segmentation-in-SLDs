"""
Centralized Configuration Manager.

Loads config/project_config.yaml and provides a single access point for all
pipeline parameters.  Every module reads its settings through this manager
instead of opening YAML files directly.
"""

import os
import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DEFAULT_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "config", "project_config.yaml")

_config = None


def get_project_root():
    """Return the absolute path to the repository root."""
    return _PROJECT_ROOT


def load_config(config_path=None):
    """Load (or reload) the project configuration from YAML.

    Parameters
    ----------
    config_path : str, optional
        Path to a custom config file.  Defaults to ``config/project_config.yaml``.

    Returns
    -------
    dict
        The full configuration dictionary.
    """
    global _config
    path = config_path or _DEFAULT_CONFIG_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            "Run `python install.py` to initialise the repository."
        )

    with open(path, "r", encoding="utf-8") as fh:
        _config = yaml.safe_load(fh)

    return _config


def get_config():
    """Return the currently loaded configuration (lazy-load if needed)."""
    global _config
    if _config is None:
        load_config()
    return _config


def resolve_path(*parts):
    """Join *parts* relative to the project root and return an absolute path."""
    return os.path.join(_PROJECT_ROOT, *parts)
