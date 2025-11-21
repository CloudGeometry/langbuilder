"""Integration tests for project creation and owner assignment (Epic 1, Story 1.5).

Gherkin Scenario: Project Creation and New Entity Owner Assignment
Given any authenticated user is logged in
When the user attempts to create a new Project
Then the user should have access to the Create Project function
When a user successfully creates a new Project or Flow
Then the creating user should be automatically assigned the Owner role for that new entity
And an Admin should be able to modify this new entity's Owner role assignment
"""

from uuid import UUID

import pytest
from httpx import AsyncClient
from langbuilder.services.database.models.user_role_assignment.model import UserRoleAssignment
from langbuilder.services.deps import get_db_service
from sqlmodel import select


@pytest.mark.asyncio
class TestProjectCreation:
    """Test automatic Owner role assignment on project/flow creation."""

    async def test_user_can_create_project(
        self,
        client: AsyncClient,
        logged_in_headers,
    ):
        """Verify that any authenticated user can create a new project."""
        # Create a project (folder)
        project_data = {
            "name": "Test Project for Creation",
            "description": "Test project to verify creation access",
        }

        response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        project = response.json()
        assert project["name"] == project_data["name"]

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers)

    async def test_creating_user_gets_owner_role_on_project(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that user who creates a project automatically gets Owner role."""
        # Create a project
        project_data = {
            "name": "Test Project for Owner Assignment",
            "description": "Test project",
        }

        create_response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        project = create_response.json()

        # Check that user has Owner role for this project
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            assignment_stmt = select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == active_user.id,
                UserRoleAssignment.scope_type == "Project",
                UserRoleAssignment.scope_id == UUID(project["id"]),
            )
            assignment_result = await session.exec(assignment_stmt)
            assignment = assignment_result.first()

            assert assignment is not None, "User should have a role assignment for the created project"

            # Load the role
            await session.refresh(assignment, ["role"])
            assert assignment.role.name == "Owner", "User should have Owner role on created project"

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers)

    async def test_creating_user_gets_owner_role_on_flow(
        self,
        client: AsyncClient,
        logged_in_headers,
        active_user,
    ):
        """Verify that user who creates a flow automatically gets Owner role."""
        # Create a flow
        flow_data = {
            "name": "Test Flow for Owner Assignment",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
        }

        create_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        flow = create_response.json()

        # Check that user has Owner role for this flow
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            assignment_stmt = select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == active_user.id,
                UserRoleAssignment.scope_type == "Flow",
                UserRoleAssignment.scope_id == UUID(flow["id"]),
            )
            assignment_result = await session.exec(assignment_stmt)
            assignment = assignment_result.first()

            assert assignment is not None, "User should have a role assignment for the created flow"

            # Load the role
            await session.refresh(assignment, ["role"])
            assert assignment.role.name == "Owner", "User should have Owner role on created flow"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers)

    async def test_new_entity_owner_is_mutable(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Owner role on new entities (non-Starter Project) is mutable."""
        # Create a new project
        project_data = {
            "name": "Test Project for Mutable Owner",
            "description": "Test project",
        }

        create_response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        project = create_response.json()

        # Find the Owner assignment
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            assignment_stmt = select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == active_user.id,
                UserRoleAssignment.scope_type == "Project",
                UserRoleAssignment.scope_id == UUID(project["id"]),
            )
            assignment_result = await session.exec(assignment_stmt)
            assignment = assignment_result.first()

            assert assignment is not None
            # New project Owner assignments should NOT be immutable (unlike Starter Project)
            assert not assignment.is_immutable, "New project Owner assignment should be mutable"

            assignment_id = assignment.id

        # Admin should be able to modify this assignment
        update_data = {"role_name": "Editor"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment_id}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        assert update_response.status_code == 200, "Admin should be able to modify new entity Owner"

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers_super_user)

    async def test_admin_can_modify_new_project_owner(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Admin can modify Owner role on newly created projects."""
        # Create a new project
        project_data = {
            "name": "Test Project for Admin Modification",
            "description": "Test project",
        }

        create_response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        project = create_response.json()

        # Get the Owner assignment
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}&scope_type=Project",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()
        project_assignment = next((a for a in assignments if a["scope_id"] == project["id"]), None)

        assert project_assignment is not None, "Should find Owner assignment for new project"

        # Admin modifies the assignment
        update_data = {"role_name": "Viewer"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        assert update_response.status_code == 200, "Admin should be able to modify new project Owner"
        updated = update_response.json()
        assert updated["role"]["name"] == "Viewer", "Role should be updated to Viewer"

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers_super_user)

    async def test_admin_can_delete_new_project_owner(
        self,
        client: AsyncClient,
        logged_in_headers,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Admin can delete Owner role on newly created projects."""
        # Create a new project
        project_data = {
            "name": "Test Project for Admin Deletion",
            "description": "Test project",
        }

        create_response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        project = create_response.json()

        # Get the Owner assignment
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}&scope_type=Project",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()
        project_assignment = next((a for a in assignments if a["scope_id"] == project["id"]), None)

        assert project_assignment is not None, "Should find Owner assignment for new project"

        # Admin deletes the assignment
        delete_response = await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

        assert delete_response.status_code == 204, "Admin should be able to delete new project Owner"

        # Cleanup
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers_super_user)

    async def test_all_authenticated_users_can_create_projects(
        self,
        client: AsyncClient,
        logged_in_headers,
    ):
        """Verify that all authenticated users have access to create projects."""
        # This test verifies Story 1.5 requirement:
        # "Given any authenticated user is logged in
        #  When the user attempts to create a new Project
        #  Then the user should have access to the Create Project function"

        project_data = {
            "name": "Test Project for Any User",
            "description": "Test that any authenticated user can create",
        }

        response = await client.post(
            "/api/v1/projects/",
            json=project_data,
            headers=logged_in_headers,
        )

        # Any authenticated user should be able to create
        assert response.status_code == 201, (
            f"Any authenticated user should be able to create projects, got {response.status_code}"
        )

        # Cleanup
        project = response.json()
        await client.delete(f"/api/v1/projects/{project['id']}", headers=logged_in_headers)

    async def test_flow_owner_assignment_is_automatic(
        self,
        client: AsyncClient,
        logged_in_headers,
        active_user,
    ):
        """Verify that flow creator automatically gets Owner role without manual assignment."""
        # Create a flow
        flow_data = {
            "name": "Test Flow for Automatic Owner",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
        }

        create_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers,
        )
        assert create_response.status_code == 201
        flow = create_response.json()

        # Immediately check for Owner role (should exist automatically)
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            assignment_stmt = select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == active_user.id,
                UserRoleAssignment.scope_type == "Flow",
                UserRoleAssignment.scope_id == UUID(flow["id"]),
            )
            assignment_result = await session.exec(assignment_stmt)
            assignment = assignment_result.first()

            assert assignment is not None, "Owner role should be automatically assigned on flow creation"

            await session.refresh(assignment, ["role"])
            assert assignment.role.name == "Owner", "Automatically assigned role should be Owner"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers)
