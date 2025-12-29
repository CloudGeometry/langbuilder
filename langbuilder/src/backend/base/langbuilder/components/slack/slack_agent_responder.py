"""Slack Agent Responder Component for LangBuilder.

Sends responses to Slack with support for:
- Regular messages and threaded replies
- Agents & AI Apps API (set status, suggested prompts)
- Block Kit formatting
"""

import json
import httpx
from langbuilder.custom.custom_component.component import Component
from langbuilder.io import (
    BoolInput,
    DataInput,
    DropdownInput,
    MessageTextInput,
    SecretStrInput,
    Output,
)
from langbuilder.schema.data import Data


class SlackAgentResponderComponent(Component):
    """Send responses to Slack with agent panel support."""

    display_name = "Slack Agent Responder"
    description = "Sends messages to Slack with support for threaded replies and Agents & AI Apps features."
    documentation = "https://api.slack.com/docs/agents-ai-apps"
    icon = "slack"
    name = "SlackAgentResponder"

    inputs = [
        SecretStrInput(
            name="bot_token",
            display_name="Bot Token",
            info="Slack Bot User OAuth Token (xoxb-...)",
            required=True,
        ),
        DataInput(
            name="event_data",
            display_name="Event Data",
            info="Slack event data containing channel, thread_ts (from SlackEventParser)",
            required=False,
        ),
        MessageTextInput(
            name="channel",
            display_name="Channel",
            info="Channel ID to send message to (overrides event_data.channel)",
            required=False,
        ),
        MessageTextInput(
            name="thread_ts",
            display_name="Thread Timestamp",
            info="Thread timestamp to reply in (overrides event_data.thread_ts)",
            required=False,
        ),
        DataInput(
            name="message_data",
            display_name="Message Data",
            info="Message content (text or Data with 'text' field)",
            required=True,
        ),
        DropdownInput(
            name="response_type",
            display_name="Response Type",
            options=["message", "set_status", "set_suggested_prompts", "set_title"],
            value="message",
            info="Type of response to send",
            required=True,
        ),
        BoolInput(
            name="use_blocks",
            display_name="Use Block Kit",
            value=False,
            info="Format message using Block Kit sections",
            advanced=True,
        ),
        DataInput(
            name="suggested_prompts",
            display_name="Suggested Prompts",
            info="List of suggested prompts for agent panel (for set_suggested_prompts)",
            required=False,
            advanced=True,
        ),
        MessageTextInput(
            name="status_text",
            display_name="Status Text",
            info="Status message for agent panel (for set_status)",
            required=False,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Result", name="result", method="send_response"),
    ]

    def _get_channel(self) -> str:
        """Get channel from direct input or event_data."""
        if self.channel:
            return str(self.channel)
        if self.event_data:
            data = self.event_data.data if isinstance(self.event_data, Data) else self.event_data
            if isinstance(data, dict):
                return data.get("channel", "")
        return ""

    def _get_thread_ts(self) -> str:
        """Get thread_ts from direct input or event_data."""
        if self.thread_ts:
            return str(self.thread_ts)
        if self.event_data:
            data = self.event_data.data if isinstance(self.event_data, Data) else self.event_data
            if isinstance(data, dict):
                return data.get("thread_ts", "")
        return ""

    def _get_message_text(self) -> str:
        """Extract message text from message_data."""
        if isinstance(self.message_data, Data):
            data = self.message_data.data
            # Try common text fields
            for key in ["text", "message", "content", "response"]:
                if key in data:
                    return str(data[key])
            # Return JSON string if no text field found
            return json.dumps(data, indent=2)
        elif isinstance(self.message_data, dict):
            for key in ["text", "message", "content", "response"]:
                if key in self.message_data:
                    return str(self.message_data[key])
            return json.dumps(self.message_data, indent=2)
        elif isinstance(self.message_data, str):
            return self.message_data
        return str(self.message_data)

    def _format_as_blocks(self, text: str) -> list[dict]:
        """Format text as Block Kit blocks."""
        # Split text into sections if it's long
        blocks = []

        # Add text as section block(s)
        # Slack has a 3000 char limit per section
        max_section_length = 2900

        if len(text) <= max_section_length:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": text}
            })
        else:
            # Split into multiple sections
            for i in range(0, len(text), max_section_length):
                chunk = text[i:i + max_section_length]
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": chunk}
                })

        return blocks

    def send_response(self) -> Data:
        """Send response to Slack based on response_type."""
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            if self.response_type == "message":
                return self._send_message(headers)
            elif self.response_type == "set_status":
                return self._set_agent_status(headers)
            elif self.response_type == "set_suggested_prompts":
                return self._set_suggested_prompts(headers)
            elif self.response_type == "set_title":
                return self._set_agent_title(headers)
            else:
                return Data(data={
                    "success": False,
                    "error": f"Unknown response type: {self.response_type}",
                })
        except httpx.HTTPError as e:
            return Data(data={
                "success": False,
                "error": f"HTTP error: {str(e)}",
            })
        except Exception as e:
            return Data(data={
                "success": False,
                "error": f"Error: {str(e)}",
            })

    def _send_message(self, headers: dict) -> Data:
        """Send a chat message."""
        text = self._get_message_text()
        channel = self._get_channel()
        thread_ts = self._get_thread_ts()

        if not channel:
            return Data(data={
                "success": False,
                "error": "Channel is required (provide channel input or event_data with channel)",
            })

        payload = {
            "channel": channel,
            "text": text,
        }

        # Add thread_ts if available
        if thread_ts:
            payload["thread_ts"] = thread_ts

        # Use blocks if requested
        if self.use_blocks:
            payload["blocks"] = self._format_as_blocks(text)

        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://slack.com/api/chat.postMessage",
                headers=headers,
                json=payload,
            )

        result = response.json()

        if result.get("ok"):
            return Data(data={
                "success": True,
                "channel": result.get("channel"),
                "ts": result.get("ts"),
                "message": text,
            })
        else:
            return Data(data={
                "success": False,
                "error": result.get("error", "Unknown error"),
                "response": result,
            })

    def _set_agent_status(self, headers: dict) -> Data:
        """Set agent status in Agents & AI Apps panel."""
        channel = self._get_channel()
        thread_ts = self._get_thread_ts()

        if not thread_ts:
            return Data(data={
                "success": False,
                "error": "thread_ts is required for set_status",
            })

        payload = {
            "channel_id": channel,
            "thread_ts": thread_ts,
            "status": self.status_text or "Processing...",
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://slack.com/api/assistant.threads.setStatus",
                headers=headers,
                json=payload,
            )

        result = response.json()

        if result.get("ok"):
            return Data(data={
                "success": True,
                "operation": "set_status",
                "status": self.status_text,
            })
        else:
            return Data(data={
                "success": False,
                "error": result.get("error", "Unknown error"),
                "response": result,
            })

    def _set_suggested_prompts(self, headers: dict) -> Data:
        """Set suggested prompts in Agents & AI Apps panel."""
        channel = self._get_channel()
        thread_ts = self._get_thread_ts()

        if not thread_ts:
            return Data(data={
                "success": False,
                "error": "thread_ts is required for set_suggested_prompts",
            })

        # Extract prompts from data
        prompts = []
        if isinstance(self.suggested_prompts, Data):
            prompts_data = self.suggested_prompts.data
            if isinstance(prompts_data, list):
                prompts = prompts_data
            elif "prompts" in prompts_data:
                prompts = prompts_data["prompts"]
        elif isinstance(self.suggested_prompts, list):
            prompts = self.suggested_prompts

        # Format prompts for Slack API
        formatted_prompts = []
        for p in prompts:
            if isinstance(p, str):
                formatted_prompts.append({"title": p, "message": p})
            elif isinstance(p, dict):
                formatted_prompts.append({
                    "title": p.get("title", p.get("text", "")),
                    "message": p.get("message", p.get("text", "")),
                })

        payload = {
            "channel_id": channel,
            "thread_ts": thread_ts,
            "prompts": formatted_prompts,
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://slack.com/api/assistant.threads.setSuggestedPrompts",
                headers=headers,
                json=payload,
            )

        result = response.json()

        if result.get("ok"):
            return Data(data={
                "success": True,
                "operation": "set_suggested_prompts",
                "prompts": formatted_prompts,
            })
        else:
            return Data(data={
                "success": False,
                "error": result.get("error", "Unknown error"),
                "response": result,
            })

    def _set_agent_title(self, headers: dict) -> Data:
        """Set thread title in Agents & AI Apps panel."""
        channel = self._get_channel()
        thread_ts = self._get_thread_ts()

        if not thread_ts:
            return Data(data={
                "success": False,
                "error": "thread_ts is required for set_title",
            })

        title = self._get_message_text()

        payload = {
            "channel_id": channel,
            "thread_ts": thread_ts,
            "title": title,
        }

        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://slack.com/api/assistant.threads.setTitle",
                headers=headers,
                json=payload,
            )

        result = response.json()

        if result.get("ok"):
            return Data(data={
                "success": True,
                "operation": "set_title",
                "title": title,
            })
        else:
            return Data(data={
                "success": False,
                "error": result.get("error", "Unknown error"),
                "response": result,
            })
