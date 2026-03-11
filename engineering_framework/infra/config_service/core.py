"""Config Service Core."""
import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional

from .interfaces import ConfigService

logger = logging.getLogger(__name__)


class InMemoryConfigService(ConfigService):
    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = dict(initial or {})
        self._watchers: Dict[str, List[Callable[[str, Any], None]]] = defaultdict(list)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        old = self._data.get(key)
        self._data[key] = value
        if old != value:
            for cb in self._watchers.get(key, []):
                try:
                    cb(key, value)
                except Exception as e:
                    logger.error("Watcher error for %s: %s", key, e)

    def watch(self, key: str, callback: Callable[[str, Any], None]) -> None:
        self._watchers[key].append(callback)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._data)
