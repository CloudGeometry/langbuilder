"""Integration tests for Create permission enforcement (Epic 2, Story 2.3).

Gherkin Scenario: Blocking Unauthorized Flow Creation
Given a non-Admin user is logged in
When the user views the Project interface
Then the UI elements for creating a new Flow must be hidden or disabled if the user lacks the Create permission
And if the user attempts to bypass the UI, the AuthService should block the creation
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreatePermission:
    """Test Create permission enforcement."""

    async def test_user_with_create_permission_can_create_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user with Create permission can create flows."""
        assignment_id = None
        flow_id = None
        try:
            # Assign Editor role (has Create)
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
            assignment_id = assignment_response.json()["id"]

            # Create a flow in this project
            flow_data = {
                "name": "Test Flow Create",
                "description": "Test flow",
                "data": {"nodes": [], "edges": []},
                "folder_id": str(default_folder.id),
            }

            create_response = await client.post(
                "/api/v1/flows/",
                json=flow_data,
                headers=logged_in_headers,
            )

            assert create_response.status_code == 201, "Editor should be able to create flows"
            flow = create_response.json()
            flow_id = flow["id"]
        finally:
            # Cleanup
            if flow_id:
                await client.delete(f"/api/v1/flows/{flow_id}", headers=logged_in_headers_super_user)
            if assignment_id:
                await client.delete(
                    f"/api/v1/rbac/assignments/{assignment_id}",
                    headers=logged_in_headers_super_user,
                )

    async def test_user_without_create_permission_cannot_create_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that user without Create permission cannot create flows."""
        assignment_id = None
        try:
            # Assign Viewer role (no Create permission)
            assignment_data = {
                "user_id": str(active_user.id),
                "role_name": "Viewer",
                "scope_type": "Project",
                "scope_id": str(default_folder.id),
            }

            assignment_response = await client.post(
                "/api/v1/rbac/assignments",
                json=assignment_data,
                headers=logged_in_headers_super_user,
            )
            assert assignment_response.status_code == 201
            assignment_id = assignment_response.json()["id"]

            # Try to create a flow in this project
            flow_data = {
                "name": "Test Flow No Create",
                "description": "Test flow",
                "data": {"nodes": [], "edges": []},
                "folder_id": str(default_folder.id),
            }

            create_response = await client.post(
                "/api/v1/flows/",
                json=flow_data,
                headers=logged_in_headers,
            )

            # Should be forbidden
            assert create_response.status_code == 403, "Viewer should not be able to create flows"
        finally:
            # Cleanup
            if assignment_id:
                await client.delete(
                    f"/api/v1/rbac/assignments/{assignment_id}",
                    headers=logged_in_headers_super_user,
                )

    async def test_check_create_permission_via_api(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that check-permission API correctly reports Create permission."""
        # Assign Editor role (has Create)
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

        # Check Create permission
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Create&scope_type=Project&scope_id={default_folder.id}",
            headers=logged_in_headers,
        )

        assert check_response.status_code == 200
        result = check_response.json()
        assert result["has_permission"] == True, "Editor should have Create permission"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )
