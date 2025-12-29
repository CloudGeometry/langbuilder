"""Conversation State Manager Component for LangBuilder.

Manages conversation state for multi-turn Slack interactions.
Uses in-memory storage with TTL-based expiration.
"""

import json
import time
from typing import Any
from langbuilder.custom.custom_component.component import Component
from langbuilder.io import DataInput, DropdownInput, IntInput, MessageTextInput, Output
from langbuilder.schema.data import Data


class ConversationStateManagerComponent(Component):
    """Manage conversation state for multi-turn Slack interactions."""

    display_name = "Conversation State Manager"
    description = "Stores and retrieves conversation state for multi-turn Slack agent interactions."
    documentation = "https://docs.langbuilder.org/components-slack#conversation-state"
    icon = "database"
    name = "ConversationStateManager"

    # Class-level state storage (persists across instances within same process)
    _states: dict[str, dict[str, Any]] = {}

    inputs = [
        DropdownInput(
            name="operation",
            display_name="Operation",
            options=["get", "set", "update", "delete", "clear_expired"],
            value="get",
            info="Operation to perform on conversation state",
            required=True,
        ),
        MessageTextInput(
            name="session_key",
            display_name="Session Key",
            info="Unique key for the conversation (e.g., user_id + thread_ts)",
            required=True,
        ),
        DataInput(
            name="state_data",
            display_name="State Data",
            info="Data to store (for set/update operations)",
            required=False,
        ),
        IntInput(
            name="ttl_seconds",
            display_name="TTL (seconds)",
            value=3600,
            info="Time-to-live for state entries (default: 1 hour)",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="State", name="state", method="manage_state"),
        Output(display_name="Exists", name="exists", method="check_exists"),
    ]

    def _generate_key(self) -> str:
        """Generate storage key from session_key."""
        return f"conv_state:{self.session_key}"

    @classmethod
    def _get_states(cls) -> dict[str, dict[str, Any]]:
        """Get the class-level state storage."""
        if not hasattr(cls, '_states') or cls._states is None:
            cls._states = {}
        return cls._states

    def _cleanup_expired(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        current_time = time.time()
        expired_keys = []
        states = self._get_states()

        for key, entry in states.items():
            if entry.get("expires_at", 0) < current_time:
                expired_keys.append(key)

        for key in expired_keys:
            del states[key]

        return len(expired_keys)

    def check_exists(self) -> Data:
        """Check if state exists for the session key."""
        key = self._generate_key()
        states = self._get_states()
        entry = states.get(key)

        if entry is None:
            return Data(data={"exists": False})

        # Check if expired
        if entry.get("expires_at", 0) < time.time():
            del states[key]
            return Data(data={"exists": False, "was_expired": True})

        return Data(data={"exists": True})

    def manage_state(self) -> Data:
        """Perform the specified operation on conversation state."""
        key = self._generate_key()
        current_time = time.time()
        states = self._get_states()

        if self.operation == "get":
            entry = states.get(key)

            if entry is None:
                return Data(data={
                    "found": False,
                    "state": {},
                    "session_key": self.session_key,
                    "status": "NEW",
                    "contacts": [],
                })

            # Check if expired
            if entry.get("expires_at", 0) < current_time:
                del states[key]
                return Data(data={
                    "found": False,
                    "state": {},
                    "session_key": self.session_key,
                    "was_expired": True,
                    "status": "NEW",
                    "contacts": [],
                })

            return Data(data={
                "found": True,
                "state": entry.get("data", {}),
                "session_key": self.session_key,
                "created_at": entry.get("created_at"),
                "updated_at": entry.get("updated_at"),
                "expires_at": entry.get("expires_at"),
            })

        elif self.operation == "set":
            # Extract data to store
            if isinstance(self.state_data, Data):
                data_to_store = self.state_data.data
            elif isinstance(self.state_data, dict):
                data_to_store = self.state_data
            elif isinstance(self.state_data, str):
                try:
                    data_to_store = json.loads(self.state_data)
                except json.JSONDecodeError:
                    data_to_store = {"value": self.state_data}
            else:
                data_to_store = {}

            expires_at = current_time + (self.ttl_seconds or 3600)

            states[key] = {
                "data": data_to_store,
                "created_at": current_time,
                "updated_at": current_time,
                "expires_at": expires_at,
            }

            return Data(data={
                "success": True,
                "operation": "set",
                "session_key": self.session_key,
                "state": data_to_store,
                "expires_at": expires_at,
            })

        elif self.operation == "update":
            # Merge with existing state
            entry = states.get(key, {})
            existing_data = entry.get("data", {})

            if isinstance(self.state_data, Data):
                new_data = self.state_data.data
            elif isinstance(self.state_data, dict):
                new_data = self.state_data
            elif isinstance(self.state_data, str):
                try:
                    new_data = json.loads(self.state_data)
                except json.JSONDecodeError:
                    new_data = {"value": self.state_data}
            else:
                new_data = {}

            # Merge: new data overwrites existing
            merged_data = {**existing_data, **new_data}
            expires_at = current_time + (self.ttl_seconds or 3600)

            states[key] = {
                "data": merged_data,
                "created_at": entry.get("created_at", current_time),
                "updated_at": current_time,
                "expires_at": expires_at,
            }

            return Data(data={
                "success": True,
                "operation": "update",
                "session_key": self.session_key,
                "state": merged_data,
                "expires_at": expires_at,
            })

        elif self.operation == "delete":
            existed = key in states
            if existed:
                del states[key]

            return Data(data={
                "success": True,
                "operation": "delete",
                "session_key": self.session_key,
                "existed": existed,
            })

        elif self.operation == "clear_expired":
            removed_count = self._cleanup_expired()
            return Data(data={
                "success": True,
                "operation": "clear_expired",
                "removed_count": removed_count,
                "remaining_count": len(states),
            })

        else:
            return Data(data={
                "success": False,
                "error": f"Unknown operation: {self.operation}",
            })
