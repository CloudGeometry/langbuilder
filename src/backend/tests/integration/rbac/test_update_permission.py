"""Integration tests for Update permission enforcement (Epic 2, Story 2.4).

Gherkin Scenario: Preventing Edits for Unauthorized Users
Given a user loads the editor for a Project or Flow
When the user lacks the Update/Edit permission
Then the editor should load in a read-only state
And the user should be prevented from making any changes/edits
And the check must also occur before allowing import functionality
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUpdatePermission:
    """Test Update permission enforcement."""

    async def test_user_with_update_permission_can_modify_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user with Update permission can modify flows."""
        # First, assign user Editor role on folder so they can create flows
        folder_assignment = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }
        await client.post(
            "/api/v1/rbac/assignments",
            json=folder_assignment,
            headers=logged_in_headers_super_user,
        )

        # Create a flow
        flow_data = {
            "name": "Test Flow Update",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers,  # User creates it, gets Owner
        )
        assert create_response.status_code == 201
        flow = create_response.json()

        # Update the flow (Owner has Update permission)
        update_data = {
            "name": "Updated Flow Name",
            "description": "Updated description",
        }

        update_response = await client.patch(
            f"/api/v1/flows/{flow['id']}",
            json=update_data,
            headers=logged_in_headers,
        )

        assert update_response.status_code == 200, "Owner should be able to update flow"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)

    async def test_user_without_update_permission_cannot_modify_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user without Update permission cannot modify flows."""
        # Create a flow as admin
        flow_data = {
            "name": "Test Flow No Update",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers_super_user,
        )
        assert create_response.status_code == 201
        flow = create_response.json()

        # Assign Viewer role (no Update permission)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Flow",
            "scope_id": flow["id"],
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201

        # Try to update the flow
        update_data = {
            "name": "Updated Name",
        }

        update_response = await client.patch(
            f"/api/v1/flows/{flow['id']}",
            json=update_data,
            headers=logged_in_headers,
        )

        # Should be forbidden
        assert update_response.status_code == 403, "Viewer should not be able to update flow"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)

    @pytest.mark.skip(reason="Design test - actual import enforcement tested in import endpoint tests")
    async def test_update_permission_enables_import(
        self,
        client: AsyncClient,
    ):
        """Verify that Update permission enables Flow/Project import functionality."""
        # This is a design test
        # Actual import functionality enforcement is tested in the import endpoint tests

    async def test_check_update_permission_via_api(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that check-permission API correctly reports Update permission."""
        # Assign Editor role (has Update)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201

        # Check Update permission
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Update&scope_type=Project&scope_id={default_folder.id}",
            headers=logged_in_headers,
        )

        assert check_response.status_code == 200
        result = check_response.json()
        assert result["has_permission"] == True, "Editor should have Update permission"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_editor_role_prevents_readonly_state(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Editor role (with Update) does NOT trigger read-only mode."""
        # Assign Editor role
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201

        # Create flow
        flow_data = {
            "name": "Test Flow Editor",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        flow = create_response.json()

        # Check Update permission (should be True for Editor)
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Update&scope_type=Flow&scope_id={flow['id']}",
            headers=logged_in_headers,
        )

        result = check_response.json()
        assert result["has_permission"] == True, "Editor should have Update permission (not read-only)"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )
