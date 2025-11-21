"""Integration tests for Delete permission enforcement (Epic 2, Story 2.5).

Gherkin Scenario: Blocking Unauthorized Deletion
Given a user views the interface for a Project or Flow
When the user does not have the Delete permission
Then the UI elements for deleting the entity must be hidden or disabled
And if the user attempts to bypass the UI, the AuthService should block the action
And the action should only be permitted if the user is an Admin or has the Owner role for the scope entity
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestDeletePermission:
    """Test Delete permission enforcement."""

    async def test_user_with_delete_permission_can_delete_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user with Delete permission can delete flows."""
        # First, grant Owner role to user on the project (so they can create flows)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Owner",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201
        project_assignment = assignment_response.json()

        # Create a flow (user has Owner on project, which includes Create permission)
        flow_data = {
            "name": "Test Flow Delete",
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

        # Delete the flow (Owner has Delete permission)
        delete_response = await client.delete(
            f"/api/v1/flows/{flow['id']}",
            headers=logged_in_headers,
        )

        assert delete_response.status_code == 204, "Owner should be able to delete flow"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_user_without_delete_permission_cannot_delete_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user without Delete permission cannot delete flows."""
        # Create a flow as admin
        flow_data = {
            "name": "Test Flow No Delete",
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

        # Assign Editor role (no Delete permission)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Flow",
            "scope_id": flow["id"],
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201

        # Try to delete the flow
        delete_response = await client.delete(
            f"/api/v1/flows/{flow['id']}",
            headers=logged_in_headers,
        )

        # Should be forbidden
        assert delete_response.status_code == 403, "Editor should not be able to delete flow"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)

    async def test_viewer_cannot_delete(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Viewer role cannot delete resources."""
        # Create a flow as admin
        flow_data = {
            "name": "Test Flow Viewer Delete",
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

        # Assign Viewer role
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

        # Try to delete
        delete_response = await client.delete(
            f"/api/v1/flows/{flow['id']}",
            headers=logged_in_headers,
        )

        assert delete_response.status_code == 403, "Viewer should not be able to delete"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)

    async def test_owner_role_can_delete(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Owner role has Delete permission."""
        # First, grant Owner role to user on the project (so they can create flows)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Owner",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201
        project_assignment = assignment_response.json()

        # Create a flow (user gets Owner automatically on the flow they create)
        flow_data = {
            "name": "Test Flow Owner Delete",
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

        # Owner should be able to delete
        delete_response = await client.delete(
            f"/api/v1/flows/{flow['id']}",
            headers=logged_in_headers,
        )

        assert delete_response.status_code == 204, "Owner should be able to delete"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_admin_can_delete(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        default_folder,
    ):
        """Verify that Admin (superuser) can delete any resource."""
        # Create a flow as admin
        flow_data = {
            "name": "Test Flow Admin Delete",
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

        # Admin should be able to delete
        delete_response = await client.delete(
            f"/api/v1/flows/{flow['id']}",
            headers=logged_in_headers_super_user,
        )

        assert delete_response.status_code == 204, "Admin should be able to delete"

    async def test_check_delete_permission_via_api(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that check-permission API correctly reports Delete permission."""
        # Assign Owner role (has Delete)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Owner",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert assignment_response.status_code == 201

        # Check Delete permission
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Delete&scope_type=Project&scope_id={default_folder.id}",
            headers=logged_in_headers,
        )

        assert check_response.status_code == 200
        result = check_response.json()
        assert result["has_permission"] == True, "Owner should have Delete permission"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_editor_role_does_not_have_delete(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Editor role does NOT have Delete permission."""
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

        # Check Delete permission (should be False)
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Delete&scope_type=Project&scope_id={default_folder.id}",
            headers=logged_in_headers,
        )

        result = check_response.json()
        assert result["has_permission"] == False, "Editor should NOT have Delete permission"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )
