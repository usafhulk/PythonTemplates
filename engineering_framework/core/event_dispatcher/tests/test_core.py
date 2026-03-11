"""Event Dispatcher Tests."""
import asyncio
import pytest
from ..core import SyncEventDispatcher, AsyncEventDispatcher
from ..interfaces import Event


def test_sync_dispatch():
    dispatcher = SyncEventDispatcher()
    received = []
    dispatcher.subscribe("user.created", lambda e: received.append(e.data))
    dispatcher.dispatch(Event("user.created", data={"id": 1}))
    assert received == [{"id": 1}]


def test_sync_unsubscribe():
    dispatcher = SyncEventDispatcher()
    received = []
    handler = lambda e: received.append(e.data)
    dispatcher.subscribe("test", handler)
    dispatcher.unsubscribe("test", handler)
    dispatcher.dispatch(Event("test", data="x"))
    assert received == []


def test_async_dispatch():
    dispatcher = AsyncEventDispatcher()
    received = []
    async def handler(event):
        received.append(event.data)
    dispatcher.subscribe("order.placed", handler)
    asyncio.run(dispatcher.dispatch_async(Event("order.placed", data={"order_id": "ORD-1"})))
    assert received == [{"order_id": "ORD-1"}]
