"""
Slack Message Sender - LangBuilder Custom Component

Posts messages to Slack channels using the Slack Web API.
Supports rich formatting with markdown and context data from HubSpot.

Author: CloudGeometry
Project: ICP Validator - Slack Integration
"""

from langbuilder.custom import Component
from langbuilder.io import HandleInput, StrInput, SecretStrInput, Output
from langbuilder.schema import Data
import httpx


class SlackMessageSender(Component):
    """
    Posts a message to a Slack channel.

    Uses the Slack Web API chat.postMessage endpoint.
    Supports markdown formatting and can include context data
    from upstream components (e.g., HubSpot contact info).

    Required Slack scopes: chat:write, chat:write.public (optional)
    """

    display_name = "Slack Message Sender"
    description = "Posts a message to a Slack channel"
    icon = "MessageSquare"
    name = "SlackMessageSender"

    inputs = [
        SecretStrInput(
            name="bot_token",
            display_name="Bot Token",
            required=True,
            info="Slack Bot OAuth Token (starts with xoxb-)",
        ),
        StrInput(
            name="channel",
            display_name="Channel",
            required=True,
            info="Channel name (#sales) or Channel ID (C01234567)",
        ),
        HandleInput(
            name="message",
            display_name="Message",
            input_types=["Data", "Message"],
            required=True,
            info="Message content to post (text or Data with 'text' or 'message' field)",
        ),
        HandleInput(
            name="context_data",
            display_name="Context Data",
            input_types=["Data"],
            required=False,
            info="Optional context data (e.g., HubSpot contact info) for formatting",
        ),
        StrInput(
            name="message_template",
            display_name="Message Template",
            required=False,
            advanced=True,
            info="Optional template with {placeholders} for context_data fields",
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Result",
            method="send_message",
        ),
    ]

    def _extract_value(self, input_data, field_name: str) -> str:
        """Extract string value from Data, Message, or string input."""
        if input_data is None:
            return ""

        # Handle list of Data objects
        if isinstance(input_data, list) and len(input_data) > 0:
            input_data = input_data[0]

        # Handle Data object
        if hasattr(input_data, "data"):
            data = input_data.data
            if isinstance(data, dict):
                # Try field name, then common alternatives
                for key in [field_name, "text", "message", "content", "reasoning", "value"]:
                    if key in data:
                        return str(data[key])
                # Return first value if nothing matches
                if data:
                    return str(next(iter(data.values())))
            return str(data)

        # Handle Message object
        if hasattr(input_data, "text"):
            return str(input_data.text)

        # Handle string
        return str(input_data)

    def _format_message(self) -> str:
        """Format the message, optionally using template and context data."""
        # Get base message
        message_text = self._extract_value(self.message, "message")

        # If we have a template and context data, use template formatting
        if self.message_template and self.context_data:
            try:
                context = {}
                if hasattr(self.context_data, "data") and isinstance(self.context_data.data, dict):
                    context = self.context_data.data
                message_text = self.message_template.format(**context)
            except KeyError as e:
                # If template formatting fails, fall back to base message
                self.log(f"Template formatting failed: missing key {e}")

        return message_text

    async def send_message(self) -> Data:
        """
        Post a message to Slack channel.

        Returns:
            Data object with success status, message timestamp, and channel info
        """
        url = "https://slack.com/api/chat.postMessage"

        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json",
        }

        message_text = self._format_message()

        payload = {
            "channel": self.channel,
            "text": message_text,
            "mrkdwn": True,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                result = response.json()

                if result.get("ok"):
                    self.status = f"Message posted to {self.channel}"
                    return Data(data={
                        "success": True,
                        "channel": result.get("channel"),
                        "ts": result.get("ts"),
                        "message": message_text[:100] + "..." if len(message_text) > 100 else message_text,
                    })
                else:
                    error = result.get("error", "Unknown error")
                    self.status = f"Error: {error}"
                    return Data(data={
                        "success": False,
                        "error": error,
                        "channel": self.channel,
                    })

        except httpx.TimeoutException:
            self.status = "Request timeout"
            return Data(data={
                "success": False,
                "error": "Request timed out after 10 seconds",
            })
        except Exception as e:
            self.status = f"Error: {str(e)}"
            return Data(data={
                "success": False,
                "error": str(e),
            })
