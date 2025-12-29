"""State Router Component for Interactive Slack Agent.

Routes conversation based on current state and user input.
Handles the multi-turn conversation flow for ICP validation.
"""

import re
from langbuilder.custom.custom_component.component import Component
from langbuilder.io import DataInput, Output
from langbuilder.schema.data import Data


class StateRouterComponent(Component):
    """Route conversation based on state and user input."""

    display_name = "State Router"
    description = "Routes conversation based on current state and user input for multi-turn Slack agent."
    documentation = ""
    icon = "git-branch"
    name = "StateRouter"

    # Conversation states
    STATE_NEW = "NEW"
    STATE_AWAITING_NAME = "AWAITING_NAME"
    STATE_AWAITING_SELECT = "AWAITING_SELECT"

    # Route outputs
    ROUTE_WELCOME = "welcome"
    ROUTE_SEARCH = "search"
    ROUTE_SELECT = "select"
    ROUTE_INVALID_SELECT = "invalid_select"
    ROUTE_SKIP = "skip"

    inputs = [
        DataInput(
            name="event_data",
            display_name="Event Data",
            info="Parsed Slack event data from SlackEventParser",
            required=True,
        ),
        DataInput(
            name="current_state",
            display_name="Current State",
            info="Current conversation state from ConversationStateManager",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Routing Decision", name="routing", method="route"),
    ]

    def route(self) -> Data:
        """Determine routing based on state and input."""
        # Extract event data
        event = self.event_data.data if hasattr(self.event_data, 'data') else self.event_data or {}

        # Check if we should skip (bot message, challenge, etc.)
        if not event.get("should_process", True):
            return Data(data={
                "route": self.ROUTE_SKIP,
                "reason": event.get("reason", "Should not process"),
                "state": self._get_state_value(),
            })

        # Check for challenge (URL verification)
        if event.get("is_challenge") or event.get("event_type") == "url_verification":
            return Data(data={
                "route": self.ROUTE_SKIP,
                "reason": "URL verification challenge",
                "challenge": event.get("challenge", ""),
            })

        # Get current state
        state_data = {}
        if self.current_state:
            state_data = self.current_state.data if hasattr(self.current_state, 'data') else self.current_state or {}

        current_status = state_data.get("status", self.STATE_NEW)
        stored_contacts = state_data.get("contacts", [])

        # Get user input
        user_text = event.get("text", "").strip()
        event_type = event.get("event_type", "message")
        channel = event.get("channel", "")
        thread_ts = event.get("thread_ts", "")

        # Strip @mentions from text (e.g., "<@U0A4QSXV85Q> Antoine" -> "Antoine")
        clean_text = re.sub(r'<@[A-Z0-9]+>', '', user_text).strip()

        # Route based on event type and state

        # For app_mention with actual text after the mention, go directly to search
        if event_type == "app_mention" and clean_text:
            return Data(data={
                "route": self.ROUTE_SEARCH,
                "search_query": clean_text,
                "new_state": {
                    "status": self.STATE_AWAITING_SELECT,
                    "contacts": [],
                    "last_query": clean_text,
                },
                "channel": channel,
                "thread_ts": thread_ts,
            })

        # New thread started (agent panel opened) or just @mentioned without text
        if event_type == "assistant_thread_started" or (current_status == self.STATE_NEW and not clean_text):
            return Data(data={
                "route": self.ROUTE_WELCOME,
                "new_state": {
                    "status": self.STATE_AWAITING_NAME,
                    "contacts": [],
                },
                "channel": channel,
                "thread_ts": thread_ts,
                "message": "Welcome! Type a contact name to validate against our ICP criteria.",
            })

        # Awaiting name - user should type a contact name
        if current_status == self.STATE_AWAITING_NAME:
            search_text = clean_text or user_text
            if not search_text:
                return Data(data={
                    "route": self.ROUTE_SKIP,
                    "reason": "Empty message",
                    "state": current_status,
                })

            return Data(data={
                "route": self.ROUTE_SEARCH,
                "search_query": search_text,
                "new_state": {
                    "status": self.STATE_AWAITING_SELECT,
                    "contacts": [],
                    "last_query": search_text,
                },
                "channel": channel,
                "thread_ts": thread_ts,
            })

        # Awaiting selection - user should type a number
        if current_status == self.STATE_AWAITING_SELECT:
            # Check if user typed a valid number
            if user_text.isdigit():
                selection = int(user_text)
                if 1 <= selection <= len(stored_contacts):
                    selected_contact = stored_contacts[selection - 1]
                    return Data(data={
                        "route": self.ROUTE_SELECT,
                        "selected_contact": selected_contact,
                        "selection_index": selection,
                        "new_state": {
                            "status": self.STATE_AWAITING_NAME,  # Reset after selection
                            "contacts": [],
                        },
                        "channel": channel,
                        "thread_ts": thread_ts,
                    })
                else:
                    return Data(data={
                        "route": self.ROUTE_INVALID_SELECT,
                        "reason": f"Invalid selection: {selection}. Please type a number between 1 and {len(stored_contacts)}.",
                        "state": current_status,
                        "contacts": stored_contacts,
                        "channel": channel,
                        "thread_ts": thread_ts,
                    })
            else:
                # User typed something other than a number - maybe they want to search again?
                # For now, prompt them to select
                return Data(data={
                    "route": self.ROUTE_INVALID_SELECT,
                    "reason": f"Please type a number (1-{len(stored_contacts)}) to select a contact, or type a new name to search again.",
                    "state": current_status,
                    "contacts": stored_contacts,
                    "channel": channel,
                    "thread_ts": thread_ts,
                    # Also include the text in case they want to search
                    "search_query": user_text,
                })

        # Unknown state - default to awaiting name
        return Data(data={
            "route": self.ROUTE_SEARCH,
            "search_query": user_text,
            "new_state": {
                "status": self.STATE_AWAITING_NAME,
                "contacts": [],
            },
            "channel": channel,
            "thread_ts": thread_ts,
        })

    def _get_state_value(self) -> str:
        """Get current state value."""
        if self.current_state:
            state_data = self.current_state.data if hasattr(self.current_state, 'data') else self.current_state or {}
            return state_data.get("status", self.STATE_NEW)
        return self.STATE_NEW
