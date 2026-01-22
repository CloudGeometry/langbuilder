from typing import Any

from composio import Action

from langbuilder.base.composio.composio_base import ComposioBaseComponent
from langbuilder.inputs import (
    IntInput,
    MessageTextInput,
    MultilineInput,
)
from langbuilder.logging import logger


class ComposioConfluenceAPIComponent(ComposioBaseComponent):
    """Confluence API component for interacting with Confluence services via Composio."""

    display_name: str = "Confluence"
    description: str = "Confluence API - Create, update, and manage pages, spaces, and content"
    icon = "Confluence"
    documentation: str = "https://docs.composio.dev/toolkits/confluence"
    app_name = "confluence"

    # Atlassian subdomain for authentication
    atlassian_subdomain: str = "cloudgeometry"

    _actions_data: dict = {
        "CONFLUENCE_CREATE_PAGE": {
            "display_name": "Create Page",
            "action_fields": [
                "CONFLUENCE_CREATE_PAGE_spaceId",
                "CONFLUENCE_CREATE_PAGE_title",
                "CONFLUENCE_CREATE_PAGE_body",
                "CONFLUENCE_CREATE_PAGE_parentId",
            ],
        },
        "CONFLUENCE_GET_PAGE_BY_ID": {
            "display_name": "Get Page By ID",
            "action_fields": [
                "CONFLUENCE_GET_PAGE_BY_ID_id",
                "CONFLUENCE_GET_PAGE_BY_ID_version",
                "CONFLUENCE_GET_PAGE_BY_ID_draft",
            ],
        },
        "CONFLUENCE_GET_PAGES": {
            "display_name": "Get Pages",
            "action_fields": [
                "CONFLUENCE_GET_PAGES_spaceId",
                "CONFLUENCE_GET_PAGES_title",
                "CONFLUENCE_GET_PAGES_status",
                "CONFLUENCE_GET_PAGES_body_format",
                "CONFLUENCE_GET_PAGES_limit",
                "CONFLUENCE_GET_PAGES_sort",
            ],
        },
        "CONFLUENCE_UPDATE_PAGE": {
            "display_name": "Update Page",
            "action_fields": [
                "CONFLUENCE_UPDATE_PAGE_id",
                "CONFLUENCE_UPDATE_PAGE_title",
                "CONFLUENCE_UPDATE_PAGE_body",
                "CONFLUENCE_UPDATE_PAGE_version_number",
                "CONFLUENCE_UPDATE_PAGE_spaceId",
            ],
        },
        "CONFLUENCE_DELETE_PAGE": {
            "display_name": "Delete Page",
            "action_fields": [
                "CONFLUENCE_DELETE_PAGE_id",
            ],
        },
        "CONFLUENCE_SEARCH_CONTENT": {
            "display_name": "Search Content",
            "action_fields": [
                "CONFLUENCE_SEARCH_CONTENT_query",
                "CONFLUENCE_SEARCH_CONTENT_spaceKey",
                "CONFLUENCE_SEARCH_CONTENT_limit",
                "CONFLUENCE_SEARCH_CONTENT_start",
                "CONFLUENCE_SEARCH_CONTENT_expand",
            ],
        },
        "CONFLUENCE_CREATE_SPACE": {
            "display_name": "Create Space",
            "action_fields": [
                "CONFLUENCE_CREATE_SPACE_key",
                "CONFLUENCE_CREATE_SPACE_name",
                "CONFLUENCE_CREATE_SPACE_description",
                "CONFLUENCE_CREATE_SPACE_type",
            ],
        },
        "CONFLUENCE_GET_SPACE_BY_ID": {
            "display_name": "Get Space By ID",
            "action_fields": [
                "CONFLUENCE_GET_SPACE_BY_ID_id",
            ],
        },
        "CONFLUENCE_GET_SPACES": {
            "display_name": "Get Spaces",
            "action_fields": [
                "CONFLUENCE_GET_SPACES_spaceKey",
                "CONFLUENCE_GET_SPACES_type",
                "CONFLUENCE_GET_SPACES_status",
                "CONFLUENCE_GET_SPACES_label",
                "CONFLUENCE_GET_SPACES_limit",
                "CONFLUENCE_GET_SPACES_start",
                "CONFLUENCE_GET_SPACES_expand",
            ],
        },
        "CONFLUENCE_GET_SPACE_CONTENTS": {
            "display_name": "Get Space Contents",
            "action_fields": [
                "CONFLUENCE_GET_SPACE_CONTENTS_spaceKey",
                "CONFLUENCE_GET_SPACE_CONTENTS_type",
                "CONFLUENCE_GET_SPACE_CONTENTS_status",
                "CONFLUENCE_GET_SPACE_CONTENTS_limit",
                "CONFLUENCE_GET_SPACE_CONTENTS_start",
            ],
        },
        "CONFLUENCE_CREATE_BLOGPOST": {
            "display_name": "Create Blog Post",
            "action_fields": [
                "CONFLUENCE_CREATE_BLOGPOST_spaceId",
                "CONFLUENCE_CREATE_BLOGPOST_title",
                "CONFLUENCE_CREATE_BLOGPOST_body",
                "CONFLUENCE_CREATE_BLOGPOST_status",
            ],
        },
        "CONFLUENCE_GET_BLOGPOST_BY_ID": {
            "display_name": "Get Blog Post By ID",
            "action_fields": [
                "CONFLUENCE_GET_BLOGPOST_BY_ID_id",
            ],
        },
        "CONFLUENCE_ADD_CONTENT_LABEL": {
            "display_name": "Add Content Label",
            "action_fields": [
                "CONFLUENCE_ADD_CONTENT_LABEL_id",
                "CONFLUENCE_ADD_CONTENT_LABEL_labels",
            ],
        },
        "CONFLUENCE_GET_LABELS_FOR_PAGE": {
            "display_name": "Get Labels For Page",
            "action_fields": [
                "CONFLUENCE_GET_LABELS_FOR_PAGE_id",
                "CONFLUENCE_GET_LABELS_FOR_PAGE_limit",
                "CONFLUENCE_GET_LABELS_FOR_PAGE_start",
            ],
        },
        "CONFLUENCE_GET_CHILD_PAGES": {
            "display_name": "Get Child Pages",
            "action_fields": [
                "CONFLUENCE_GET_CHILD_PAGES_id",
                "CONFLUENCE_GET_CHILD_PAGES_limit",
                "CONFLUENCE_GET_CHILD_PAGES_start",
            ],
        },
        "CONFLUENCE_GET_ATTACHMENTS": {
            "display_name": "Get Attachments",
            "action_fields": [
                "CONFLUENCE_GET_ATTACHMENTS_pageId",
                "CONFLUENCE_GET_ATTACHMENTS_limit",
                "CONFLUENCE_GET_ATTACHMENTS_start",
                "CONFLUENCE_GET_ATTACHMENTS_mediaType",
            ],
        },
    }

    _all_fields = {field for action_data in _actions_data.values() for field in action_data["action_fields"]}
    _bool_variables = {
        "CONFLUENCE_GET_PAGE_BY_ID_draft",
    }

    inputs = [
        *ComposioBaseComponent._base_inputs,
        # Atlassian subdomain configuration
        MessageTextInput(
            name="atlassian_subdomain",
            display_name="Atlassian Subdomain",
            info="Your Atlassian subdomain (e.g., 'cloudgeometry' for cloudgeometry.atlassian.net)",
            value="cloudgeometry",
            advanced=True,
        ),
        # Create Page fields
        MessageTextInput(
            name="CONFLUENCE_CREATE_PAGE_spaceId",
            display_name="Space ID",
            info="The ID of the space to create the page in",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_PAGE_title",
            display_name="Title",
            info="The title of the page",
            show=False,
            required=True,
        ),
        MultilineInput(
            name="CONFLUENCE_CREATE_PAGE_body",
            display_name="Body",
            info="The content body of the page (HTML or storage format)",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_PAGE_parentId",
            display_name="Parent ID",
            info="The ID of the parent page (optional)",
            show=False,
            advanced=True,
        ),
        # Get Page By ID fields
        IntInput(
            name="CONFLUENCE_GET_PAGE_BY_ID_id",
            display_name="Page ID",
            info="The ID of the page to retrieve",
            show=False,
            required=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_PAGE_BY_ID_version",
            display_name="Version",
            info="Specific version number to retrieve",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_PAGE_BY_ID_draft",
            display_name="Draft",
            info="Whether to retrieve draft version",
            show=False,
            advanced=True,
        ),
        # Get Pages fields
        MessageTextInput(
            name="CONFLUENCE_GET_PAGES_spaceId",
            display_name="Space ID",
            info="Filter by space ID",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_PAGES_title",
            display_name="Title",
            info="Filter by page title",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_PAGES_status",
            display_name="Status",
            info="Filter by status (e.g., 'current', 'archived')",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_PAGES_body_format",
            display_name="Body Format",
            info="Format of the body content to return",
            show=False,
            advanced=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_PAGES_limit",
            display_name="Limit",
            info="Maximum number of pages to return",
            show=False,
            value=25,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_PAGES_sort",
            display_name="Sort",
            info="Sort order for results",
            show=False,
            advanced=True,
        ),
        # Update Page fields
        MessageTextInput(
            name="CONFLUENCE_UPDATE_PAGE_id",
            display_name="Page ID",
            info="The ID of the page to update",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_UPDATE_PAGE_title",
            display_name="Title",
            info="New title for the page",
            show=False,
            required=True,
        ),
        MultilineInput(
            name="CONFLUENCE_UPDATE_PAGE_body",
            display_name="Body",
            info="New content body for the page",
            show=False,
        ),
        IntInput(
            name="CONFLUENCE_UPDATE_PAGE_version_number",
            display_name="Version Number",
            info="Current version number (required for update)",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_UPDATE_PAGE_spaceId",
            display_name="Space ID",
            info="Space ID (optional, for moving page)",
            show=False,
            advanced=True,
        ),
        # Delete Page fields
        MessageTextInput(
            name="CONFLUENCE_DELETE_PAGE_id",
            display_name="Page ID",
            info="The ID of the page to delete",
            show=False,
            required=True,
        ),
        # Search Content fields
        MessageTextInput(
            name="CONFLUENCE_SEARCH_CONTENT_query",
            display_name="Query",
            info="Search query string (CQL or text)",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_SEARCH_CONTENT_spaceKey",
            display_name="Space Key",
            info="Filter by space key",
            show=False,
        ),
        IntInput(
            name="CONFLUENCE_SEARCH_CONTENT_limit",
            display_name="Limit",
            info="Maximum number of results to return",
            show=False,
            value=25,
        ),
        IntInput(
            name="CONFLUENCE_SEARCH_CONTENT_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_SEARCH_CONTENT_expand",
            display_name="Expand",
            info="Comma-separated list of properties to expand",
            show=False,
            advanced=True,
        ),
        # Create Space fields
        MessageTextInput(
            name="CONFLUENCE_CREATE_SPACE_key",
            display_name="Key",
            info="Unique key for the space (e.g., 'DEV', 'DOCS')",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_SPACE_name",
            display_name="Name",
            info="Display name for the space",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_SPACE_description",
            display_name="Description",
            info="Description of the space",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_SPACE_type",
            display_name="Type",
            info="Type of space ('global' or 'personal')",
            show=False,
            advanced=True,
        ),
        # Get Space By ID fields
        MessageTextInput(
            name="CONFLUENCE_GET_SPACE_BY_ID_id",
            display_name="Space ID",
            info="The ID of the space to retrieve",
            show=False,
            required=True,
        ),
        # Get Spaces fields
        MessageTextInput(
            name="CONFLUENCE_GET_SPACES_spaceKey",
            display_name="Space Key",
            info="Filter by space key",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACES_type",
            display_name="Type",
            info="Filter by space type",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACES_status",
            display_name="Status",
            info="Filter by space status",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACES_label",
            display_name="Label",
            info="Filter by space label",
            show=False,
        ),
        IntInput(
            name="CONFLUENCE_GET_SPACES_limit",
            display_name="Limit",
            info="Maximum number of spaces to return",
            show=False,
            value=25,
        ),
        IntInput(
            name="CONFLUENCE_GET_SPACES_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACES_expand",
            display_name="Expand",
            info="Comma-separated list of properties to expand",
            show=False,
            advanced=True,
        ),
        # Get Space Contents fields
        MessageTextInput(
            name="CONFLUENCE_GET_SPACE_CONTENTS_spaceKey",
            display_name="Space Key",
            info="The key of the space",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACE_CONTENTS_type",
            display_name="Type",
            info="Filter by content type ('page', 'blogpost')",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_SPACE_CONTENTS_status",
            display_name="Status",
            info="Filter by content status",
            show=False,
        ),
        IntInput(
            name="CONFLUENCE_GET_SPACE_CONTENTS_limit",
            display_name="Limit",
            info="Maximum number of items to return",
            show=False,
            value=25,
        ),
        IntInput(
            name="CONFLUENCE_GET_SPACE_CONTENTS_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        # Create Blog Post fields
        MessageTextInput(
            name="CONFLUENCE_CREATE_BLOGPOST_spaceId",
            display_name="Space ID",
            info="The ID of the space to create the blog post in",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_BLOGPOST_title",
            display_name="Title",
            info="The title of the blog post",
            show=False,
            required=True,
        ),
        MultilineInput(
            name="CONFLUENCE_CREATE_BLOGPOST_body",
            display_name="Body",
            info="The content body of the blog post",
            show=False,
        ),
        MessageTextInput(
            name="CONFLUENCE_CREATE_BLOGPOST_status",
            display_name="Status",
            info="Status of the blog post ('current' or 'draft')",
            show=False,
            value="current",
        ),
        # Get Blog Post By ID fields
        MessageTextInput(
            name="CONFLUENCE_GET_BLOGPOST_BY_ID_id",
            display_name="Blog Post ID",
            info="The ID of the blog post to retrieve",
            show=False,
            required=True,
        ),
        # Add Content Label fields
        MessageTextInput(
            name="CONFLUENCE_ADD_CONTENT_LABEL_id",
            display_name="Content ID",
            info="The ID of the content (page or blog post) to label",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_ADD_CONTENT_LABEL_labels",
            display_name="Labels",
            info="Comma-separated list of labels to add",
            show=False,
            required=True,
        ),
        # Get Labels For Page fields
        MessageTextInput(
            name="CONFLUENCE_GET_LABELS_FOR_PAGE_id",
            display_name="Page ID",
            info="The ID of the page to get labels for",
            show=False,
            required=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_LABELS_FOR_PAGE_limit",
            display_name="Limit",
            info="Maximum number of labels to return",
            show=False,
            value=25,
            advanced=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_LABELS_FOR_PAGE_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        # Get Child Pages fields
        MessageTextInput(
            name="CONFLUENCE_GET_CHILD_PAGES_id",
            display_name="Page ID",
            info="The ID of the parent page",
            show=False,
            required=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_CHILD_PAGES_limit",
            display_name="Limit",
            info="Maximum number of child pages to return",
            show=False,
            value=25,
        ),
        IntInput(
            name="CONFLUENCE_GET_CHILD_PAGES_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        # Get Attachments fields
        MessageTextInput(
            name="CONFLUENCE_GET_ATTACHMENTS_pageId",
            display_name="Page ID",
            info="The ID of the page to get attachments from",
            show=False,
            required=True,
        ),
        IntInput(
            name="CONFLUENCE_GET_ATTACHMENTS_limit",
            display_name="Limit",
            info="Maximum number of attachments to return",
            show=False,
            value=25,
        ),
        IntInput(
            name="CONFLUENCE_GET_ATTACHMENTS_start",
            display_name="Start",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        MessageTextInput(
            name="CONFLUENCE_GET_ATTACHMENTS_mediaType",
            display_name="Media Type",
            info="Filter by media type",
            show=False,
            advanced=True,
        ),
    ]

    def _initiate_default_connection(self, entity, app: str) -> str:
        """Override to pass Atlassian subdomain for OAuth connection."""
        subdomain = getattr(self, "atlassian_subdomain", "cloudgeometry")
        connection = entity.initiate_connection(
            app_name=app,
            use_composio_auth=True,
            force_new_integration=True,
            integration_params={"subdomain": subdomain},
        )
        return connection.redirectUrl

    def execute_action(self):
        """Execute action and return response."""
        # Validate action is selected
        if not self.action or self.action == "disabled" or (isinstance(self.action, list) and not self.action):
            msg = "Please select an action before executing. Connect your Composio account and choose an action from the dropdown."
            raise ValueError(msg)

        toolset = self._build_wrapper()

        try:
            self._build_action_maps()
            # Get the display name from the action list
            display_name = self.action[0]["name"] if isinstance(self.action, list) and self.action else self.action
            # Use the display_to_key_map to get the action key
            action_key = self._display_to_key_map.get(display_name)
            if not action_key:
                msg = f"Invalid action: {display_name}. Please select a valid action from the dropdown."
                raise ValueError(msg)

            enum_name = getattr(Action, action_key)
            params = {}
            if action_key in self._actions_data:
                for field in self._actions_data[action_key]["action_fields"]:
                    value = getattr(self, field, None)

                    if value is None or value == "":
                        continue

                    # Handle comma-separated lists for labels
                    if field.endswith("_labels") and value:
                        value = [item.strip() for item in value.split(",")]

                    if field in self._bool_variables:
                        value = bool(value)

                    param_name = field.replace(action_key + "_", "")
                    params[param_name] = value

            result = toolset.execute_action(
                action=enum_name,
                params=params,
            )
            if not result.get("successful"):
                error_message = result.get("error", "Unknown error")
                return {"error": str(error_message), "successful": False}

            result_data = result.get("data", {})
            if isinstance(result_data.get("details"), list):
                return result_data.get("details")
            return result_data

        except Exception as e:
            logger.error(f"Error executing Confluence action: {e}")
            display_name = self.action[0]["name"] if isinstance(self.action, list) and self.action else str(self.action)
            msg = f"Failed to execute {display_name}: {e!s}"
            raise ValueError(msg) from e

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        return super().update_build_config(build_config, field_value, field_name)

    def set_default_tools(self):
        self._default_tools = {
            self.sanitize_action_name("CONFLUENCE_CREATE_PAGE").replace(" ", "-"),
            self.sanitize_action_name("CONFLUENCE_SEARCH_CONTENT").replace(" ", "-"),
        }
