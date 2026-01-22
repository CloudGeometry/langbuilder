# Standard library imports
from collections.abc import Sequence
from typing import Any

import httpx
from composio import Action, App
from composio.client.collections import AppAuthScheme
from composio.client.exceptions import NoItemsFound
from composio.exceptions import ApiKeyError
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# Third-party imports
from composio_langchain import ComposioToolSet

# Local imports
from langbuilder.base.langchain_utilities.model import LCToolComponent
from langbuilder.field_typing import Tool
from langbuilder.inputs.inputs import (
    AuthInput,
    ConnectionInput,
    DropdownInput,
    MessageTextInput,
    SecretStrInput,
    SortableListInput,
)
from langbuilder.io import Output
from langbuilder.logging import logger
from langbuilder.schema.data import Data

# Default enabled tools - can be dynamically fetched from API
DEFAULT_ENABLED_TOOLS = [
    "confluence",
    "discord",
    "dropbox",
    "github",
    "gmail",
    "googlecalendar",
    "linkedin",
    "notion",
    "outlook",
    "slack",
    "youtube",
]


class ComposioAPIComponent(LCToolComponent):
    """Composio API component for integrating Composio toolset with agents.

    This component supports multiple authentication schemes:
    - OAuth2: Redirects to external authentication flow
    - API_KEY: Uses credentials field for API key
    - BASIC: Uses username/password fields

    The component dynamically shows/hides fields based on the selected app's
    authentication requirements.
    """

    display_name: str = "Composio Tools"
    description: str = "Use Composio toolset to run actions with your agent"
    name = "ComposioAPI"
    icon = "Composio"
    documentation: str = "https://docs.composio.dev"

    inputs = [
        # Basic configuration inputs
        MessageTextInput(
            name="entity_id",
            display_name="Entity ID",
            value="default",
            advanced=True,
            info="Unique identifier for the user/entity. Use 'default' for single-user setups.",
            tool_mode=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="Composio API Key",
            required=True,
            info="Your Composio API key from https://app.composio.dev/settings",
            real_time_refresh=True,
            # No default value per LangBuilder patterns - use env var fallback
        ),
        # App/Tool selection with connection management
        DropdownInput(
            name="app_name",
            display_name="App",
            placeholder="Select an app...",
            options=[],
            value="",
            info="The Composio app to connect and use",
            real_time_refresh=True,
            tool_mode=True,
        ),
        # Auth status and link
        AuthInput(
            name="auth_link",
            value="",
            auth_tooltip="Please insert a valid Composio API Key and select an app.",
        ),
        # Credentials for API_KEY auth scheme
        SecretStrInput(
            name="credentials",
            display_name="Credentials",
            info="API key or credentials for the selected app (for API_KEY auth)",
            show=False,
            real_time_refresh=True,
            # No default value per LangBuilder patterns
        ),
        # Username/Password for BASIC auth scheme
        MessageTextInput(
            name="auth_username",
            display_name="Username",
            info="Username for basic authentication",
            show=False,
            tool_mode=True,
        ),
        SecretStrInput(
            name="auth_password",
            display_name="Password",
            info="Password for basic authentication",
            show=False,
            # No default value per LangBuilder patterns
        ),
        # Connection status display
        MessageTextInput(
            name="connection_status",
            display_name="Connection Status",
            info="Current connection status",
            show=False,
            advanced=True,
        ),
        # Actions selection
        SortableListInput(
            name="actions",
            display_name="Actions",
            placeholder="Select action",
            helper_text="Please connect to an app before selecting actions.",
            helper_text_metadata={"icon": "OctagonAlert", "variant": "destructive"},
            options=[],
            value="",
            info="The actions to execute",
            limit=1,
            show=False,
            real_time_refresh=True,
            tool_mode=True,
        ),
        # Legacy tool_name field for backwards compatibility
        ConnectionInput(
            name="tool_name",
            display_name="Tool Name (Legacy)",
            placeholder="Select a tool...",
            button_metadata={"icon": "unplug", "variant": "destructive"},
            options=[],
            search_category=[],
            value="",
            connection_link="",
            info="Legacy tool selection - use App dropdown instead",
            real_time_refresh=True,
            show=False,
            advanced=True,
        ),
    ]

    # Uses default LCToolComponent outputs:
    # Output(name="api_run_model", display_name="Data", method="run_model")
    # Output(name="api_build_tool", display_name="Tool", method="build_tool")

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def sanitize_action_name(self, action_name: str) -> str:
        """Convert action name to display format."""
        return action_name.replace("_", " ").title()

    def desanitize_action_name(self, action_name: str) -> str:
        """Convert display name back to action key."""
        return action_name.replace(" ", "_").upper()

    def _build_wrapper(self) -> ComposioToolSet:
        """Build the Composio toolset wrapper.

        Returns:
            ComposioToolSet: The initialized toolset.

        Raises:
            ValueError: If the API key is not found or invalid.
        """
        try:
            if not self.api_key:
                msg = "Composio API Key is required"
                raise ValueError(msg)
            return ComposioToolSet(api_key=self.api_key, entity_id=self.entity_id)
        except (ValueError, ApiKeyError) as e:
            logger.error(f"Error building Composio wrapper: {e}")
            msg = "Please provide a valid Composio API Key in the component settings"
            raise ValueError(msg) from e

    # -------------------------------------------------------------------------
    # Authentication Methods
    # -------------------------------------------------------------------------

    def _get_auth_scheme(self, app_name: str) -> AppAuthScheme | None:
        """Get the primary authentication scheme for an app.

        Args:
            app_name: The name of the Composio app.

        Returns:
            The auth scheme or None if not found.
        """
        try:
            toolset = self._build_wrapper()
            return toolset.get_auth_scheme_for_app(app=app_name.lower())
        except (ValueError, ConnectionError, NoItemsFound) as e:
            logger.error(f"Error getting auth scheme for {app_name}: {e}")
            return None

    def _get_oauth_apps(self) -> list[str]:
        """Fetch list of OAuth-enabled apps from Composio API.

        Returns:
            List of app names that support OAuth authentication.
        """
        try:
            url = "https://backend.composio.dev/api/v1/apps"
            headers = {"x-api-key": self.api_key}
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                return [
                    app["key"]
                    for app in data.get("items", [])
                    if app.get("auth_schemes") and any(s.get("auth_mode") == "OAUTH2" for s in app["auth_schemes"])
                ]
        except Exception as e:
            logger.error(f"Error fetching OAuth apps: {e}")
            return []

    def _check_for_authorization(self, app_name: str) -> bool:
        """Check if the entity is already authorized for the app.

        Args:
            app_name: The name of the app to check.

        Returns:
            True if authorized, False otherwise.
        """
        try:
            toolset = self._build_wrapper()
            entity = toolset.client.get_entity(id=self.entity_id)
            entity.get_connection(app=app_name)
            return True
        except (NoItemsFound, ValueError, ConnectionError):
            return False

    def _get_connected_app_names_for_entity(self) -> list[str]:
        """Get list of connected app names for the current entity.

        Returns:
            List of lowercase app names that are connected.
        """
        try:
            toolset = self._build_wrapper()
            connected_apps = toolset.get_connected_accounts()
            return [app.appName.lower() for app in connected_apps if app.status == "ACTIVE"]
        except (ValueError, ConnectionError) as e:
            logger.error(f"Error getting connected apps: {e}")
            return []

    def _initiate_default_connection(self, app_name: str) -> str:
        """Initiate OAuth connection and return redirect URL.

        Args:
            app_name: The name of the app to connect.

        Returns:
            The OAuth redirect URL.
        """
        try:
            toolset = self._build_wrapper()
            entity = toolset.client.get_entity(id=self.entity_id)
            connection = entity.initiate_connection(
                app_name=app_name,
                use_composio_auth=True,
                force_new_integration=True,
            )
            return connection.redirectUrl
        except Exception as e:
            logger.error(f"Error initiating connection for {app_name}: {e}")
            msg = f"Failed to initiate OAuth connection: {e}"
            raise ValueError(msg) from e

    def _handle_auth_by_scheme(
        self, build_config: dict, app_name: str, auth_scheme: AppAuthScheme | None
    ) -> dict:
        """Handle authentication based on the auth scheme.

        Args:
            build_config: The current build configuration.
            app_name: The name of the app.
            auth_scheme: The auth scheme for the app.

        Returns:
            Updated build configuration.
        """
        # Reset auth-related fields
        build_config["credentials"]["show"] = False
        build_config["auth_username"]["show"] = False
        build_config["auth_password"]["show"] = False

        if not auth_scheme:
            build_config["auth_link"]["value"] = "error"
            build_config["auth_link"]["auth_tooltip"] = "Could not determine authentication method"
            return build_config

        auth_mode = auth_scheme.auth_mode

        if auth_mode == "OAUTH2":
            # OAuth2 - show auth link for redirect
            try:
                redirect_url = self._initiate_default_connection(app_name)
                build_config["auth_link"]["value"] = redirect_url
                build_config["auth_link"]["auth_tooltip"] = "Click to connect via OAuth"
            except ValueError as e:
                build_config["auth_link"]["value"] = "error"
                build_config["auth_link"]["auth_tooltip"] = str(e)

        elif auth_mode == "API_KEY":
            # API Key auth - show credentials field
            build_config["credentials"]["show"] = True
            build_config["auth_link"]["value"] = ""
            build_config["auth_link"]["auth_tooltip"] = "Enter your API key in the Credentials field"

        elif auth_mode == "BASIC":
            # Basic auth - show username/password fields
            build_config["auth_username"]["show"] = True
            build_config["auth_password"]["show"] = True
            build_config["auth_link"]["value"] = ""
            build_config["auth_link"]["auth_tooltip"] = "Enter username and password"

        else:
            # Unknown auth mode - try OAuth as fallback
            try:
                redirect_url = self._initiate_default_connection(app_name)
                build_config["auth_link"]["value"] = redirect_url
                build_config["auth_link"]["auth_tooltip"] = f"Auth mode: {auth_mode} - trying OAuth"
            except ValueError:
                build_config["auth_link"]["value"] = "error"
                build_config["auth_link"]["auth_tooltip"] = f"Unsupported auth mode: {auth_mode}"

        return build_config

    # -------------------------------------------------------------------------
    # Build Config Update Methods
    # -------------------------------------------------------------------------

    def _update_app_options(self, build_config: dict) -> dict:
        """Update the app dropdown options.

        Args:
            build_config: The current build configuration.

        Returns:
            Updated build configuration with app options.
        """
        # Use default enabled tools, or fetch dynamically
        app_options = DEFAULT_ENABLED_TOOLS

        # Try to get dynamic list from API if enabled
        try:
            toolset = self._build_wrapper()
            all_apps = toolset.client.apps.get()
            if all_apps:
                app_options = sorted([app.key for app in all_apps])
        except (ValueError, ConnectionError, ApiKeyError) as e:
            logger.debug(f"Using default app list, could not fetch from API: {e}")

        build_config["app_name"]["options"] = app_options
        return build_config

    def _update_actions_for_app(self, build_config: dict, app_name: str) -> dict:
        """Update actions dropdown for the selected app.

        Args:
            build_config: The current build configuration.
            app_name: The selected app name.

        Returns:
            Updated build configuration with action options.
        """
        try:
            # Get all available actions for this app
            all_actions = list(Action.all())
            app_actions = sorted(
                [action for action in all_actions if action.app.lower() == app_name.lower()],
                key=lambda x: x.name,
            )

            build_config["actions"]["options"] = [
                {"name": self.sanitize_action_name(action.name), "metadata": action.name}
                for action in app_actions
            ]
            build_config["actions"]["show"] = True
            build_config["actions"]["helper_text"] = ""
            build_config["actions"]["helper_text_metadata"] = {"icon": "Check", "variant": "success"}

        except Exception as e:
            logger.error(f"Error fetching actions for {app_name}: {e}")
            build_config["actions"]["options"] = []
            build_config["actions"]["helper_text"] = f"Error loading actions: {e}"
            build_config["actions"]["helper_text_metadata"] = {"icon": "OctagonAlert", "variant": "destructive"}

        return build_config

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        """Update build configuration based on field changes.

        This method handles:
        - API key changes: Update app options
        - App selection: Check auth, show appropriate fields
        - Auth link clicks: Handle OAuth flow or disconnection
        - Credentials submission: Handle API_KEY/BASIC auth

        Args:
            build_config: The current build configuration.
            field_value: The new field value.
            field_name: The name of the field that changed.

        Returns:
            Updated build configuration.
        """
        # Handle tool_mode toggle
        if field_name == "tool_mode":
            build_config["app_name"]["show"] = not field_value
            build_config["actions"]["show"] = False
            return build_config

        # Handle API key changes
        if field_name == "api_key":
            if not field_value:
                # Reset everything when API key is cleared
                build_config["app_name"]["options"] = []
                build_config["app_name"]["value"] = ""
                build_config["auth_link"]["value"] = ""
                build_config["auth_link"]["auth_tooltip"] = "Please insert a valid Composio API Key."
                build_config["actions"]["show"] = False
                build_config["actions"]["options"] = []
                build_config["actions"]["value"] = ""
                build_config["credentials"]["show"] = False
                build_config["auth_username"]["show"] = False
                build_config["auth_password"]["show"] = False
                return build_config

            # Update app options when API key is provided
            return self._update_app_options(build_config)

        # Ensure we have an API key for subsequent operations
        if not hasattr(self, "api_key") or not self.api_key:
            return build_config

        # Populate app options if empty
        if not build_config["app_name"]["options"]:
            build_config = self._update_app_options(build_config)

        # Handle app selection
        if field_name == "app_name" and field_value:
            app_name = field_value.lower() if isinstance(field_value, str) else str(field_value).lower()

            # Reset auth fields
            build_config["actions"]["show"] = False
            build_config["actions"]["options"] = []
            build_config["actions"]["value"] = ""

            # Check if already connected
            if self._check_for_authorization(app_name):
                build_config["auth_link"]["value"] = "validated"
                build_config["auth_link"]["auth_tooltip"] = "Connected - Click to disconnect"
                build_config = self._update_actions_for_app(build_config, app_name)
            else:
                # Get auth scheme and set up appropriate fields
                auth_scheme = self._get_auth_scheme(app_name)
                build_config = self._handle_auth_by_scheme(build_config, app_name, auth_scheme)

            return build_config

        # Handle auth link interactions (connect/disconnect)
        if field_name == "auth_link" and field_value == "disconnect":
            try:
                app_name = getattr(self, "app_name", "").lower()
                if app_name:
                    toolset = self._build_wrapper()
                    entity = toolset.client.get_entity(id=self.entity_id)
                    connection = entity.get_connection(app=app_name)
                    entity.client.integrations.remove(id=connection.integrationId)

                    # Re-initiate connection
                    auth_scheme = self._get_auth_scheme(app_name)
                    build_config = self._handle_auth_by_scheme(build_config, app_name, auth_scheme)
                    build_config["actions"]["show"] = False
                    build_config["actions"]["options"] = []
                    build_config["actions"]["value"] = ""
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
                build_config["auth_link"]["value"] = "error"
                build_config["auth_link"]["auth_tooltip"] = f"Disconnect failed: {e}"
            return build_config

        # Handle auth link validation (after OAuth callback)
        if field_name == "auth_link" and field_value == "validated":
            app_name = getattr(self, "app_name", "").lower()
            if app_name:
                build_config = self._update_actions_for_app(build_config, app_name)
            return build_config

        # Handle credentials submission (for API_KEY auth)
        if field_name == "credentials" and field_value:
            app_name = getattr(self, "app_name", "").lower()
            if app_name:
                try:
                    toolset = self._build_wrapper()
                    entity = toolset.client.get_entity(id=self.entity_id)
                    # Create connection with API key
                    entity.initiate_connection(
                        app_name=app_name,
                        auth_mode="API_KEY",
                        auth_config={"api_key": field_value},
                    )
                    build_config["auth_link"]["value"] = "validated"
                    build_config["auth_link"]["auth_tooltip"] = "Connected - Click to disconnect"
                    build_config = self._update_actions_for_app(build_config, app_name)
                except Exception as e:
                    logger.error(f"Error connecting with API key: {e}")
                    build_config["auth_link"]["value"] = "error"
                    build_config["auth_link"]["auth_tooltip"] = f"Connection failed: {e}"
            return build_config

        return build_config

    # -------------------------------------------------------------------------
    # Output Methods
    # -------------------------------------------------------------------------

    def run_model(self) -> Data:
        """Execute the selected action and return results as Data.

        Returns:
            Data object containing the action results.

        Raises:
            ValueError: If no action is selected or execution fails.
        """
        if not self.actions or self.actions == "disabled" or (isinstance(self.actions, list) and not self.actions):
            msg = "Please select an action before executing. Connect your Composio account, select an app, and choose an action from the dropdown."
            raise ValueError(msg)

        try:
            toolset = self._build_wrapper()

            # Get the action name from the selection
            action_display = self.actions[0]["name"] if isinstance(self.actions, list) else self.actions
            action_name = self.desanitize_action_name(action_display)

            # Execute the action
            result = toolset.execute_action(
                action=getattr(Action, action_name),
                params={},
            )

            if not result.get("successful"):
                error_msg = result.get("error", "Unknown error")
                return Data(data={"error": str(error_msg), "successful": False})

            self.status = f"Action {action_display} executed successfully"
            return Data(data=result.get("data", {}))

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return Data(data={"error": str(e), "successful": False})

    async def _get_tools(self) -> list[Tool]:
        """Override to return properly named tool with tags.

        This ensures the tool has a unique name (not 'run_model') for agent tool selection.
        """
        tool = self.build_tool()
        if tool and not getattr(tool, "tags", None):
            tool.tags = [tool.name]
        return [tool] if tool else []

    def build_tool(self) -> Tool:
        """Build Composio tool for Agent use with proper naming and tags.

        Returns:
            Tool: A StructuredTool configured for agent use.

        Raises:
            ValueError: If no actions are selected or tool building fails.
        """
        # Define input schema for the tool
        class ComposioToolInput(BaseModel):
            app_name: str = Field(default="", description="The Composio app to use (e.g., github, slack, gmail)")
            action_name: str = Field(default="", description="The action to execute on the app")
            params: str = Field(default="{}", description="JSON string of parameters for the action")

        def _execute_composio_action(
            app_name: str = "",
            action_name: str = "",
            params: str = "{}",
        ) -> str:
            """Execute a Composio action."""
            import json

            try:
                # Use provided values or fall back to component attributes
                target_app = app_name or getattr(self, "app_name", "")
                target_action = action_name

                # If no action provided, try to get from component
                if not target_action and hasattr(self, "actions") and self.actions:
                    if isinstance(self.actions, list) and self.actions:
                        target_action = self.actions[0].get("metadata", self.actions[0].get("name", ""))
                    else:
                        target_action = str(self.actions)

                if not target_action:
                    return "Error: No action specified"

                # Parse params
                try:
                    action_params = json.loads(params) if params else {}
                except json.JSONDecodeError:
                    action_params = {}

                # Build toolset and execute
                toolset = self._build_wrapper()
                action_key = self.desanitize_action_name(target_action)

                result = toolset.execute_action(
                    action=getattr(Action, action_key),
                    params=action_params,
                )

                if not result.get("successful"):
                    return f"Error: {result.get('error', 'Unknown error')}"

                return f"Success: {json.dumps(result.get('data', {}), indent=2)}"

            except Exception as e:
                logger.error(f"Error executing Composio action: {e}")
                return f"Error: {e!s}"

        # Create the tool with unique name and tags
        tool_name = "composio_execute_action"
        tool = StructuredTool.from_function(
            name=tool_name,
            description=(
                "Execute actions on connected apps via Composio. "
                "Supports GitHub, Slack, Gmail, Google Calendar, and many more integrations. "
                "Use this to interact with external services on behalf of the user."
            ),
            args_schema=ComposioToolInput,
            func=_execute_composio_action,
            return_direct=False,
            tags=[tool_name],
        )

        self.status = "Composio tool created"
        return tool
