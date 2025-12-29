"""Response Formatter Component for Interactive Slack Agent.

Formats different types of responses for the multi-turn conversation:
- Welcome message
- Not found message
- Contact list (numbered for selection)
- Validation result
"""

from langbuilder.custom.custom_component.component import Component
from langbuilder.io import DataInput, DropdownInput, MessageTextInput, Output
from langbuilder.schema.data import Data


class ResponseFormatterComponent(Component):
    """Format responses for the interactive Slack agent."""

    display_name = "Response Formatter"
    description = "Formats responses for the interactive Slack ICP agent (welcome, contact list, validation results)."
    documentation = ""
    icon = "message-square"
    name = "ResponseFormatter"

    # Response types
    TYPE_WELCOME = "welcome"
    TYPE_NOT_FOUND = "not_found"
    TYPE_CONTACT_LIST = "contact_list"
    TYPE_VALIDATION = "validation"
    TYPE_INVALID_SELECT = "invalid_select"
    TYPE_ERROR = "error"

    inputs = [
        DropdownInput(
            name="response_type",
            display_name="Response Type",
            options=["welcome", "not_found", "contact_list", "validation", "invalid_select", "error"],
            value="welcome",
            info="Type of response to format",
            required=True,
        ),
        DataInput(
            name="contacts",
            display_name="Contacts",
            info="List of contacts from HubSpot search (for contact_list type)",
            required=False,
        ),
        DataInput(
            name="validation_result",
            display_name="Validation Result",
            info="ICP validation result (for validation type)",
            required=False,
        ),
        MessageTextInput(
            name="search_query",
            display_name="Search Query",
            info="The search query that was used (for not_found message)",
            required=False,
        ),
        MessageTextInput(
            name="error_message",
            display_name="Error Message",
            info="Error message to display (for error type)",
            required=False,
        ),
        DataInput(
            name="selected_contact",
            display_name="Selected Contact",
            info="The contact that was selected (for validation type)",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Formatted Response", name="response", method="format_response"),
        Output(display_name="New State", name="new_state", method="get_new_state"),
    ]

    def format_response(self) -> Data:
        """Format the response based on type."""
        response_type = self._detect_response_type()

        if response_type == self.TYPE_WELCOME:
            return self._format_welcome()
        elif response_type == self.TYPE_NOT_FOUND:
            return self._format_not_found()
        elif response_type == self.TYPE_CONTACT_LIST:
            return self._format_contact_list()
        elif response_type == self.TYPE_VALIDATION:
            return self._format_validation()
        elif response_type == self.TYPE_INVALID_SELECT:
            return self._format_invalid_select()
        elif response_type == self.TYPE_ERROR:
            return self._format_error()
        else:
            return Data(data={"text": f"Unknown response type: {response_type}"})

    def _detect_response_type(self) -> str:
        """Auto-detect the response type based on available data."""
        # If explicitly set, use that
        if self.response_type and self.response_type != "welcome":
            return self.response_type

        # Check if we have contacts from HubSpot search
        contacts = self._get_contacts_list()
        if contacts:
            return self.TYPE_CONTACT_LIST

        # Check if contacts input is connected but empty (no results)
        if self.contacts is not None:
            data = self.contacts.data if hasattr(self.contacts, 'data') else self.contacts
            if isinstance(data, dict) and data.get("success") and data.get("count", 0) == 0:
                return self.TYPE_NOT_FOUND

        # Check if validation result is provided
        if self.validation_result:
            result = self.validation_result.data if hasattr(self.validation_result, 'data') else self.validation_result
            if isinstance(result, dict) and ("qualified" in result or "is_qualified" in result):
                return self.TYPE_VALIDATION

        # Check for error message
        if self.error_message:
            return self.TYPE_ERROR

        # Default to welcome
        return self.TYPE_WELCOME

    def get_new_state(self) -> Data:
        """Get the new state to save after this response."""
        response_type = self._detect_response_type()

        if response_type == self.TYPE_WELCOME:
            return Data(data={"status": "AWAITING_NAME", "contacts": []})

        elif response_type == self.TYPE_NOT_FOUND:
            return Data(data={"status": "AWAITING_NAME", "contacts": []})

        elif response_type == self.TYPE_CONTACT_LIST:
            contacts = self._get_contacts_list()
            return Data(data={"status": "AWAITING_SELECT", "contacts": contacts})

        elif response_type == self.TYPE_VALIDATION:
            return Data(data={"status": "AWAITING_NAME", "contacts": []})

        elif response_type == self.TYPE_INVALID_SELECT:
            # Keep the same state
            contacts = self._get_contacts_list()
            return Data(data={"status": "AWAITING_SELECT", "contacts": contacts})

        else:
            return Data(data={"status": "AWAITING_NAME", "contacts": []})

    def _format_welcome(self) -> Data:
        """Format welcome message."""
        text = (
            "*Welcome to the ICP Validator!* :wave:\n\n"
            "I can help you check if a contact matches our Ideal Customer Profile.\n\n"
            "*To get started:* Type a contact name (e.g., `Antoine` or `John Smith`)"
        )
        return Data(data={"text": text})

    def _format_not_found(self) -> Data:
        """Format not found message."""
        query = self.search_query or "your search"
        text = (
            f":mag: *No contacts found* for `{query}`\n\n"
            "Please try:\n"
            "• A different spelling\n"
            "• First name only\n"
            "• Last name only\n"
            "• Company name"
        )
        return Data(data={"text": text})

    def _format_contact_list(self) -> Data:
        """Format numbered contact list for selection."""
        contacts = self._get_contacts_list()

        if not contacts:
            return self._format_not_found()

        if len(contacts) == 1:
            # Single match - we'll auto-validate, but still show info
            contact = contacts[0]
            text = (
                f":white_check_mark: *Found 1 match:*\n\n"
                f"*{contact.get('name', 'Unknown')}*\n"
                f"• {contact.get('job_title', 'N/A')} at {contact.get('company', 'N/A')}\n"
                f"• {contact.get('email', 'N/A')}\n\n"
                "_Validating against ICP..._"
            )
            return Data(data={"text": text, "auto_validate": True, "contact": contact})

        # Multiple matches - show numbered list
        lines = [f":mag: *Found {len(contacts)} contacts:*\n"]

        for i, contact in enumerate(contacts, 1):
            name = contact.get("name", "Unknown")
            title = contact.get("job_title", "")
            company = contact.get("company", "")
            email = contact.get("email", "")

            detail = ""
            if title and company:
                detail = f"{title} @ {company}"
            elif company:
                detail = company
            elif title:
                detail = title

            lines.append(f"*{i}.* {name}")
            if detail:
                lines.append(f"      _{detail}_")
            if email:
                lines.append(f"      {email}")
            lines.append("")

        lines.append("*Type a number (1-{}) to validate a contact*".format(len(contacts)))

        text = "\n".join(lines)
        return Data(data={"text": text, "contacts": contacts})

    def _format_validation(self) -> Data:
        """Format validation result."""
        # Get validation result
        result = {}
        if self.validation_result:
            result = self.validation_result.data if hasattr(self.validation_result, 'data') else self.validation_result or {}

        # Get selected contact
        contact = {}
        if self.selected_contact:
            contact = self.selected_contact.data if hasattr(self.selected_contact, 'data') else self.selected_contact or {}

        is_qualified = result.get("qualified", result.get("is_qualified", False))
        reasoning = result.get("reasoning", result.get("reason", "No reasoning provided"))

        contact_name = contact.get("name", "Contact")
        contact_company = contact.get("company", "")

        if is_qualified:
            emoji = ":white_check_mark:"
            status = "QUALIFIED"
            color = "good"
        else:
            emoji = ":x:"
            status = "NOT ICP"
            color = "danger"

        text = (
            f"{emoji} *{status}*\n\n"
            f"*Contact:* {contact_name}"
        )

        if contact_company:
            text += f" ({contact_company})"

        text += f"\n\n*Analysis:*\n{reasoning}"
        text += "\n\n---\n_Type another name to validate more contacts_"

        return Data(data={"text": text, "qualified": is_qualified})

    def _format_invalid_select(self) -> Data:
        """Format invalid selection message."""
        contacts = self._get_contacts_list()
        max_num = len(contacts) if contacts else "?"

        text = (
            f":warning: *Invalid selection*\n\n"
            f"Please type a number between *1* and *{max_num}* to select a contact.\n\n"
            f"Or type a new name to search again."
        )
        return Data(data={"text": text})

    def _format_error(self) -> Data:
        """Format error message."""
        error = self.error_message or "An unexpected error occurred"
        text = (
            f":exclamation: *Error*\n\n"
            f"{error}\n\n"
            "_Please try again or type a different name._"
        )
        return Data(data={"text": text})

    def _get_contacts_list(self) -> list:
        """Extract contacts list from input."""
        if not self.contacts:
            return []

        data = self.contacts.data if hasattr(self.contacts, 'data') else self.contacts

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("contacts", [])

        return []
