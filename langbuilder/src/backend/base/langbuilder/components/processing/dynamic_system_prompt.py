"""
Dynamic System Prompt Component

Combines a static system prompt template with dynamic variables that change
between runs. The output can be fed directly into an Agent component.

Author: CloudGeometry
"""

from langbuilder.custom.custom_component.component import Component
from langbuilder.io import MessageTextInput, MultilineInput, Output
from langbuilder.schema.message import Message


class DynamicSystemPromptComponent(Component):
    """
    Creates a dynamic system prompt by combining a base template with
    runtime variables. Perfect for feeding into Agent components where
    you need a consistent structure but changing context.

    Example use cases:
    - Base prompt: "You are a helpful assistant for {company}. Current context: {context}"
    - Dynamic var: Latest user preferences, session state, or real-time data
    """

    display_name = "Dynamic System Prompt"
    description = "Combines a base system prompt template with dynamic runtime variables"
    icon = "braces"
    name = "DynamicSystemPrompt"

    inputs = [
        MultilineInput(
            name="base_prompt",
            display_name="Base System Prompt",
            info="The static part of your system prompt. Use {dynamic_input} as a placeholder "
                 "where the dynamic variable will be inserted. Example: 'You are an assistant. "
                 "Current context: {dynamic_input}'",
            required=True,
            value="You are a helpful AI assistant.\n\nCurrent context:\n{dynamic_input}",
        ),
        MessageTextInput(
            name="dynamic_input",
            display_name="Dynamic Input",
            info="The variable content that changes between runs. This will replace "
                 "{dynamic_input} in the base prompt, or be appended if no placeholder exists.",
            required=False,
            tool_mode=True,
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info="Text used to separate base prompt and dynamic input when no placeholder is found",
            required=False,
            value="\n\n---\n\n",
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            display_name="System Prompt",
            name="system_prompt",
            method="build_system_prompt",
        ),
    ]

    def build_system_prompt(self) -> Message:
        """
        Build the final system prompt by combining base template with dynamic input.

        Returns:
            Message: The combined system prompt as a Message object
        """
        base = self.base_prompt or ""
        dynamic = self._extract_text(self.dynamic_input) or ""
        separator = self.separator or "\n\n"

        # Check if placeholder exists in base prompt
        if "{dynamic_input}" in base:
            # Replace placeholder with dynamic content
            final_prompt = base.replace("{dynamic_input}", dynamic)
        elif dynamic:
            # Append dynamic content with separator
            final_prompt = f"{base}{separator}{dynamic}"
        else:
            # No dynamic content, use base as-is
            final_prompt = base

        self.status = f"Built prompt: {len(final_prompt)} chars"
        return Message(text=final_prompt)

    def _extract_text(self, value) -> str:
        """Extract text from Message, Data, or return string as-is."""
        if value is None:
            return ""
        if hasattr(value, "text"):
            return str(value.text).strip()
        if hasattr(value, "data") and isinstance(value.data, dict):
            for key in ["text", "content", "value", "message"]:
                if key in value.data:
                    return str(value.data[key]).strip()
            return ""
        return str(value).strip()
