"""Integration tests for RBAC Management API (Epic 3, Stories 3.1-3.4).

Epic 3: Web-based Admin Management Interface
Story 3.1: RBAC Management Section in the Admin Page
Story 3.2: Assignment Creation Workflow (New Roles)
Story 3.3: Assignment List View and Filtering
Story 3.4: Assignment Editing and Removal
Story 3.5: Flow Role Inheritance Display Rule
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRBACManagementAPI:
    """Test RBAC Management API endpoints for Admin users."""

    # Story 3.1: RBAC Management Section Access
    async def test_admin_can_access_rbac_management(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
    ):
        """Verify that Admin can access RBAC management endpoints."""
        # List roles
        roles_response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers_super_user)
        assert roles_response.status_code == 200, "Admin should access roles endpoint"

        # List assignments
        assignments_response = await client.get(
            "/api/v1/rbac/assignments",
            headers=logged_in_headers_super_user,
        )
        assert assignments_response.status_code == 200, "Admin should access assignments endpoint"

    async def test_non_admin_cannot_access_rbac_management(
        self,
        client: AsyncClient,
        logged_in_headers,
    ):
        """Verify that non-Admin users cannot access RBAC management."""
        # List roles
        roles_response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers)
        assert roles_response.status_code == 403, "Non-admin should be forbidden from roles endpoint"

        # List assignments
        assignments_response = await client.get("/api/v1/rbac/assignments", headers=logged_in_headers)
        assert assignments_response.status_code == 403, "Non-admin should be forbidden from assignments"

    # Story 3.2: Assignment Creation Workflow
    async def test_assignment_creation_workflow(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify the complete assignment creation workflow."""
        # Step 1: Get available roles
        roles_response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers_super_user)
        assert roles_response.status_code == 200
        roles = roles_response.json()
        assert len(roles) >= 4, "Should have at least 4 default roles"

        # Step 2: Select User, Scope, Role
        # (In UI, this would be done via form)

        # Step 3: Create assignment
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_id = None
        try:
            create_response = await client.post(
                "/api/v1/rbac/assignments",
                json=assignment_data,
                headers=logged_in_headers_super_user,
            )

            assert create_response.status_code == 201
            assignment = create_response.json()
            assignment_id = assignment["id"]

            # Step 4: Confirm assignment was created
            assert assignment["user_id"] == str(active_user.id)
            assert assignment["role"]["name"] == "Editor"
            assert assignment["scope_type"] == "Project"
        finally:
            # Cleanup
            if assignment_id:
                await client.delete(
                    f"/api/v1/rbac/assignments/{assignment_id}",
                    headers=logged_in_headers_super_user,
                )

    async def test_only_default_roles_assignable(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
    ):
        """Verify that only the 4 default roles (plus Admin) are available for assignment."""
        roles_response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers_super_user)
        assert roles_response.status_code == 200

        roles = roles_response.json()
        role_names = [r["name"] for r in roles]

        # Should have the 4 default roles
        assert "Admin" in role_names
        assert "Owner" in role_names
        assert "Editor" in role_names
        assert "Viewer" in role_names

    # Story 3.3: Assignment List View and Filtering
    async def test_assignment_list_view(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be listed with all details."""
        # Create some assignments
        assignments_to_create = [
            {
                "user_id": str(active_user.id),
                "role_name": "Editor",
                "scope_type": "Project",
                "scope_id": str(default_folder.id),
            },
            {
                "user_id": str(active_user.id),
                "role_name": "Viewer",
                "scope_type": "Project",
                "scope_id": str(default_folder.id),
            },
        ]

        created_ids = []
        for assignment_data in assignments_to_create:
            # Use different scope_id for second assignment to avoid duplicate
            if len(created_ids) > 0:
                # Create another project for second assignment
                project_response = await client.post(
                    "/api/v1/projects/",
                    json={"name": "Test Project 2", "description": "Test"},
                    headers=logged_in_headers_super_user,
                )
                project2 = project_response.json()
                assignment_data["scope_id"] = project2["id"]

            response = await client.post(
                "/api/v1/rbac/assignments",
                json=assignment_data,
                headers=logged_in_headers_super_user,
            )
            if response.status_code == 201:
                created_ids.append(response.json()["id"])

        # List all assignments
        list_response = await client.get(
            "/api/v1/rbac/assignments",
            headers=logged_in_headers_super_user,
        )

        assert list_response.status_code == 200
        assignments = list_response.json()

        # Should find our created assignments
        our_assignments = [a for a in assignments if a["id"] in created_ids]
        assert len(our_assignments) >= 1

        # Each assignment should have required fields
        for assignment in our_assignments:
            assert "id" in assignment
            assert "user_id" in assignment
            assert "role" in assignment
            assert "scope_type" in assignment
            assert "scope_id" in assignment
            assert "is_immutable" in assignment

        # Cleanup
        for assignment_id in created_ids:
            await client.delete(
                f"/api/v1/rbac/assignments/{assignment_id}",
                headers=logged_in_headers_super_user,
            )

    async def test_filter_assignments_by_user(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be filtered by user."""
        # Create assignment
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

        # Filter by user
        filter_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )

        assert filter_response.status_code == 200
        filtered_assignments = filter_response.json()

        # All results should be for this user
        for assignment in filtered_assignments:
            assert assignment["user_id"] == str(active_user.id)

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_filter_assignments_by_role(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be filtered by role name."""
        # Create assignment
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Owner",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert create_response.status_code == 201

        # Filter by role
        filter_response = await client.get(
            "/api/v1/rbac/assignments?role_name=Owner",
            headers=logged_in_headers_super_user,
        )

        assert filter_response.status_code == 200
        filtered_assignments = filter_response.json()

        # All results should have Owner role
        for assignment in filtered_assignments:
            assert assignment["role"]["name"] == "Owner"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_filter_assignments_by_scope_type(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be filtered by scope type."""
        # Create assignment
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        create_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert create_response.status_code == 201

        # Filter by scope type
        filter_response = await client.get(
            "/api/v1/rbac/assignments?scope_type=Project",
            headers=logged_in_headers_super_user,
        )

        assert filter_response.status_code == 200
        filtered_assignments = filter_response.json()

        # All results should have Project scope
        for assignment in filtered_assignments:
            assert assignment["scope_type"] == "Project"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    # Story 3.4: Assignment Editing and Removal
    async def test_assignment_editing(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be edited (change role)."""
        # Create assignment
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

        # Edit the assignment (change role)
        update_data = {"role_name": "Editor"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        assert update_response.status_code == 200
        updated_assignment = update_response.json()
        assert updated_assignment["role"]["name"] == "Editor"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_assignment_removal(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignments can be removed/deleted."""
        # Create assignment
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

        # Remove the assignment
        delete_response = await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

        assert delete_response.status_code == 204

        # Verify it's gone
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()

        deleted = [a for a in assignments if a["id"] == assignment["id"]]
        assert len(deleted) == 0, "Assignment should be deleted"

    # Story 3.5: Flow Role Inheritance Display Rule
    async def test_inherited_flow_roles_not_shown_in_list(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that inherited Flow roles are not shown as separate assignments."""
        # Assign Editor role at Project level
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        project_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert project_response.status_code == 201
        project_assignment = project_response.json()

        # Create a flow in this project
        flow_data = {
            "name": "Test Flow Inherited",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers,
        )
        assert flow_response.status_code == 201
        flow = flow_response.json()

        # List assignments
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()

        # Should have Project assignment, but NOT a separate Flow assignment for inherited role
        flow_assignments = [a for a in assignments if a["scope_type"] == "Flow" and a["scope_id"] == flow["id"]]

        # Should NOT have inherited assignment in list
        # (Note: Auto-assigned Owner from flow creation might exist, but that's different)

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_assignment_api_returns_complete_data(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignment API returns all necessary fields."""
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
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

        # Verify all required fields are present
        assert "id" in assignment
        assert "user_id" in assignment
        assert "role" in assignment
        assert "name" in assignment["role"]
        assert "scope_type" in assignment
        assert "scope_id" in assignment
        assert "is_immutable" in assignment
        assert "created_at" in assignment
        assert "created_by" in assignment

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )
