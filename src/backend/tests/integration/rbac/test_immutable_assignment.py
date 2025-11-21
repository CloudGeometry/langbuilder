"""Integration tests for immutable assignment protection (Epic 1, Story 1.4).

Gherkin Scenario: Preventing changes to the Starter Project Owner Role
Given a user has the Owner role assigned to their default/Starter Project (which is pre-existing)
When an Admin attempts to modify, delete, or transfer this specific Owner role assignment
Then the attempt should be blocked at the application logic layer
And the user should maintain the Owner role on their Starter Project
"""

import pytest
from httpx import AsyncClient
from langbuilder.services.database.models.folder.model import Folder
from langbuilder.services.database.models.user_role_assignment.model import UserRoleAssignment
from langbuilder.services.deps import get_db_service
from sqlmodel import select


@pytest.mark.asyncio
class TestImmutableAssignment:
    """Test that immutable assignments (Starter Project Owner) cannot be modified or deleted."""

    async def test_starter_project_owner_assignment_is_immutable(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Starter Project Owner assignment is marked as immutable."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Find the Starter Project folder for the user
            folder_stmt = select(Folder).where(
                Folder.user_id == active_user.id,
                Folder.name == "Starter Project",
            )
            folder_result = await session.exec(folder_stmt)
            starter_folder = folder_result.first()

            if starter_folder:
                # Find the Owner assignment for this starter project
                assignment_stmt = select(UserRoleAssignment).where(
                    UserRoleAssignment.user_id == active_user.id,
                    UserRoleAssignment.scope_type == "Project",
                    UserRoleAssignment.scope_id == starter_folder.id,
                )
                assignment_result = await session.exec(assignment_stmt)
                assignment = assignment_result.first()

                if assignment:
                    # Verify it's marked as immutable
                    assert assignment.is_immutable, "Starter Project Owner assignment should be immutable"

    async def test_cannot_update_immutable_assignment(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Admin cannot update an immutable assignment."""
        db_manager = get_db_service()

        # First, create an immutable assignment for testing
        async with db_manager.with_session() as session:
            # Create a test folder
            folder = Folder(
                name="Test Immutable Folder",
                description="Test folder for immutable assignment",
                user_id=active_user.id,
            )
            session.add(folder)
            await session.commit()
            await session.refresh(folder)

            # Create an immutable assignment directly in DB
            from langbuilder.services.database.models.role.crud import get_role_by_name

            owner_role = await get_role_by_name(session, "Owner")

            assignment = UserRoleAssignment(
                user_id=active_user.id,
                role_id=owner_role.id,
                scope_type="Project",
                scope_id=folder.id,
                is_immutable=True,
                created_by=active_user.id,
            )
            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)

            assignment_id = assignment.id

        # Try to update the immutable assignment via API
        update_data = {"role_name": "Editor"}

        response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment_id}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        # Should be rejected
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "immutable" in response.text.lower(), "Error message should mention immutability"

        # Cleanup
        async with db_manager.with_session() as session:
            assignment_db = await session.get(UserRoleAssignment, assignment_id)
            if assignment_db:
                await session.delete(assignment_db)
            folder_db = await session.get(Folder, folder.id)
            if folder_db:
                await session.delete(folder_db)
            await session.commit()

    async def test_cannot_delete_immutable_assignment(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that Admin cannot delete an immutable assignment."""
        db_manager = get_db_service()

        # First, create an immutable assignment for testing
        async with db_manager.with_session() as session:
            # Create a test folder
            folder = Folder(
                name="Test Immutable Folder 2",
                description="Test folder for immutable assignment",
                user_id=active_user.id,
            )
            session.add(folder)
            await session.commit()
            await session.refresh(folder)

            # Create an immutable assignment directly in DB
            from langbuilder.services.database.models.role.crud import get_role_by_name

            owner_role = await get_role_by_name(session, "Owner")

            assignment = UserRoleAssignment(
                user_id=active_user.id,
                role_id=owner_role.id,
                scope_type="Project",
                scope_id=folder.id,
                is_immutable=True,
                created_by=active_user.id,
            )
            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)

            assignment_id = assignment.id

        # Try to delete the immutable assignment via API
        response = await client.delete(
            f"/api/v1/rbac/assignments/{assignment_id}",
            headers=logged_in_headers_super_user,
        )

        # Should be rejected
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "immutable" in response.text.lower(), "Error message should mention immutability"

        # Verify assignment still exists
        list_response = await client.get(
            f"/api/v1/rbac/assignments?user_id={active_user.id}",
            headers=logged_in_headers_super_user,
        )
        assignments = list_response.json()
        found = any(a["id"] == str(assignment_id) for a in assignments)
        assert found, "Immutable assignment should still exist after failed deletion"

        # Cleanup
        async with db_manager.with_session() as session:
            # Force delete for cleanup
            assignment_db = await session.get(UserRoleAssignment, assignment_id)
            if assignment_db:
                await session.delete(assignment_db)
            folder_db = await session.get(Folder, folder.id)
            if folder_db:
                await session.delete(folder_db)
            await session.commit()

    async def test_mutable_assignments_can_be_modified(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
        default_folder,
    ):
        """Verify that mutable (non-immutable) assignments CAN be modified."""
        # Create a normal (mutable) assignment
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

        # Verify it's not immutable
        assert not assignment.get("is_immutable", False), "New assignment should not be immutable"

        # Update should succeed
        update_data = {"role_name": "Editor"}

        update_response = await client.patch(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            json=update_data,
            headers=logged_in_headers_super_user,
        )

        assert update_response.status_code == 200, "Mutable assignment should be updatable"

        # Delete should succeed
        delete_response = await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

        assert delete_response.status_code == 204, "Mutable assignment should be deletable"

    async def test_immutable_flag_in_assignment_response(
        self,
        client: AsyncClient,
        logged_in_headers_super_user,
        active_user,
    ):
        """Verify that the is_immutable flag is included in assignment API responses."""
        # Create a mutable assignment
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            folder = Folder(
                name="Test Folder for Immutable Flag",
                description="Test folder",
                user_id=active_user.id,
            )
            session.add(folder)
            await session.commit()
            await session.refresh(folder)

        assignment_data = {
            "user_id": str(active_user.id),
            "role_name": "Viewer",
            "scope_type": "Project",
            "scope_id": str(folder.id),
        }

        create_response = await client.post(
            "/api/v1/rbac/assignments",
            json=assignment_data,
            headers=logged_in_headers_super_user,
        )
        assert create_response.status_code == 201
        assignment = create_response.json()

        # Verify is_immutable field is present
        assert "is_immutable" in assignment, "Assignment response should include is_immutable field"
        assert assignment["is_immutable"] == False, "New assignments should not be immutable by default"

        # Cleanup
        await client.delete(
            f"/api/v1/rbac/assignments/{assignment['id']}",
            headers=logged_in_headers_super_user,
        )

        async with db_manager.with_session() as session:
            folder_db = await session.get(Folder, folder.id)
            if folder_db:
                await session.delete(folder_db)
            await session.commit()

    async def test_immutability_protects_user_starter_project_access(
        self,
        client: AsyncClient,
        active_user,
    ):
        """Verify that immutability ensures users always retain access to their Starter Project."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Find the Starter Project folder for the user
            folder_stmt = select(Folder).where(
                Folder.user_id == active_user.id,
                Folder.name == "Starter Project",
            )
            folder_result = await session.exec(folder_stmt)
            starter_folder = folder_result.first()

            if starter_folder:
                # Find the Owner assignment for this starter project
                assignment_stmt = select(UserRoleAssignment).where(
                    UserRoleAssignment.user_id == active_user.id,
                    UserRoleAssignment.scope_type == "Project",
                    UserRoleAssignment.scope_id == starter_folder.id,
                )
                assignment_result = await session.exec(assignment_stmt)
                assignment = assignment_result.first()

                if assignment:
                    # Verify it's immutable
                    assert assignment.is_immutable, "Starter Project Owner assignment must be immutable"

                    # Verify role is Owner
                    await session.refresh(assignment, ["role"])
                    assert assignment.role.name == "Owner", "Starter Project assignment must be Owner role"
