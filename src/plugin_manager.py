"""
src/plugin_manager.py — Lightweight Plugin System for Agentic AI HTML5 Parser.

Discovers plugins by scanning ``plugins/*/plugin.yml`` relative to the project
root, dynamically imports each plugin's ``entry_point`` Python module, and calls
its ``register(manager)`` function to register hooks.

Supported hook events
---------------------
- ``before_tokenize``  — fired before the tokenizer runs (receives ``html``)
- ``after_tokenize``   — fired after tokenization (receives ``html``, ``tokens``)
- ``before_parse``     — fired before the tree‑builder runs (receives ``html``)
- ``after_parse``      — fired after a successful parse (receives ``html``, ``tree``)
- ``on_error``         — fired when the parser raises an exception (receives ``error``)

Usage
-----
    from src.plugin_manager import get_plugin_manager

    pm = get_plugin_manager()
    pm.load_plugins()                # discover & register all plugins
    pm.emit("after_parse", html=html_str, tree=root_node)
"""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Optional YAML support — fall back to a minimal inline parser if PyYAML
# is not installed so that the plugin system has zero hard dependencies.
# ---------------------------------------------------------------------------
try:
    import yaml as _yaml  # type: ignore

    def _load_yaml(path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as fh:
            return _yaml.safe_load(fh) or {}

except ImportError:  # pragma: no cover
    def _load_yaml(path: Path) -> Dict[str, Any]:  # type: ignore[misc]
        """Minimal key: value YAML parser (single‑level, no lists)."""
        data: Dict[str, Any] = {}
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, _, value = line.partition(":")
                    data[key.strip()] = value.strip().strip("\"'")
        return data


# ---------------------------------------------------------------------------
# Project‑root detection
# ---------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT: Path = _THIS_FILE.parent.parent  # …/Agentic AI HTML5 Parser/

PLUGINS_DIR: Path = PROJECT_ROOT / "plugins"


# ---------------------------------------------------------------------------
# PluginManager
# ---------------------------------------------------------------------------

class PluginManager:
    """
    Central registry for parser plugins and hook callbacks.

    Attributes
    ----------
    _hooks : dict
        Maps event names to lists of registered callback functions.
    _loaded_plugins : list
        Metadata dicts for each successfully loaded plugin.
    """

    #: Canonical set of supported hook event names.
    SUPPORTED_EVENTS: frozenset = frozenset([
        "before_tokenize",
        "after_tokenize",
        "before_parse",
        "after_parse",
        "on_error",
    ])

    def __init__(self) -> None:
        self._hooks: Dict[str, List[Callable]] = {event: [] for event in self.SUPPORTED_EVENTS}
        self._loaded_plugins: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Hook registry
    # ------------------------------------------------------------------

    def register_hook(self, event_name: str, callback: Callable) -> None:
        """Register *callback* for *event_name*.

        Parameters
        ----------
        event_name:
            One of the ``SUPPORTED_EVENTS``.
        callback:
            Any callable.  Receives keyword arguments specific to the event.
        """
        if event_name not in self.SUPPORTED_EVENTS:
            raise ValueError(
                f"Unknown event '{event_name}'.  "
                f"Supported events: {sorted(self.SUPPORTED_EVENTS)}"
            )
        self._hooks[event_name].append(callback)

    def emit(self, event_name: str, **kwargs: Any) -> None:
        """Invoke all callbacks registered for *event_name*.

        Parameters
        ----------
        event_name:
            Event to fire.
        **kwargs:
            Keyword arguments forwarded verbatim to each callback.
        """
        for callback in self._hooks.get(event_name, []):
            try:
                callback(**kwargs)
            except Exception as exc:  # noqa: BLE001
                print(f"[PluginManager] Error in '{event_name}' callback "
                      f"{callback!r}: {exc}")

    # ------------------------------------------------------------------
    # Plugin discovery & loading
    # ------------------------------------------------------------------

    def load_plugins(self, plugins_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Discover and load all plugins found under *plugins_dir*.

        For each sub‑directory that contains a ``plugin.yml`` file the manager:
        1. Reads the YAML metadata.
        2. Resolves the ``entry_point`` Python module relative to that directory.
        3. Imports the module and calls its ``register(manager)`` function.

        Parameters
        ----------
        plugins_dir:
            Directory to scan.  Defaults to ``PROJECT_ROOT/plugins/``.

        Returns
        -------
        list of dict
            Metadata for every plugin that was successfully loaded.
        """
        base = Path(plugins_dir) if plugins_dir else PLUGINS_DIR
        if not base.is_dir():
            return []

        loaded: List[Dict[str, Any]] = []
        for plugin_dir in sorted(base.iterdir()):
            if not plugin_dir.is_dir():
                continue
            manifest = plugin_dir / "plugin.yml"
            if not manifest.exists():
                continue

            meta = _load_yaml(manifest)
            meta.setdefault("_path", str(plugin_dir))

            entry_point: Optional[str] = meta.get("entry_point")
            if not entry_point:
                print(f"[PluginManager] Skipping '{plugin_dir.name}': "
                      "no 'entry_point' in plugin.yml")
                continue

            module = self._import_plugin_module(plugin_dir, entry_point)
            if module is None:
                continue

            register_fn = getattr(module, "register", None)
            if register_fn is None or not callable(register_fn):
                print(f"[PluginManager] Plugin '{meta.get('name', plugin_dir.name)}' "
                      "has no register() function — skipping.")
                continue

            try:
                register_fn(self)
                loaded.append(meta)
                print(f"[PluginManager] Loaded plugin: {meta.get('name', plugin_dir.name)} "
                      f"v{meta.get('version', '?')}")
            except Exception as exc:
                print(f"[PluginManager] Error loading plugin "
                      f"'{meta.get('name', plugin_dir.name)}': {exc}")

        self._loaded_plugins.extend(loaded)
        return loaded

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def loaded_plugins(self) -> List[Dict[str, Any]]:
        """Return a copy of the loaded‑plugin metadata list."""
        return list(self._loaded_plugins)

    def hook_count(self, event_name: str) -> int:
        """Return the number of callbacks registered for *event_name*."""
        return len(self._hooks.get(event_name, []))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _import_plugin_module(plugin_dir: Path, module_name: str):
        """Dynamically import a module from inside *plugin_dir*."""
        # Strip .py extension if accidentally included in plugin.yml
        module_name = module_name.removesuffix(".py")
        module_file = plugin_dir / f"{module_name}.py"

        if not module_file.exists():
            print(f"[PluginManager] Module file not found: {module_file}")
            return None

        # Build a unique fully-qualified module name to avoid collisions
        fq_name = f"_plugin_{plugin_dir.name}_{module_name}"

        spec = importlib.util.spec_from_file_location(fq_name, module_file)
        if spec is None or spec.loader is None:
            print(f"[PluginManager] Cannot create spec for: {module_file}")
            return None

        module = importlib.util.module_from_spec(spec)
        sys.modules[fq_name] = module
        try:
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
        except Exception as exc:
            print(f"[PluginManager] Import error in '{module_file}': {exc}")
            return None
        return module


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_PLUGIN_MANAGER_INSTANCE: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Return the global singleton ``PluginManager`` instance.

    Creates a new instance on the first call.  Thread safety is intentionally
    not enforced to keep the implementation simple for single‑threaded use.
    """
    global _PLUGIN_MANAGER_INSTANCE
    if _PLUGIN_MANAGER_INSTANCE is None:
        _PLUGIN_MANAGER_INSTANCE = PluginManager()
    return _PLUGIN_MANAGER_INSTANCE


def reset_plugin_manager() -> None:
    """Reset the global singleton (useful in tests)."""
    global _PLUGIN_MANAGER_INSTANCE
    _PLUGIN_MANAGER_INSTANCE = None
