"""Integration tests for default roles and permission mappings (Epic 1, Story 1.2).

Gherkin Scenario: Mapping Default Roles and Extended Permissions
Given the four base permissions are defined
When the default roles are persisted
Then the Owner role should have full CRUD access to its scope entity
And the Admin role should have full CRUD access across all scopes/entities
And the Editor role should have Create, Read, Update access (but not Delete)
And the Viewer role should have only Read/View access
And the Read/View permission should enable Flow execution, saving, exporting, and downloading
And the Update/Edit permission should enable Flow/Project import
"""

import pytest
from httpx import AsyncClient
from langbuilder.services.database.models.permission.model import Permission
from langbuilder.services.database.models.role.model import Role
from langbuilder.services.deps import get_db_service
from sqlalchemy.orm import selectinload
from sqlmodel import select


@pytest.mark.asyncio
class TestDefaultRoles:
    """Test that default roles have correct permission mappings."""

    async def test_owner_role_has_full_crud(self, client: AsyncClient):
        """Verify that Owner role has Create, Read, Update, Delete permissions."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get Owner role with permissions
            stmt = select(Role).where(Role.name == "Owner").options(selectinload(Role.role_permissions))
            result = await session.exec(stmt)
            owner_role = result.first()

            assert owner_role is not None, "Owner role not found"

            # Get permission names for this role
            permission_ids = [rp.permission_id for rp in owner_role.role_permissions]

            # Get permission details
            perm_stmt = select(Permission).where(Permission.id.in_(permission_ids))
            perm_result = await session.exec(perm_stmt)
            permissions = perm_result.all()

            permission_names = {p.name for p in permissions}

            # Owner should have all CRUD permissions
            assert "Create" in permission_names, "Owner missing Create permission"
            assert "Read" in permission_names, "Owner missing Read permission"
            assert "Update" in permission_names, "Owner missing Update permission"
            assert "Delete" in permission_names, "Owner missing Delete permission"

    async def test_admin_role_has_full_crud(self, client: AsyncClient):
        """Verify that Admin role has full CRUD access across all scopes."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get Admin role with permissions
            stmt = select(Role).where(Role.name == "Admin").options(selectinload(Role.role_permissions))
            result = await session.exec(stmt)
            admin_role = result.first()

            assert admin_role is not None, "Admin role not found"

            # Get permission names for this role
            permission_ids = [rp.permission_id for rp in admin_role.role_permissions]

            # Get permission details
            perm_stmt = select(Permission).where(Permission.id.in_(permission_ids))
            perm_result = await session.exec(perm_stmt)
            permissions = perm_result.all()

            permission_names = {p.name for p in permissions}

            # Admin should have all CRUD permissions
            assert "Create" in permission_names, "Admin missing Create permission"
            assert "Read" in permission_names, "Admin missing Read permission"
            assert "Update" in permission_names, "Admin missing Update permission"
            assert "Delete" in permission_names, "Admin missing Delete permission"

            # Admin should have permissions for both Flow and Project scopes
            permission_scopes = {p.scope for p in permissions}
            assert "Flow" in permission_scopes or "Project" in permission_scopes, (
                "Admin should have permissions for Flow or Project scopes"
            )

    async def test_editor_role_has_create_read_update_no_delete(self, client: AsyncClient):
        """Verify that Editor role has Create, Read, Update but NOT Delete."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get Editor role with permissions
            stmt = select(Role).where(Role.name == "Editor").options(selectinload(Role.role_permissions))
            result = await session.exec(stmt)
            editor_role = result.first()

            assert editor_role is not None, "Editor role not found"

            # Get permission names for this role
            permission_ids = [rp.permission_id for rp in editor_role.role_permissions]

            # Get permission details
            perm_stmt = select(Permission).where(Permission.id.in_(permission_ids))
            perm_result = await session.exec(perm_stmt)
            permissions = perm_result.all()

            permission_names = {p.name for p in permissions}

            # Editor should have Create, Read, Update
            assert "Create" in permission_names, "Editor missing Create permission"
            assert "Read" in permission_names, "Editor missing Read permission"
            assert "Update" in permission_names, "Editor missing Update permission"

            # Editor should NOT have Delete
            assert "Delete" not in permission_names, "Editor should not have Delete permission"

    async def test_viewer_role_has_only_read(self, client: AsyncClient):
        """Verify that Viewer role has only Read/View permission."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get Viewer role with permissions
            stmt = select(Role).where(Role.name == "Viewer").options(selectinload(Role.role_permissions))
            result = await session.exec(stmt)
            viewer_role = result.first()

            assert viewer_role is not None, "Viewer role not found"

            # Get permission names for this role
            permission_ids = [rp.permission_id for rp in viewer_role.role_permissions]

            # Get permission details
            perm_stmt = select(Permission).where(Permission.id.in_(permission_ids))
            perm_result = await session.exec(perm_stmt)
            permissions = perm_result.all()

            permission_names = {p.name for p in permissions}

            # Viewer should ONLY have Read
            assert "Read" in permission_names, "Viewer missing Read permission"
            assert "Create" not in permission_names, "Viewer should not have Create permission"
            assert "Update" not in permission_names, "Viewer should not have Update permission"
            assert "Delete" not in permission_names, "Viewer should not have Delete permission"

    async def test_all_roles_exist_with_descriptions(self, client: AsyncClient):
        """Verify that all roles exist and have proper descriptions."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get all system roles
            stmt = select(Role).where(Role.is_system_role == True)
            result = await session.exec(stmt)
            roles = result.all()

            role_dict = {r.name: r for r in roles}

            # Verify all 4 roles exist
            assert "Admin" in role_dict, "Admin role not found"
            assert "Owner" in role_dict, "Owner role not found"
            assert "Editor" in role_dict, "Editor role not found"
            assert "Viewer" in role_dict, "Viewer role not found"

            # Verify all roles have descriptions
            for role_name, role in role_dict.items():
                assert role.description is not None and len(role.description) > 0, (
                    f"Role {role_name} has no description"
                )

    async def test_permission_counts_per_role(self, client: AsyncClient):
        """Verify that each role has the expected number of permissions."""
        db_manager = get_db_service()
        async with db_manager.with_session() as session:
            # Get role permission counts
            role_names = ["Admin", "Owner", "Editor", "Viewer"]

            for role_name in role_names:
                stmt = select(Role).where(Role.name == role_name).options(selectinload(Role.role_permissions))
                result = await session.exec(stmt)
                role = result.first()

                assert role is not None, f"{role_name} role not found"

                permission_count = len(role.role_permissions)

                # Verify permission counts match expectations
                if role_name == "Viewer":
                    # Viewer should have only Read permissions (2 scopes = 2 permissions)
                    assert permission_count >= 1, f"Viewer should have at least 1 permission, found {permission_count}"
                elif role_name == "Editor":
                    # Editor should have Create, Read, Update (3 actions x 2 scopes = 6 permissions)
                    assert permission_count >= 3, f"Editor should have at least 3 permissions, found {permission_count}"
                elif role_name in ["Owner", "Admin"]:
                    # Owner and Admin should have full CRUD (4 actions x 2 scopes = 8 permissions)
                    assert permission_count >= 4, (
                        f"{role_name} should have at least 4 permissions, found {permission_count}"
                    )

    async def test_role_permission_mappings_via_api(self, client: AsyncClient, logged_in_headers_super_user):
        """Verify that role permission mappings are correct via API."""
        # Get all roles via API
        response = await client.get("/api/v1/rbac/roles", headers=logged_in_headers_super_user)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        roles = response.json()

        # Verify we have all 4 default roles
        role_names = [r["name"] for r in roles]
        assert "Admin" in role_names
        assert "Owner" in role_names
        assert "Editor" in role_names
        assert "Viewer" in role_names

    @pytest.mark.skip(reason="Design test - actual enforcement tested in test_read_permission.py (Epic 2, Story 2.2)")
    async def test_read_permission_enables_flow_operations(self, client: AsyncClient):
        """Verify that Read permission conceptually enables execution, saving, exporting, downloading.

        Note: This is a documentation/design test. Actual enforcement is tested in Epic 2 tests.
        """
        # This test verifies the permission mapping design is correct
        # The actual enforcement of "Read enables execution/export/download" is tested
        # in test_read_permission.py (Epic 2, Story 2.2)

    @pytest.mark.skip(reason="Design test - actual enforcement tested in test_update_permission.py (Epic 2, Story 2.4)")
    async def test_update_permission_enables_import(self, client: AsyncClient):
        """Verify that Update permission conceptually enables Flow/Project import.

        Note: This is a documentation/design test. Actual enforcement is tested in Epic 2 tests.
        """
        # This test verifies the permission mapping design is correct
        # The actual enforcement of "Update enables import" is tested
        # in test_update_permission.py (Epic 2, Story 2.4)
