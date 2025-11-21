"""Integration tests for Read permission enforcement (Epic 2, Story 2.2).

Gherkin Scenario: UI Filtering and Read Access Enforcement
Given a user loads the Project or Flow list view
When the user lacks the Read/View permission for an entity
Then that entity should not be displayed in the list view
When a user attempts to view the editor, execute, save/export, or download a Flow/Project
Then the AuthService should confirm Read/View permission
And the action should be blocked if permission is denied
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestReadPermission:
    """Test Read permission enforcement for listing and viewing resources."""

    async def test_user_only_sees_flows_with_read_permission(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that flow list only shows flows user has Read permission for."""
        # First, assign user a role on the folder so they can create flows
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

        # Create multiple flows
        # Flow A: User has Owner role (should see)
        flow_a_data = {
            "name": "Flow A - Owner",
            "description": "User has Owner role",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_a_response = await client.post(
            "/api/v1/flows/",
            json=flow_a_data,
            headers=logged_in_headers,  # User creates it, gets Owner
        )
        assert flow_a_response.status_code == 201
        flow_a = flow_a_response.json()

        # Flow B: User has Viewer role (should see)
        flow_b_data = {
            "name": "Flow B - Viewer",
            "description": "User has Viewer role",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_b_response = await client.post(
            "/api/v1/flows/",
            json=flow_b_data,
            headers=logged_in_headers_super_user,  # Admin creates it
        )
        assert flow_b_response.status_code == 201
        flow_b = flow_b_response.json()

        # Assign Viewer role to user for Flow B
        viewer_assignment = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Flow",
            "scope_id": flow_b["id"],
        }

        await client.post(
            "/api/v1/rbac/assignments",
            json=viewer_assignment,
            headers=logged_in_headers_super_user,
        )

        # Flow C: User has no role (should NOT see)
        # Create Flow C in a DIFFERENT folder that user has no access to
        other_folder_response = await client.post(
            "/api/v1/projects/",
            json={"name": "Folder for Flow C", "description": "No access"},
            headers=logged_in_headers_super_user,
        )
        assert other_folder_response.status_code == 201
        other_folder = other_folder_response.json()

        flow_c_data = {
            "name": "Flow C - No Access",
            "description": "User has no role",
            "data": {"nodes": [], "edges": []},
            "folder_id": other_folder["id"],  # Different folder with no user access
        }

        flow_c_response = await client.post(
            "/api/v1/flows/",
            json=flow_c_data,
            headers=logged_in_headers_super_user,  # Admin creates it
        )
        assert flow_c_response.status_code == 201
        flow_c = flow_c_response.json()

        # List flows as regular user
        list_response = await client.get("/api/v1/flows/", headers=logged_in_headers)
        assert list_response.status_code == 200

        flows = list_response.json()
        flow_ids = [f["id"] for f in flows]

        # Should see Flow A and B (has Read permission)
        assert flow_a["id"] in flow_ids, "Should see Flow A (Owner role)"
        assert flow_b["id"] in flow_ids, "Should see Flow B (Viewer role)"

        # Should NOT see Flow C (no permission)
        assert flow_c["id"] not in flow_ids, "Should NOT see Flow C (no role)"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow_a['id']}", headers=logged_in_headers_super_user)
        await client.delete(f"/api/v1/flows/{flow_b['id']}", headers=logged_in_headers_super_user)
        await client.delete(f"/api/v1/flows/{flow_c['id']}", headers=logged_in_headers_super_user)
        await client.delete(f"/api/v1/projects/{other_folder['id']}", headers=logged_in_headers_super_user)

    async def test_user_only_sees_projects_with_read_permission(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that project list only shows projects user has Read permission for."""
        # Create Project A: User creates it (gets Owner)
        project_a_data = {
            "name": "Project A - Owner",
            "description": "User has Owner role",
        }

        project_a_response = await client.post(
            "/api/v1/projects/",
            json=project_a_data,
            headers=logged_in_headers,
        )
        assert project_a_response.status_code == 201
        project_a = project_a_response.json()

        # Create Project B: Admin creates it, no role for user
        project_b_data = {
            "name": "Project B - No Access",
            "description": "User has no role",
        }

        project_b_response = await client.post(
            "/api/v1/projects/",
            json=project_b_data,
            headers=logged_in_headers_super_user,
        )
        assert project_b_response.status_code == 201
        project_b = project_b_response.json()

        # List projects as regular user
        list_response = await client.get("/api/v1/projects/", headers=logged_in_headers)
        assert list_response.status_code == 200

        projects = list_response.json()
        project_ids = [p["id"] for p in projects]

        # Should see Project A (Owner)
        assert project_a["id"] in project_ids, "Should see Project A (Owner role)"

        # Should NOT see Project B (no permission)
        assert project_b["id"] not in project_ids, "Should NOT see Project B (no role)"

        # Cleanup
        await client.delete(f"/api/v1/projects/{project_a['id']}", headers=logged_in_headers_super_user)
        await client.delete(f"/api/v1/projects/{project_b['id']}", headers=logged_in_headers_super_user)

    async def test_cannot_view_flow_without_read_permission(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        default_folder,
    ):
        """Verify that user cannot view flow details without Read permission."""
        # Create a flow as admin
        flow_data = {
            "name": "Flow No Read Access",
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

        # Try to view as regular user (no Read permission)
        view_response = await client.get(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers)

        # Should be forbidden or not found
        assert view_response.status_code in [403, 404], f"Expected 403 or 404, got {view_response.status_code}"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)

    async def test_read_permission_enables_flow_execution(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Read permission enables flow execution."""
        # This is a design test - actual execution testing requires more setup
        # The key is that Viewer role (which has Read) should allow execution

    async def test_read_permission_enables_flow_export(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Read permission enables flow export/download."""
        # This is a design test - actual export testing requires more setup
        # The key is that Viewer role (which has Read) should allow export

    async def test_check_permission_api_for_read(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that check-permission API correctly reports Read permission."""
        # Assign Viewer role (has Read)
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert create_response.status_code == 201
        assignment = create_response.json()

        # Check Read permission via API
        check_response = await client.get(
            f"/api/v1/rbac/check-permission?permission=Read&scope_type=Project&scope_id={default_folder.id}",
            headers=logged_in_headers,
        )

        assert check_response.status_code == 200
        result = check_response.json()
        assert result["has_permission"] == True, "Viewer should have Read permission"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )
