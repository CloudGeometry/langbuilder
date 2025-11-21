"""Integration tests for role assignment logic (Epic 1, Story 1.3).

Gherkin Scenario: Admin Assigns or Modifies a Role Assignment
Given the internal assignment API (assignRole / removeRole) is exposed
When an Admin calls the API to create a new role assignment (User, Role, Scope)
Then the assignment should be successfully persisted
When an Admin calls the API to modify or delete an existing assignment
Then the Admin should be authorized to perform the action
And the updated assignment should be successfully persisted or removed
But the Admin should be prevented from modifying the Starter Project Owner assignment (as per 1.4)
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRoleAssignment:
    """Test role assignment creation, modification, and deletion via API."""

    async def test_admin_can_create_role_assignment(
        self, client: AsyncClient, logged_in_headers_super_user, active_user, default_folder
    ):
        """Verify that Admin can create a new role assignment."""
        # Create assignment data
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        assignment_id = None
        try:
            # Create assignment via API
            response = await client.post(
                "/api/v1/rbac/assignments",
                json=assignment_data,
                headers=logged_in_headers_super_user,
            )

            assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

            assignment = response.json()
            assignment_id = assignment["id"]

            # Verify assignment properties
            assert assignment["user_id"] == str(active_user.id)
            assert assignment["role"]["name"] == "Editor"
            assert assignment["scope_type"] == "Project"
            assert assignment["scope_id"] == str(default_folder.id)
            assert "id" in assignment
            assert "created_at" in assignment
        finally:
            # Cleanup: Delete the assignment
            if assignment_id:
                await client.delete(
                    f"/api/v1/rbac/assignments/{assignment_id}",
                    headers=logged_in_headers_super_user,
                )

    async def test_admin_can_list_role_assignments(self, client: AsyncClient, logged_in_headers_super_user):
        """Verify that Admin can list all role assignments."""
        response = await client.get(
            "/api/v1/rbac/assignments",
            headers=logged_in_headers_super_user,
        )

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        assignments = response.json()
        assert isinstance(assignments, list)

    async def test_admin_can_filter_assignments_by_user(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Admin can filter assignments by user ID."""
        # Create an assignment
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

        # List assignments filtered by user
        response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )

        assert response.status_code == 200
        assignments = response.json()

        # Should find at least the assignment we just created
        user_assignments = [a for a in assignments if a["user_id"] == str(active_user.id)]
        assert len(user_assignments) >= 1

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_admin_can_filter_assignments_by_role(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Admin can filter assignments by role name."""
        # Create an assignment with specific role
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

        # List assignments filtered by role
        response = await client.get(
            "/api/v1/rbac/assignments?role_name=Owner",
            headers=logged_in_headers_super_user,
        )

        assert response.status_code == 200
        assignments = response.json()

        # Should find at least the assignment we just created
        owner_assignments = [a for a in assignments if a["role"]["name"] == "Owner"]
        assert len(owner_assignments) >= 1

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_admin_can_filter_assignments_by_scope_type(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Admin can filter assignments by scope type."""
        # Create an assignment
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

        # List assignments filtered by scope type
        response = await client.get(
            "/api/v1/rbac/assignments?scope_type=Project",
            headers=logged_in_headers_super_user,
        )

        assert response.status_code == 200
        assignments = response.json()

        # Should find at least the assignment we just created
        project_assignments = [a for a in assignments if a["scope_type"] == "Project"]
        assert len(project_assignments) >= 1

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{create_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_admin_can_update_role_assignment(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Admin can update an existing role assignment."""
        # Create an assignment
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

        # Update the role to Editor
        update_data = {"role_name": "Editor"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        assert update_response.status_code == 200, (
            f"Expected 200, got {update_response.status_code}: {update_response.text}"
        )
        updated_assignment = update_response.json()

        # Verify the role was updated
        assert updated_assignment["role"]["name"] == "Editor"
        assert updated_assignment["id"] == assignment["id"]

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_admin_can_delete_role_assignment(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that Admin can delete a role assignment."""
        # Create an assignment
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

        # Delete the assignment
        delete_response = await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}"

        # Verify the assignment is deleted by trying to list it
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()

        # Should not find the deleted assignment
        deleted_assignment = [a for a in assignments if a["id"] == assignment["id"]]
        assert len(deleted_assignment) == 0, "Deleted assignment still exists"

    async def test_non_admin_cannot_create_assignment(
        self,
        client: AsyncClient,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that non-Admin users cannot create role assignments."""
        # Try to create assignment as non-admin
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers,
        )

        # Should be forbidden
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

        # Validate error message indicates forbidden access
        error_detail = response.json().get("detail", "")
        assert error_detail, "Error response should include detail message"

    async def test_non_admin_cannot_update_assignment(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that non-Admin users cannot update role assignments."""
        # Create assignment as admin
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

        # Try to update as non-admin
        update_data = {"role_name": "Editor"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            json=update_data,
            headers=logged_in_headers,
        )

        # Should be forbidden
        assert update_response.status_code == 403, f"Expected 403, got {update_response.status_code}"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_non_admin_cannot_delete_assignment(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that non-Admin users cannot delete role assignments."""
        # Create assignment as admin
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

        # Try to delete as non-admin
        delete_response = await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers,
        )

        # Should be forbidden
        assert delete_response.status_code == 403, f"Expected 403, got {delete_response.status_code}"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_cannot_create_duplicate_assignment(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that duplicate assignments (same user, role, scope) are rejected."""
        # Create an assignment
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        first_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert first_response.status_code == 201

        # Try to create the same assignment again
        second_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )

        # Should be rejected as duplicate
        assert second_response.status_code == 409, (
            f"Expected 409, got {second_response.status_code}: {second_response.text}"
        )

        # Validate error message indicates duplicate/conflict
        error_detail = second_response.json().get("detail", "")
        assert error_detail, "Error response should include detail message"
        assert any(word in error_detail.lower() for word in ["already", "exists", "duplicate"]), (
            f"Error message should indicate duplicate: {error_detail}"
        )

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{first_response.json()['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_cannot_assign_nonexistent_role(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that assignment with non-existent role is rejected."""
        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "NonExistentRole",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )

        # Should be not found
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

        # Validate error message indicates not found
        error_detail = response.json().get("detail", "")
        assert error_detail, "Error response should include detail message"
        assert "not found" in error_detail.lower(), f"Error message should indicate not found: {error_detail}"

    async def test_cannot_assign_to_nonexistent_user(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        default_folder,
    ):
        """Verify that assignment to non-existent user is rejected."""
        fake_user_id = str(uuid4())

        assignment_data = {
            "user_id": fake_user_id,
            "role_name": "Viewer",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )

        # Should be not found
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"

    async def test_cannot_assign_to_nonexistent_scope(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that assignment to non-existent scope resource is rejected."""
        fake_scope_id = str(uuid4())

        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Project",
            "scope_id": fake_scope_id,
        }

        response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )

        # Should be not found
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
