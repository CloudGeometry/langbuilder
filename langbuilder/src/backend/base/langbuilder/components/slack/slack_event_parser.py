"""Slack Event Parser Component for LangBuilder.

Parses incoming Slack events from Event Subscriptions API.
Handles URL verification challenges and extracts event data.
"""

import json
from langbuilder.custom.custom_component.component import Component
from langbuilder.io import DataInput, MessageTextInput, Output
from langbuilder.schema.data import Data
from langbuilder.schema import Message


class SlackEventParserComponent(Component):
    """Parse Slack events from Event Subscriptions webhook."""

    display_name = "Slack Event Parser"
    description = "Parses incoming Slack events and extracts event type, user, text, and channel information."
    documentation = "https://api.slack.com/apis/events-api"
    icon = "slack"
    name = "SlackEventParser"

    inputs = [
        DataInput(
            name="webhook_data",
            display_name="Webhook Data",
            info="Raw webhook payload from Slack Event Subscriptions",
            required=True,
        ),
        MessageTextInput(
            name="bot_user_id",
            display_name="Bot User ID",
            info="The bot's Slack user ID (to filter out bot's own messages). Find in Slack App settings.",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Event Data", name="event_data", method="parse_event"),
        Output(display_name="Session Key", name="session_key", method="get_session_key"),
        Output(display_name="Is Challenge", name="is_challenge", method="check_challenge"),
        Output(display_name="Challenge Response", name="challenge_response", method="get_challenge_response"),
    ]

    def _get_payload(self) -> dict:
        """Extract payload from webhook data."""
        if isinstance(self.webhook_data, Data):
            return self.webhook_data.data
        elif isinstance(self.webhook_data, dict):
            return self.webhook_data
        elif isinstance(self.webhook_data, str):
            try:
                return json.loads(self.webhook_data)
            except json.JSONDecodeError:
                return {"raw": self.webhook_data}
        return {}

    def get_session_key(self) -> Message:
        """Generate a session key for state management: channel:thread_ts."""
        payload = self._get_payload()

        # Handle event callback type
        if payload.get("type") == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type", "")

            # Handle Agents & AI Apps thread events
            if event_type in ("assistant_thread_started", "assistant_thread_context_changed"):
                assistant_thread = event.get("assistant_thread", {})
                channel = assistant_thread.get("channel_id", "")
                thread_ts = assistant_thread.get("thread_ts", "")
            else:
                # Standard message/mention events
                channel = event.get("channel", "")
                ts = event.get("ts", "")
                thread_ts = event.get("thread_ts", ts)  # Use ts if no thread_ts

            session_key = f"{channel}:{thread_ts}"
            return Message(text=session_key)

        # Fallback for unknown payload types
        return Message(text="unknown:unknown")

    def check_challenge(self) -> Data:
        """Check if this is a URL verification challenge."""
        payload = self._get_payload()
        is_challenge = payload.get("type") == "url_verification"
        return Data(data={"is_challenge": is_challenge})

    def get_challenge_response(self) -> Data:
        """Return the challenge response for URL verification."""
        payload = self._get_payload()
        if payload.get("type") == "url_verification":
            challenge = payload.get("challenge", "")
            return Data(data={"challenge": challenge, "should_respond": True})
        return Data(data={"challenge": "", "should_respond": False})

    def parse_event(self) -> Data:
        """Parse Slack event and extract relevant information."""
        payload = self._get_payload()

        # Handle URL verification challenge
        if payload.get("type") == "url_verification":
            return Data(data={
                "event_type": "url_verification",
                "challenge": payload.get("challenge", ""),
                "is_challenge": True,
            })

        # Handle event callbacks
        if payload.get("type") == "event_callback":
            event = payload.get("event", {})
            event_type = event.get("type", "unknown")

            # Extract common fields
            user_id = event.get("user", "")
            channel = event.get("channel", "")
            text = event.get("text", "")
            ts = event.get("ts", "")
            thread_ts = event.get("thread_ts", "")

            # Check if this is from the bot itself
            bot_id = event.get("bot_id", "")
            is_bot_message = bool(bot_id) or (self.bot_user_id and user_id == self.bot_user_id)

            # Handle different event types
            if event_type == "message":
                subtype = event.get("subtype", "")

                # Skip bot messages, message changes, etc.
                if subtype in ["bot_message", "message_changed", "message_deleted"]:
                    return Data(data={
                        "event_type": "message",
                        "subtype": subtype,
                        "should_process": False,
                        "reason": f"Skipping {subtype}",
                    })

                if is_bot_message:
                    return Data(data={
                        "event_type": "message",
                        "should_process": False,
                        "reason": "Message from bot itself",
                    })

                return Data(data={
                    "event_type": "message",
                    "subtype": subtype,
                    "user_id": user_id,
                    "channel": channel,
                    "text": text,
                    "ts": ts,
                    "thread_ts": thread_ts or ts,  # Use ts if no thread
                    "should_process": True,
                    "is_dm": channel.startswith("D"),  # DMs start with D
                    "is_thread_reply": bool(thread_ts),
                })

            elif event_type == "assistant_thread_started":
                # Slack Agents & AI Apps panel opened
                assistant_thread = event.get("assistant_thread", {})
                return Data(data={
                    "event_type": "assistant_thread_started",
                    "user_id": assistant_thread.get("user_id", user_id),
                    "channel": assistant_thread.get("channel_id", channel),
                    "thread_ts": assistant_thread.get("thread_ts", ""),
                    "context": assistant_thread.get("context", {}),
                    "should_process": True,
                    "is_agent_panel": True,
                })

            elif event_type == "assistant_thread_context_changed":
                # Context changed in agent panel
                assistant_thread = event.get("assistant_thread", {})
                return Data(data={
                    "event_type": "assistant_thread_context_changed",
                    "user_id": assistant_thread.get("user_id", user_id),
                    "channel": assistant_thread.get("channel_id", channel),
                    "thread_ts": assistant_thread.get("thread_ts", ""),
                    "context": assistant_thread.get("context", {}),
                    "should_process": True,
                })

            elif event_type == "app_mention":
                # Bot was mentioned in a channel
                return Data(data={
                    "event_type": "app_mention",
                    "user_id": user_id,
                    "channel": channel,
                    "text": text,
                    "ts": ts,
                    "thread_ts": thread_ts or ts,
                    "should_process": True,
                })

            else:
                # Other event types
                return Data(data={
                    "event_type": event_type,
                    "user_id": user_id,
                    "channel": channel,
                    "text": text,
                    "ts": ts,
                    "should_process": False,
                    "reason": f"Unhandled event type: {event_type}",
                    "raw_event": event,
                })

        # Unknown payload type
        return Data(data={
            "event_type": "unknown",
            "should_process": False,
            "reason": f"Unknown payload type: {payload.get('type', 'none')}",
            "raw_payload": payload,
        })
