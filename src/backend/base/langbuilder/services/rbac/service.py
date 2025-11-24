"""RBAC Service for permission checking and role management."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger
from sqlalchemy.orm import selectinload
from sqlmodel import select

from langbuilder.services.base import Service
from langbuilder.services.database.models.flow.model import Flow
from langbuilder.services.database.models.folder.model import Folder
from langbuilder.services.database.models.permission.model import Permission
from langbuilder.services.database.models.role.crud import get_role_by_name
from langbuilder.services.database.models.role.model import Role
from langbuilder.services.database.models.role_permission.model import RolePermission
from langbuilder.services.database.models.user.crud import get_user_by_id
from langbuilder.services.database.models.user_role_assignment.crud import (
    get_user_role_assignment,
    get_user_role_assignment_by_id,
)
from langbuilder.services.database.models.user_role_assignment.model import UserRoleAssignment
from langbuilder.services.rbac.exceptions import (
    AssignmentNotFoundException,
    DuplicateAssignmentException,
    ImmutableAssignmentException,
    InvalidScopeException,
    ResourceNotFoundException,
    RoleNotFoundException,
    UserNotFoundException,
)

if TYPE_CHECKING:
    from sqlmodel.ext.asyncio.session import AsyncSession


class RBACService(Service):
    """Role-Based Access Control service for permission checks and role management."""

    name = "rbac_service"

    async def can_access(
        self,
        user_id: UUID | str,
        permission_name: str,
        scope_type: str,
        scope_id: UUID | str | None,
        db: AsyncSession,
    ) -> bool:
        """Core authorization check. Returns True if user has permission.

        Logic:
        1. Check if user is superuser (bypass all checks)
        2. Check if user has Global Admin role (bypass all checks)
        3. For Flow scope:
           - Check for explicit Flow-level role assignment
           - If none, check for inherited Project-level role assignment
        4. For Project scope:
           - Check for explicit Project-level role assignment
        5. Check if role has the required permission

        Args:
            user_id: The user's ID (UUID or string)
            permission_name: Permission name (e.g., "Create", "Read", "Update", "Delete")
            scope_type: Scope type (e.g., "Flow", "Project", "Global")
            scope_id: Specific resource ID (None for Global scope, UUID or string)
            db: Database session

        Returns:
            bool: True if user has permission, False otherwise
        """
        # Convert string UUIDs to UUID objects
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(scope_id, str):
            scope_id = UUID(scope_id)

        # 1. Superuser bypass
        user = await get_user_by_id(db, user_id)
        if user and user.is_superuser:
            return True

        # 2. Global Admin role bypass
        if await self._has_global_admin_role(user_id, db):
            return True

        # 3. Get user's role for the scope
        role = await self._get_user_role_for_scope(user_id, scope_type, scope_id, db)

        if not role:
            return False

        # 4. Check if role has the permission
        return await self._role_has_permission(role.id, permission_name, scope_type, db)

    async def _has_global_admin_role(self, user_id: UUID, db: AsyncSession) -> bool:
        """Check if user has Global Admin role.

        Args:
            user_id: The user's ID
            db: Database session

        Returns:
            bool: True if user has Global Admin role, False otherwise
        """
        stmt = (
            select(UserRoleAssignment)
            .where(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.scope_type == "Global",
            )
            .join(Role)
            .where(Role.name == "Admin")
        )

        result = await db.exec(stmt)
        return result.first() is not None

    async def _get_user_role_for_scope(
        self,
        user_id: UUID,
        scope_type: str,
        scope_id: UUID | None,
        db: AsyncSession,
    ) -> Role | None:
        """Get user's role for a specific scope.

        For Flow scope: checks Flow-specific assignment first, then inherited Project assignment.

        Args:
            user_id: The user's ID
            scope_type: Scope type (e.g., "Flow", "Project", "Global")
            scope_id: Specific resource ID (None for Global scope)
            db: Database session

        Returns:
            Role | None: The user's role for the scope, or None if no assignment exists
        """
        # Check for explicit scope assignment
        stmt = (
            select(UserRoleAssignment)
            .where(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.scope_type == scope_type,
                UserRoleAssignment.scope_id == scope_id,
            )
            .options(selectinload(UserRoleAssignment.role))
        )

        result = await db.exec(stmt)
        assignment = result.first()

        if assignment:
            return assignment.role

        # For Flow scope, check inherited Project role
        if scope_type == "Flow" and scope_id:
            flow_stmt = select(Flow).where(Flow.id == scope_id)
            flow_result = await db.exec(flow_stmt)
            flow = flow_result.first()

            if flow and flow.folder_id:
                return await self._get_user_role_for_scope(user_id, "Project", flow.folder_id, db)

        return None

    async def _role_has_permission(
        self,
        role_id: UUID,
        permission_name: str,
        scope_type: str,
        db: AsyncSession,
    ) -> bool:
        """Check if role has a specific permission.

        Args:
            role_id: The role's ID
            permission_name: Permission name (e.g., "Create", "Read")
            scope_type: Scope type (e.g., "Flow", "Project")
            db: Database session

        Returns:
            bool: True if role has the permission, False otherwise
        """
        stmt = (
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .join(Permission)
            .where(
                Permission.name == permission_name,
                Permission.scope == scope_type,
            )
        )

        result = await db.exec(stmt)
        return result.first() is not None

    async def assign_role(
        self,
        user_id: UUID,
        role_name: str,
        scope_type: str,
        scope_id: UUID | None,
        created_by: UUID,
        db: AsyncSession,
        is_immutable: bool = False,  # noqa: FBT001, FBT002
    ) -> UserRoleAssignment:
        """Create a new role assignment.

        Args:
            user_id: The user's ID
            role_name: The role name to assign
            scope_type: Scope type (e.g., "Flow", "Project", "Global")
            scope_id: Specific resource ID (None for Global scope)
            created_by: ID of user creating the assignment
            db: Database session
            is_immutable: Whether assignment is immutable (cannot be modified/deleted)

        Returns:
            UserRoleAssignment: The created assignment

        Raises:
            UserNotFoundException: If user not found
            RoleNotFoundException: If role not found
            ResourceNotFoundException: If scope resource (Flow or Project) not found
            InvalidScopeException: If scope_type is invalid or scope_id is invalid for the scope_type
            DuplicateAssignmentException: If assignment already exists
        """
        # 1. Validate user exists
        user = await get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundException(str(user_id))

        # 2. Validate role exists
        role = await get_role_by_name(db, role_name)
        if not role:
            raise RoleNotFoundException(role_name)

        # 3. Validate scope and resource existence
        if scope_type == "Flow":
            if not scope_id:
                msg = "Flow scope requires scope_id"
                raise InvalidScopeException(msg)
            flow_stmt = select(Flow).where(Flow.id == scope_id)
            flow_result = await db.exec(flow_stmt)
            flow = flow_result.first()
            if not flow:
                resource_type = "Flow"
                resource_id = str(scope_id)
                raise ResourceNotFoundException(resource_type, resource_id)
        elif scope_type == "Project":
            if not scope_id:
                msg = "Project scope requires scope_id"
                raise InvalidScopeException(msg)
            folder_stmt = select(Folder).where(Folder.id == scope_id)
            folder_result = await db.exec(folder_stmt)
            folder = folder_result.first()
            if not folder:
                resource_type = "Project"
                resource_id = str(scope_id)
                raise ResourceNotFoundException(resource_type, resource_id)
        elif scope_type == "Global":
            if scope_id is not None:
                msg = "Global scope should not have scope_id"
                raise InvalidScopeException(msg)
        else:
            msg = f"Invalid scope_type: {scope_type}. Must be 'Flow', 'Project', or 'Global'"
            raise InvalidScopeException(msg)

        # 4. Check for duplicate assignment
        existing = await get_user_role_assignment(db, user_id, role.id, scope_type, scope_id)
        if existing:
            raise DuplicateAssignmentException

        # 5. Create assignment
        assignment = UserRoleAssignment(
            user_id=user_id,
            role_id=role.id,
            scope_type=scope_type,
            scope_id=scope_id,
            is_immutable=is_immutable,
            created_by=created_by,
        )

        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)

        # 6. Audit log
        logger.info(
            "RBAC: Role assigned",
            extra={
                "action": "assign_role",
                "user_id": str(user_id),
                "role_name": role_name,
                "role_id": str(role.id),
                "scope_type": scope_type,
                "scope_id": str(scope_id) if scope_id else None,
                "created_by": str(created_by),
                "assignment_id": str(assignment.id),
                "is_immutable": is_immutable,
            },
        )

        return assignment

    async def remove_role(
        self,
        assignment_id: UUID,
        db: AsyncSession,
    ) -> None:
        """Remove a role assignment (if not immutable).

        Args:
            assignment_id: The assignment's ID
            db: Database session

        Raises:
            AssignmentNotFoundException: If assignment not found
            ImmutableAssignmentException: If assignment is immutable
        """
        assignment = await get_user_role_assignment_by_id(db, assignment_id)

        if not assignment:
            raise AssignmentNotFoundException(str(assignment_id))

        if assignment.is_immutable:
            raise ImmutableAssignmentException(operation="remove")

        # Capture assignment details before deletion
        user_id = assignment.user_id
        role_id = assignment.role_id
        scope_type = assignment.scope_type
        scope_id = assignment.scope_id

        await db.delete(assignment)
        await db.commit()

        # Audit log
        logger.info(
            "RBAC: Role removed",
            extra={
                "action": "remove_role",
                "assignment_id": str(assignment_id),
                "user_id": str(user_id),
                "role_id": str(role_id),
                "scope_type": scope_type,
                "scope_id": str(scope_id) if scope_id else None,
            },
        )

    async def update_role(
        self,
        assignment_id: UUID,
        new_role_name: str,
        db: AsyncSession,
    ) -> UserRoleAssignment:
        """Update an existing role assignment (if not immutable).

        Args:
            assignment_id: The assignment's ID
            new_role_name: The new role name
            db: Database session

        Returns:
            UserRoleAssignment: The updated assignment

        Raises:
            AssignmentNotFoundException: If assignment not found
            ImmutableAssignmentException: If assignment is immutable
            RoleNotFoundException: If new role not found
        """
        assignment = await get_user_role_assignment_by_id(db, assignment_id)

        if not assignment:
            raise AssignmentNotFoundException(str(assignment_id))

        if assignment.is_immutable:
            raise ImmutableAssignmentException(operation="modify")

        new_role = await get_role_by_name(db, new_role_name)
        if not new_role:
            raise RoleNotFoundException(new_role_name)

        # Capture old role_id before update
        old_role_id = assignment.role_id

        assignment.role_id = new_role.id
        await db.commit()
        await db.refresh(assignment)

        # Audit log
        logger.info(
            "RBAC: Role updated",
            extra={
                "action": "update_role",
                "assignment_id": str(assignment_id),
                "user_id": str(assignment.user_id),
                "old_role_id": str(old_role_id),
                "new_role_id": str(new_role.id),
                "new_role_name": new_role_name,
                "scope_type": assignment.scope_type,
                "scope_id": str(assignment.scope_id) if assignment.scope_id else None,
            },
        )

        return assignment

    async def list_user_assignments(
        self,
        user_id: UUID | str | None,
        db: AsyncSession,
    ) -> list[UserRoleAssignment]:
        """List all role assignments with role relationship loaded, optionally filtered by user.

        Args:
            user_id: Optional user ID to filter assignments (UUID or string)
            db: Database session

        Returns:
            list[UserRoleAssignment]: List of role assignments with role relationship loaded
        """
        # Convert string UUID to UUID object
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        if user_id:
            stmt = (
                select(UserRoleAssignment)
                .where(UserRoleAssignment.user_id == user_id)
                .options(selectinload(UserRoleAssignment.role))
            )
        else:
            stmt = select(UserRoleAssignment).options(selectinload(UserRoleAssignment.role))

        result = await db.exec(stmt)
        return list(result.all())

    async def get_user_permissions_for_scope(
        self,
        user_id: UUID | str,
        scope_type: str,
        scope_id: UUID | str | None,
        db: AsyncSession,
    ) -> list[Permission]:
        """Get all permissions a user has for a specific scope.

        Args:
            user_id: The user's ID (UUID or string)
            scope_type: Scope type (e.g., "Flow", "Project", "Global")
            scope_id: Specific resource ID (None for Global scope, UUID or string)
            db: Database session

        Returns:
            list[Permission]: List of permissions user has for the scope
        """
        # Convert string UUIDs to UUID objects
        if isinstance(user_id, str):
            user_id = UUID(user_id)
        if isinstance(scope_id, str):
            scope_id = UUID(scope_id)

        role = await self._get_user_role_for_scope(user_id, scope_type, scope_id, db)

        if not role:
            return []

        stmt = (
            select(Permission)
            .join(RolePermission)
            .where(
                RolePermission.role_id == role.id,
                Permission.scope == scope_type,
            )
        )

        result = await db.exec(stmt)
        return list(result.all())

    async def batch_can_access(
        self,
        user_id: UUID | str,
        checks: list[dict],
        db: AsyncSession,
    ) -> list[bool]:
        """Optimized batch permission check using a single SQL query.

        This method performs all permission checks in a single database query using JOINs,
        avoiding the N+1 query problem of sequential can_access() calls.

        Args:
            user_id: The user's ID (UUID or string)
            checks: List of dicts with keys: permission_name, scope_type, scope_id
            db: Database session

        Returns:
            list[bool]: List of permission results in the same order as checks

        Performance:
            - Single database query regardless of number of checks
            - Uses SQL JOINs for efficient data retrieval
            - Processes results in-memory for fast lookup
            - Target: <100ms for 10 resources, <500ms for 50 resources
        """
        if not checks:
            return []

        # Convert string UUID to UUID object
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        # 1. Check superuser bypass (single query)
        user = await get_user_by_id(db, user_id)
        if user and user.is_superuser:
            # Superuser has all permissions
            return [True] * len(checks)

        # 2. Check Global Admin role bypass (single query)
        if await self._has_global_admin_role(user_id, db):
            # Global Admin has all permissions
            return [True] * len(checks)

        # 3. Extract unique scope combinations for batch fetching
        # Group by (scope_type, scope_id) to avoid duplicate queries
        scope_combinations = set()
        for check in checks:
            scope_type = check["scope_type"]
            scope_id = check.get("scope_id")
            # Convert string scope_id to UUID if needed
            if isinstance(scope_id, str):
                scope_id = UUID(scope_id)
            scope_combinations.add((scope_type, scope_id))

        # 4. Batch fetch all role assignments for the user with all relevant scopes
        # Build a query that fetches all assignments for this user
        from sqlalchemy import or_

        scope_conditions = []
        for scope_type, scope_id in scope_combinations:
            scope_conditions.append(
                (UserRoleAssignment.scope_type == scope_type) & (UserRoleAssignment.scope_id == scope_id)
            )

        # Add inherited Flow->Project relationships
        # We need to handle Flow scope inheritance, so fetch Project assignments too
        flow_scope_ids = [scope_id for scope_type, scope_id in scope_combinations if scope_type == "Flow"]
        if flow_scope_ids:
            # Fetch the project IDs for these flows
            flow_stmt = select(Flow).where(Flow.id.in_(flow_scope_ids))
            flow_result = await db.exec(flow_stmt)
            flows = list(flow_result.all())
            scope_conditions.extend(
                (UserRoleAssignment.scope_type == "Project") & (UserRoleAssignment.scope_id == flow.folder_id)
                for flow in flows
                if flow.folder_id
            )

        # Fetch all relevant role assignments in a single query
        if scope_conditions:
            stmt = (
                select(UserRoleAssignment)
                .where(
                    UserRoleAssignment.user_id == user_id,
                    or_(*scope_conditions),
                )
                .options(selectinload(UserRoleAssignment.role))
            )
            result = await db.exec(stmt)
            assignments = list(result.all())
        else:
            assignments = []

        # Build a map of (scope_type, scope_id) -> role_id
        scope_to_role: dict[tuple[str, UUID | None], UUID] = {}
        for assignment in assignments:
            key = (assignment.scope_type, assignment.scope_id)
            scope_to_role[key] = assignment.role_id

        # Handle Flow inheritance: if Flow has no direct assignment, check Project
        if flow_scope_ids:
            for flow in flows:
                flow_key = ("Flow", flow.id)
                if flow_key not in scope_to_role and flow.folder_id:
                    project_key = ("Project", flow.folder_id)
                    if project_key in scope_to_role:
                        scope_to_role[flow_key] = scope_to_role[project_key]

        # 5. Fetch all permissions for the roles found (single query with JOIN)
        role_ids = list(set(scope_to_role.values()))
        if role_ids:
            perm_stmt = select(RolePermission, Permission).join(Permission).where(RolePermission.role_id.in_(role_ids))
            perm_result = await db.exec(perm_stmt)
            role_permissions_data = list(perm_result.all())

            # Build a map of (role_id, permission_name, scope_type) -> True
            role_perm_map: dict[tuple[UUID, str, str], bool] = {}
            for role_perm, permission in role_permissions_data:
                key = (role_perm.role_id, permission.name, permission.scope)
                role_perm_map[key] = True
        else:
            role_perm_map = {}

        # 6. Process each check using the in-memory maps
        results = []
        for check in checks:
            permission_name = check["permission_name"]
            scope_type = check["scope_type"]
            scope_id = check.get("scope_id")

            # Convert string scope_id to UUID if needed
            if isinstance(scope_id, str):
                scope_id = UUID(scope_id)

            # Look up the role for this scope
            scope_key = (scope_type, scope_id)
            role_id = scope_to_role.get(scope_key)

            if not role_id:
                results.append(False)
                continue

            # Check if the role has the permission
            perm_key = (role_id, permission_name, scope_type)
            has_permission = perm_key in role_perm_map
            results.append(has_permission)

        return results
