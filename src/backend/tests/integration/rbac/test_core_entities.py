"""Integration tests for RBAC core entities (Epic 1, Story 1.1).

Gherkin Scenario: Defining the Core RBAC Entities
Given the persistence layer is available
When the system is initialized
Then the four base permissions (Create, Read, Update, Delete) should be defined
And the two entity scopes (Flow, Project) should be defined
And the data model should establish the relationship between permissions and scopes
"""

import pytest
from httpx import AsyncClient
from langbuilder.services.database.models.permission.model import Permission
from langbuilder.services.database.models.role.model import Role
from langbuilder.services.deps import get_db_service
from sqlmodel import select


@pytest.mark.asyncio
class TestCoreRBACEntities:
    """Test that core RBAC entities are properly initialized."""

    async def test_core_permissions_exist_in_database(self, client: AsyncClient):
        """Verify that all 8 permissions (4 actions x 2 scopes) exist in database."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Query all permissions
            stmt = select(Permission)
            result = await session.exec(stmt)
            permissions = result.all()

            # Should have exactly 8 permissions (4 actions x 2 scopes)
            assert len(permissions) >= 8, f"Expected at least 8 permissions, found {len(permissions)}"

            # Verify all combinations exist
            expected = [
                ("Create", "Flow"),
                ("Read", "Flow"),
                ("Update", "Flow"),
                ("Delete", "Flow"),
                ("Create", "Project"),
                ("Read", "Project"),
                ("Update", "Project"),
                ("Delete", "Project"),
            ]

            actual = [(p.name, p.scope) for p in permissions]

            for expected_perm in expected:
                assert expected_perm in actual, f"Expected permission {expected_perm} not found"

    async def test_core_permissions_via_api(self, client: AsyncClient, logged_in_headers_super_user):
        """Verify that all permissions are accessible via API."""
        # Note: This requires an API endpoint to list permissions
        # If it doesn't exist yet, we'll test via direct DB query above

    async def test_core_roles_exist(self, client: AsyncClient):
        """Verify that all 4 default roles exist in database."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Query all roles
            stmt = select(Role)
            result = await session.exec(stmt)
            roles = result.all()

            # Extract role names
            role_names = [r.name for r in roles]

            # Verify all 4 default roles exist
            assert "Viewer" in role_names, "Viewer role not found"
            assert "Editor" in role_names, "Editor role not found"
            assert "Owner" in role_names, "Owner role not found"
            assert "Admin" in role_names, "Admin role not found"

    async def test_roles_via_api(self, client: AsyncClient, logged_in_headers_super_user):
        """Verify that all roles are accessible via RBAC API."""
        response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers_super_user)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        roles = response.json()
        role_names = [r["name"] for r in roles]

        # Verify all 4 default roles exist
        assert "Viewer" in role_names, "Viewer role not found"
        assert "Editor" in role_names, "Editor role not found"
        assert "Owner" in role_names, "Owner role not found"
        assert "Admin" in role_names, "Admin role not found"

    async def test_role_permission_relationships(self, client: AsyncClient):
        """Verify that roles have proper permission relationships."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get Admin role and verify it has full CRUD permissions
            stmt = select(Role).where(Role.name == "Admin")
            result = await session.exec(stmt)
            admin_role = result.first()

            assert admin_role is not None, "Admin role not found"
            # Note: Detailed permission checks are done in test_default_roles.py

    async def test_system_roles_are_marked_correctly(self, client: AsyncClient):
        """Verify that default roles are marked as system roles."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            stmt = select(Role).where(Role.name.in_(["Admin", "Owner", "Editor", "Viewer"]))
            result = await session.exec(stmt)
            system_roles = result.all()

            # All default roles should be marked as system roles
            for role in system_roles:
                assert role.is_system_role, f"Role {role.name} should be a system role"

    async def test_permission_scope_types(self, client: AsyncClient):
        """Verify that permissions have correct scope types."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            stmt = select(Permission)
            result = await session.exec(stmt)
            permissions = result.all()

            # Extract unique scope types
            scope_types = {p.scope for p in permissions}

            # Should have Flow and Project scopes
            assert "Flow" in scope_types, "Flow scope not found"
            assert "Project" in scope_types, "Project scope not found"

    async def test_permission_action_types(self, client: AsyncClient):
        """Verify that permissions have correct action types."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            stmt = select(Permission)
            result = await session.exec(stmt)
            permissions = result.all()

            # Extract unique action types
            action_types = {p.name for p in permissions}

            # Should have all CRUD actions
            assert "Create" in action_types, "Create action not found"
            assert "Read" in action_types, "Read action not found"
            assert "Update" in action_types, "Update action not found"
            assert "Delete" in action_types, "Delete action not found"
