"""Event Dispatcher Example."""
from engineering_framework.core.event_dispatcher.core import SyncEventDispatcher
from engineering_framework.core.event_dispatcher.interfaces import Event

dispatcher = SyncEventDispatcher()

def on_user_created(event):
    print(f"New user: {event.data}")

dispatcher.subscribe("user.created", on_user_created)
dispatcher.dispatch(Event("user.created", data={"id": 1, "email": "alice@example.com"}))
