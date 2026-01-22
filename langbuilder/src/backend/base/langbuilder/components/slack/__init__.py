"""LangBuilder Slack Components.

This module provides Slack integration components for LangBuilder flows.

Components:
    - SlackNotifyComponent: Post notification messages to Slack channels.
"""

from typing import TYPE_CHECKING

from langbuilder.components._importing import import_mod

# IDE support (not loaded at runtime)
if TYPE_CHECKING:
    from langbuilder.components.slack.slack_notify import SlackNotifyComponent

# Class name -> module name mapping
_dynamic_imports = {
    "SlackNotifyComponent": "slack_notify",
}

__all__ = ["SlackNotifyComponent"]


def __getattr__(attr_name: str):
    """Lazily import component classes on attribute access."""
    if attr_name not in _dynamic_imports:
        raise AttributeError(f"module {__name__!r} has no attribute {attr_name!r}")
    result = import_mod(attr_name, _dynamic_imports[attr_name], __spec__.parent)
    globals()[attr_name] = result
    return result
