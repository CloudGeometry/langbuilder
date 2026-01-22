from typing import Any

from composio import Action

from langbuilder.base.composio.composio_base import ComposioBaseComponent
from langbuilder.inputs import (
    BoolInput,
    IntInput,
    MessageTextInput,
    MultilineInput,
)
from langbuilder.logging import logger


class ComposioJiraAPIComponent(ComposioBaseComponent):
    """Jira API component for interacting with Jira services via Composio."""

    display_name: str = "Jira"
    description: str = "Jira API - Create, update, and manage issues, projects, and sprints"
    icon = "Jira"
    documentation: str = "https://docs.composio.dev/toolkits/jira"
    app_name = "jira"

    # Atlassian subdomain for authentication
    atlassian_subdomain: str = "cloudgeometry"

    _actions_data: dict = {
        "JIRA_CREATE_ISSUE": {
            "display_name": "Create Issue",
            "action_fields": [
                "JIRA_CREATE_ISSUE_project_key",
                "JIRA_CREATE_ISSUE_summary",
                "JIRA_CREATE_ISSUE_description",
                "JIRA_CREATE_ISSUE_issue_type",
                "JIRA_CREATE_ISSUE_priority",
                "JIRA_CREATE_ISSUE_assignee",
                "JIRA_CREATE_ISSUE_labels",
                "JIRA_CREATE_ISSUE_due_date",
            ],
        },
        "JIRA_GET_ISSUE": {
            "display_name": "Get Issue",
            "action_fields": [
                "JIRA_GET_ISSUE_issue_key",
                "JIRA_GET_ISSUE_fields",
                "JIRA_GET_ISSUE_expand",
            ],
        },
        "JIRA_EDIT_ISSUE": {
            "display_name": "Edit Issue",
            "action_fields": [
                "JIRA_EDIT_ISSUE_issue_id_or_key",
                "JIRA_EDIT_ISSUE_summary",
                "JIRA_EDIT_ISSUE_description",
                "JIRA_EDIT_ISSUE_priority_id_or_name",
                "JIRA_EDIT_ISSUE_assignee",
                "JIRA_EDIT_ISSUE_labels",
                "JIRA_EDIT_ISSUE_due_date",
                "JIRA_EDIT_ISSUE_notify_users",
            ],
        },
        "JIRA_DELETE_ISSUE": {
            "display_name": "Delete Issue",
            "action_fields": [
                "JIRA_DELETE_ISSUE_issue_id_or_key",
                "JIRA_DELETE_ISSUE_delete_subtasks",
            ],
        },
        "JIRA_SEARCH_ISSUES": {
            "display_name": "Search Issues",
            "action_fields": [
                "JIRA_SEARCH_ISSUES_jql",
                "JIRA_SEARCH_ISSUES_project_key",
                "JIRA_SEARCH_ISSUES_assignee",
                "JIRA_SEARCH_ISSUES_status_id_or_name",
                "JIRA_SEARCH_ISSUES_issue_type_id_or_name",
                "JIRA_SEARCH_ISSUES_labels",
                "JIRA_SEARCH_ISSUES_text_search",
                "JIRA_SEARCH_ISSUES_max_results",
                "JIRA_SEARCH_ISSUES_fields",
            ],
        },
        "JIRA_ADD_COMMENT": {
            "display_name": "Add Comment",
            "action_fields": [
                "JIRA_ADD_COMMENT_issue_id_or_key",
                "JIRA_ADD_COMMENT_comment",
                "JIRA_ADD_COMMENT_visibility_type",
                "JIRA_ADD_COMMENT_visibility_value",
            ],
        },
        "JIRA_TRANSITION_ISSUE": {
            "display_name": "Transition Issue",
            "action_fields": [
                "JIRA_TRANSITION_ISSUE_issue_id_or_key",
                "JIRA_TRANSITION_ISSUE_transition_id_or_name",
                "JIRA_TRANSITION_ISSUE_comment",
                "JIRA_TRANSITION_ISSUE_resolution",
                "JIRA_TRANSITION_ISSUE_assignee",
            ],
        },
        "JIRA_ASSIGN_ISSUE": {
            "display_name": "Assign Issue",
            "action_fields": [
                "JIRA_ASSIGN_ISSUE_issue_id_or_key",
                "JIRA_ASSIGN_ISSUE_account_id",
                "JIRA_ASSIGN_ISSUE_assignee_name",
            ],
        },
        "JIRA_GET_ALL_PROJECTS": {
            "display_name": "Get All Projects",
            "action_fields": [
                "JIRA_GET_ALL_PROJECTS_maxResults",
                "JIRA_GET_ALL_PROJECTS_startAt",
                "JIRA_GET_ALL_PROJECTS_expand",
            ],
        },
        "JIRA_LIST_SPRINTS": {
            "display_name": "List Sprints",
            "action_fields": [
                "JIRA_LIST_SPRINTS_board_id",
                "JIRA_LIST_SPRINTS_state",
                "JIRA_LIST_SPRINTS_max_results",
                "JIRA_LIST_SPRINTS_start_at",
            ],
        },
        "JIRA_CREATE_SPRINT": {
            "display_name": "Create Sprint",
            "action_fields": [
                "JIRA_CREATE_SPRINT_name",
                "JIRA_CREATE_SPRINT_origin_board_id",
                "JIRA_CREATE_SPRINT_goal",
                "JIRA_CREATE_SPRINT_start_date",
                "JIRA_CREATE_SPRINT_end_date",
            ],
        },
        "JIRA_FIND_USERS": {
            "display_name": "Find Users",
            "action_fields": [
                "JIRA_FIND_USERS_query",
                "JIRA_FIND_USERS_account_id",
                "JIRA_FIND_USERS_max_results",
                "JIRA_FIND_USERS_start_at",
            ],
        },
    }

    _all_fields = {field for action_data in _actions_data.values() for field in action_data["action_fields"]}
    _bool_variables = {
        "JIRA_DELETE_ISSUE_delete_subtasks",
        "JIRA_EDIT_ISSUE_notify_users",
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
        # Create Issue fields
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_project_key",
            display_name="Project Key",
            info="The project key (e.g., 'PROJ', 'DEV')",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_summary",
            display_name="Summary",
            info="Brief summary of the issue",
            show=False,
            required=True,
        ),
        MultilineInput(
            name="JIRA_CREATE_ISSUE_description",
            display_name="Description",
            info="Detailed description of the issue",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_issue_type",
            display_name="Issue Type",
            info="Type of issue (e.g., 'Bug', 'Task', 'Story', 'Epic')",
            show=False,
            value="Task",
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_priority",
            display_name="Priority",
            info="Priority level (e.g., 'Highest', 'High', 'Medium', 'Low', 'Lowest')",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_assignee",
            display_name="Assignee",
            info="Account ID of the user to assign the issue to",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_labels",
            display_name="Labels",
            info="Comma-separated list of labels",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_CREATE_ISSUE_due_date",
            display_name="Due Date",
            info="Due date in YYYY-MM-DD format",
            show=False,
            advanced=True,
        ),
        # Get Issue fields
        MessageTextInput(
            name="JIRA_GET_ISSUE_issue_key",
            display_name="Issue Key",
            info="The issue key (e.g., 'PROJ-123')",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_GET_ISSUE_fields",
            display_name="Fields",
            info="Comma-separated list of fields to return",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_GET_ISSUE_expand",
            display_name="Expand",
            info="Comma-separated list of fields to expand",
            show=False,
            advanced=True,
        ),
        # Edit Issue fields
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_issue_id_or_key",
            display_name="Issue ID or Key",
            info="The issue ID or key to edit",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_summary",
            display_name="Summary",
            info="New summary for the issue",
            show=False,
        ),
        MultilineInput(
            name="JIRA_EDIT_ISSUE_description",
            display_name="Description",
            info="New description for the issue",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_priority_id_or_name",
            display_name="Priority",
            info="New priority level",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_assignee",
            display_name="Assignee",
            info="New assignee account ID",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_labels",
            display_name="Labels",
            info="Comma-separated list of new labels",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_EDIT_ISSUE_due_date",
            display_name="Due Date",
            info="New due date in YYYY-MM-DD format",
            show=False,
            advanced=True,
        ),
        BoolInput(
            name="JIRA_EDIT_ISSUE_notify_users",
            display_name="Notify Users",
            info="Whether to notify users of the change",
            show=False,
            value=True,
            advanced=True,
        ),
        # Delete Issue fields
        MessageTextInput(
            name="JIRA_DELETE_ISSUE_issue_id_or_key",
            display_name="Issue ID or Key",
            info="The issue ID or key to delete",
            show=False,
            required=True,
        ),
        BoolInput(
            name="JIRA_DELETE_ISSUE_delete_subtasks",
            display_name="Delete Subtasks",
            info="Whether to delete subtasks as well",
            show=False,
            value=False,
        ),
        # Search Issues fields
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_jql",
            display_name="JQL Query",
            info="JQL query string for advanced search",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_project_key",
            display_name="Project Key",
            info="Filter by project key",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_assignee",
            display_name="Assignee",
            info="Filter by assignee account ID",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_status_id_or_name",
            display_name="Status",
            info="Filter by status (e.g., 'To Do', 'In Progress', 'Done')",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_issue_type_id_or_name",
            display_name="Issue Type",
            info="Filter by issue type",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_labels",
            display_name="Labels",
            info="Filter by labels (comma-separated)",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_text_search",
            display_name="Text Search",
            info="Full-text search query",
            show=False,
        ),
        IntInput(
            name="JIRA_SEARCH_ISSUES_max_results",
            display_name="Max Results",
            info="Maximum number of results to return",
            show=False,
            value=50,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_SEARCH_ISSUES_fields",
            display_name="Fields",
            info="Comma-separated list of fields to return",
            show=False,
            advanced=True,
        ),
        # Add Comment fields
        MessageTextInput(
            name="JIRA_ADD_COMMENT_issue_id_or_key",
            display_name="Issue ID or Key",
            info="The issue ID or key to comment on",
            show=False,
            required=True,
        ),
        MultilineInput(
            name="JIRA_ADD_COMMENT_comment",
            display_name="Comment",
            info="The comment text",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_ADD_COMMENT_visibility_type",
            display_name="Visibility Type",
            info="Visibility type ('group' or 'role')",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_ADD_COMMENT_visibility_value",
            display_name="Visibility Value",
            info="The group name or role name for visibility",
            show=False,
            advanced=True,
        ),
        # Transition Issue fields
        MessageTextInput(
            name="JIRA_TRANSITION_ISSUE_issue_id_or_key",
            display_name="Issue ID or Key",
            info="The issue ID or key to transition",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_TRANSITION_ISSUE_transition_id_or_name",
            display_name="Transition",
            info="The transition ID or name (e.g., 'In Progress', 'Done')",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_TRANSITION_ISSUE_comment",
            display_name="Comment",
            info="Optional comment for the transition",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_TRANSITION_ISSUE_resolution",
            display_name="Resolution",
            info="Resolution for the issue (if closing)",
            show=False,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_TRANSITION_ISSUE_assignee",
            display_name="Assignee",
            info="New assignee during transition",
            show=False,
            advanced=True,
        ),
        # Assign Issue fields
        MessageTextInput(
            name="JIRA_ASSIGN_ISSUE_issue_id_or_key",
            display_name="Issue ID or Key",
            info="The issue ID or key to assign",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_ASSIGN_ISSUE_account_id",
            display_name="Account ID",
            info="The account ID of the user to assign",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_ASSIGN_ISSUE_assignee_name",
            display_name="Assignee Name",
            info="The display name of the user to assign (alternative to account ID)",
            show=False,
        ),
        # Get All Projects fields
        IntInput(
            name="JIRA_GET_ALL_PROJECTS_maxResults",
            display_name="Max Results",
            info="Maximum number of projects to return",
            show=False,
            value=50,
        ),
        IntInput(
            name="JIRA_GET_ALL_PROJECTS_startAt",
            display_name="Start At",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        MessageTextInput(
            name="JIRA_GET_ALL_PROJECTS_expand",
            display_name="Expand",
            info="Comma-separated list of fields to expand",
            show=False,
            advanced=True,
        ),
        # List Sprints fields
        IntInput(
            name="JIRA_LIST_SPRINTS_board_id",
            display_name="Board ID",
            info="The ID of the board to get sprints from",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_LIST_SPRINTS_state",
            display_name="State",
            info="Filter by sprint state ('active', 'closed', 'future')",
            show=False,
        ),
        IntInput(
            name="JIRA_LIST_SPRINTS_max_results",
            display_name="Max Results",
            info="Maximum number of sprints to return",
            show=False,
            value=50,
            advanced=True,
        ),
        IntInput(
            name="JIRA_LIST_SPRINTS_start_at",
            display_name="Start At",
            info="Index to start at for pagination",
            show=False,
            value=0,
            advanced=True,
        ),
        # Create Sprint fields
        MessageTextInput(
            name="JIRA_CREATE_SPRINT_name",
            display_name="Name",
            info="Name of the sprint",
            show=False,
            required=True,
        ),
        IntInput(
            name="JIRA_CREATE_SPRINT_origin_board_id",
            display_name="Board ID",
            info="The ID of the board to create the sprint on",
            show=False,
            required=True,
        ),
        MessageTextInput(
            name="JIRA_CREATE_SPRINT_goal",
            display_name="Goal",
            info="The goal of the sprint",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_CREATE_SPRINT_start_date",
            display_name="Start Date",
            info="Start date in ISO 8601 format",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_CREATE_SPRINT_end_date",
            display_name="End Date",
            info="End date in ISO 8601 format",
            show=False,
        ),
        # Find Users fields
        MessageTextInput(
            name="JIRA_FIND_USERS_query",
            display_name="Query",
            info="Search query (email or display name)",
            show=False,
        ),
        MessageTextInput(
            name="JIRA_FIND_USERS_account_id",
            display_name="Account ID",
            info="Filter by specific account ID",
            show=False,
        ),
        IntInput(
            name="JIRA_FIND_USERS_max_results",
            display_name="Max Results",
            info="Maximum number of users to return",
            show=False,
            value=50,
            advanced=True,
        ),
        IntInput(
            name="JIRA_FIND_USERS_start_at",
            display_name="Start At",
            info="Index to start at for pagination",
            show=False,
            value=0,
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
            logger.error(f"Error executing Jira action: {e}")
            display_name = self.action[0]["name"] if isinstance(self.action, list) and self.action else str(self.action)
            msg = f"Failed to execute {display_name}: {e!s}"
            raise ValueError(msg) from e

    def update_build_config(self, build_config: dict, field_value: Any, field_name: str | None = None) -> dict:
        return super().update_build_config(build_config, field_value, field_name)

    def set_default_tools(self):
        self._default_tools = {
            self.sanitize_action_name("JIRA_CREATE_ISSUE").replace(" ", "-"),
            self.sanitize_action_name("JIRA_SEARCH_ISSUES").replace(" ", "-"),
        }
