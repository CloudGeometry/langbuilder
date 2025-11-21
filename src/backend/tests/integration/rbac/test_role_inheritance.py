"""Integration tests for role inheritance (Epic 1, Story 1.6).

Gherkin Scenario: Establishing Project Role Inheritance Logic
Given a user has a specific(or default) role assigned to a Project
When the user attempts to access a Flow contained within that Project
Then the user should automatically inherit the permissions of the assigned Project role for that Flow
But if an explicit, different role is assigned to the user for that specific Flow scope,
the Flow-specific role should override the inherited role (per 2.1 logic)
"""

import pytest
from httpx import AsyncClient
from langbuilder.services.deps import get_db_service, get_rbac_service
from sqlmodel import select


@pytest.mark.asyncio
class TestRoleInheritance:
    """Test Project → Flow role inheritance logic."""

    async def test_flow_inherits_project_role(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that user inherits Project role when accessing Flow in that Project."""
        # Assign Editor role to user for the Project
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
        project_assignment = create_response.json()

        # Create a flow in this project (as admin to avoid automatic Owner assignment)
        flow_data = {
            "name": "Test Flow for Inheritance",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers_super_user,  # Admin creates to test inheritance
        )
        assert flow_response.status_code == 201
        flow = flow_response.json()

        # Check user's permission on the Flow (should inherit from Project)
        rbac_service = get_rbac_service()
        db_manager = get_db_service()

        async with db_manager.with_session() as session:
            # User should have Editor permissions on the Flow (inherited from Project)
            has_read = await rbac_service.can_access(active_user.id, "Read", "Flow", flow["id"], session)
            has_update = await rbac_service.can_access(active_user.id, "Update", "Flow", flow["id"], session)
            has_delete = await rbac_service.can_access(active_user.id, "Delete", "Flow", flow["id"], session)

            assert has_read, "User should have Read permission on Flow (inherited from Project Editor)"
            assert has_update, "User should have Update permission on Flow (inherited from Project Editor)"
            assert not has_delete, "User should NOT have Delete permission (Editor role doesn't have Delete)"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_explicit_flow_role_overrides_inherited_project_role(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that explicit Flow role overrides inherited Project role."""
        # Assign Editor role to user for the Project
        project_assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Editor",
            "scope_type": "Project",
            "scope_id": str(default_folder.id),
        }

        project_response = await client.post(
            "/api/v1/rbac/assignments",
            json=project_assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert project_response.status_code == 201
        project_assignment = project_response.json()

        # Create a flow in this project (as admin to avoid automatic Owner assignment)
        flow_data = {
            "name": "Test Flow for Override",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers_super_user,  # Admin creates to test override
        )
        assert flow_response.status_code == 201
        flow = flow_response.json()

        # Assign explicit Viewer role to user for this specific Flow
        flow_assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Flow",
            "scope_id": flow["id"],
        }

        flow_assignment_response = await client.post(
            "/api/v1/rbac/assignments",
            json=flow_assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert flow_assignment_response.status_code == 201
        flow_assignment = flow_assignment_response.json()

        # Check user's permission on the Flow (should use explicit Flow role, not inherited)
        rbac_service = get_rbac_service()
        db_manager = get_db_service()

        async with db_manager.with_session() as session:
            # User should have Viewer permissions on the Flow (explicit), not Editor (inherited)
            has_read = await rbac_service.can_access(active_user.id, "Read", "Flow", flow["id"], session)
            has_update = await rbac_service.can_access(active_user.id, "Update", "Flow", flow["id"], session)
            has_delete = await rbac_service.can_access(active_user.id, "Delete", "Flow", flow["id"], session)

            assert has_read, "User should have Read permission (Viewer role)"
            assert not has_update, "User should NOT have Update permission (Viewer overrides inherited Editor)"
            assert not has_delete, "User should NOT have Delete permission (Viewer role)"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{flow_assignment['id']}",
            headers=logged_in_headers_super_user,
        )
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_no_project_role_no_flow_access(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that without Project role, user has no access to Flows in that Project."""
        # Create a flow (but don't assign any role to user)
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            from langbuilder.services.database.models.flow.model import Flow

            flow = Flow(
                name="Test Flow No Access",
                description="Test flow",
                data={"nodes": [], "edges": []},
                folder_id=default_folder.id,
                user_id=active_user.id,
            )
            session.add(flow)
            await session.commit()
            await session.refresh(flow)

            flow_id = flow.id

        # User should not have access to the flow (no Project or Flow role assigned)
        rbac_service = get_rbac_service()

        async with db_manager.with_session() as session:
            # Remove any auto-assigned Owner role for this test
            from langbuilder.services.database.models.user_role_assignment.model import UserRoleAssignment

            stmt = select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == active_user.id,
                UserRoleAssignment.scope_type == "Flow",
                UserRoleAssignment.scope_id == flow_id,
            )
            result = await session.exec(stmt)
            assignments = result.all()
            for assignment in assignments:
                await session.delete(assignment)
            await session.commit()

            # Check permissions (should be False)
            has_read = await rbac_service.can_access(active_user.id, "Read", "Flow", flow_id, session)
            has_update = await rbac_service.can_access(active_user.id, "Update", "Flow", flow_id, session)

            assert not has_read, "User should not have Read permission without Project or Flow role"
            assert not has_update, "User should not have Update permission without Project or Flow role"

        # Cleanup
        async with db_manager.with_session() as session:
            flow_db = await session.get(Flow, flow_id)
            if flow_db:
                await session.delete(flow_db)
                await session.commit()

    async def test_project_owner_has_full_access_to_flows(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that Project Owner has full CRUD access to Flows in that Project."""
        # Assign Owner role to user for the Project
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
        project_assignment = create_response.json()

        # Create a flow in this project
        flow_data = {
            "name": "Test Flow for Owner",
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

        # Check user's permission on the Flow (should have full CRUD from Project Owner)
        rbac_service = get_rbac_service()
        db_manager = get_db_service()

        async with db_manager.with_session() as session:
            has_create = await rbac_service.can_access(active_user.id, "Create", "Flow", flow["id"], session)
            has_read = await rbac_service.can_access(active_user.id, "Read", "Flow", flow["id"], session)
            has_update = await rbac_service.can_access(active_user.id, "Update", "Flow", flow["id"], session)
            has_delete = await rbac_service.can_access(active_user.id, "Delete", "Flow", flow["id"], session)

            assert has_create, "Project Owner should have Create permission on Flows"
            assert has_read, "Project Owner should have Read permission on Flows"
            assert has_update, "Project Owner should have Update permission on Flows"
            assert has_delete, "Project Owner should have Delete permission on Flows"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )

    async def test_project_viewer_has_readonly_access_to_flows(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        logged_in_headers,
        active_user,
        default_folder,
    ):
        """Verify that Project Viewer has read-only access to Flows in that Project."""
        # Assign Viewer role to user for the Project
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
        project_assignment = create_response.json()

        # Create a flow in this project
        flow_data = {
            "name": "Test Flow for Viewer",
            "description": "Test flow",
            "data": {"nodes": [], "edges": []},
            "folder_id": str(default_folder.id),
        }

        flow_response = await client.post(
            "/api/v1/flows/",
            json=flow_data,
            headers=logged_in_headers_super_user,  # Admin creates it
        )
        assert flow_response.status_code == 201
        flow = flow_response.json()

        # Check user's permission on the Flow (should have only Read from Project Viewer)
        rbac_service = get_rbac_service()
        db_manager = get_db_service()

        async with db_manager.with_session() as session:
            has_read = await rbac_service.can_access(active_user.id, "Read", "Flow", flow["id"], session)
            has_update = await rbac_service.can_access(active_user.id, "Update", "Flow", flow["id"], session)
            has_delete = await rbac_service.can_access(active_user.id, "Delete", "Flow", flow["id"], session)

            assert has_read, "Project Viewer should have Read permission on Flows"
            assert not has_update, "Project Viewer should NOT have Update permission on Flows"
            assert not has_delete, "Project Viewer should NOT have Delete permission on Flows"

        # Cleanup
        await client.delete(f"/api/v1/flows/{flow['id']}", headers=logged_in_headers_super_user)
        await client.delete(
            f"/api/v1/rbac/assignments/{project_assignment['id']}",
            headers=logged_in_headers_super_user,
        )
