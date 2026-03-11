"""Event Dispatcher Core."""
import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, List, Union

from .interfaces import Event, EventDispatcher

logger = logging.getLogger(__name__)

Handler = Union[Callable[[Event], None], Callable[[Event], Coroutine[Any, Any, None]]]


class SyncEventDispatcher(EventDispatcher):
    """Synchronous in-process event dispatcher."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        self._handlers[event_name].append(handler)
        logger.debug("Subscribed handler to event: %s", event_name)

    def unsubscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)

    def dispatch(self, event: Event) -> None:
        handlers = self._handlers.get(event.name, [])
        logger.info("Dispatching event: %s to %d handlers", event.name, len(handlers))
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error("Error in event handler for %s: %s", event.name, e)


class AsyncEventDispatcher(EventDispatcher):
    """Async event dispatcher."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Handler]] = defaultdict(list)

    def subscribe(self, event_name: str, handler: Handler) -> None:  # type: ignore[override]
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Handler) -> None:  # type: ignore[override]
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)

    def dispatch(self, event: Event) -> None:
        raise NotImplementedError("Use dispatch_async for AsyncEventDispatcher")

    async def dispatch_async(self, event: Event) -> None:
        handlers = self._handlers.get(event.name, [])
        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))  # type: ignore[arg-type]
            else:
                raise TypeError(
                    f"Sync handler {handler!r} registered on AsyncEventDispatcher. "
                    "Use SyncEventDispatcher for sync handlers."
                )
        if tasks:
            await asyncio.gather(*tasks)
