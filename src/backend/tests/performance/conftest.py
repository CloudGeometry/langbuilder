"""Conftest for RBAC performance tests.

This module provides fixtures for performance testing of the RBAC system.
It sets up test database, users, roles, permissions, and flows needed
for benchmarking permission checks and role assignments.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from langbuilder.services.auth.utils import get_password_hash
from langbuilder.services.database.models.flow.model import Flow
from langbuilder.services.database.models.folder.model import Folder
from langbuilder.services.database.models.role.seed_data import seed_rbac_data
from langbuilder.services.database.models.user.model import User
from langbuilder.services.deps import get_db_service
from langbuilder.services.rbac.service import RBACService

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlmodel.ext.asyncio.session import AsyncSession


def pytest_configure(config):
    """Register custom markers for performance tests."""
    config.addinivalue_line(
        "markers",
        "performance: mark test as a performance test (latency benchmarks)",
    )


@pytest.fixture(autouse=True)
def setup_performance_database(tmp_path, monkeypatch):
    """Setup a temporary database URL for performance testing."""
    from langbuilder.services.deps import get_settings_service

    settings_service = get_settings_service()
    db_path = tmp_path / "test_performance.db"
    test_db_url = f"sqlite:///{db_path}"
    monkeypatch.setenv("LANGBUILDER_DATABASE_URL", test_db_url)
    monkeypatch.setenv("LANGBUILDER_AUTO_LOGIN", "false")
    settings_service.set("database_url", test_db_url)

    # Clear service caches
    from langbuilder.services.manager import service_manager

    service_manager.factories.clear()
    service_manager.services.clear()

    yield

    monkeypatch.undo()


@pytest.fixture
async def perf_db_session(setup_performance_database) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for performance tests.

    This fixture initializes the database, seeds RBAC data, and provides
    a session for test use.
    """
    from langbuilder.services.utils import initialize_services

    # Initialize services and database
    await initialize_services(fix_migration=False)

    db_service = get_db_service()
    async with db_service.with_session() as session:
        # Seed RBAC data (roles, permissions, role_permissions)
        await seed_rbac_data(session)
        yield session


@pytest.fixture
async def rbac_service() -> RBACService:
    """Provide an instance of RBACService for performance tests."""
    return RBACService()


@pytest.fixture
async def perf_test_user(perf_db_session: AsyncSession) -> User:
    """Create a test user for performance benchmarks."""
    user = User(
        username=f"perfuser_{uuid4().hex[:8]}",
        password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
    )
    perf_db_session.add(user)
    await perf_db_session.commit()
    await perf_db_session.refresh(user)
    return user


@pytest.fixture
async def perf_superuser(perf_db_session: AsyncSession) -> User:
    """Create a superuser for performance benchmarks."""
    user = User(
        username=f"perfsuperuser_{uuid4().hex[:8]}",
        password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=True,
    )
    perf_db_session.add(user)
    await perf_db_session.commit()
    await perf_db_session.refresh(user)
    return user


@pytest.fixture
async def perf_admin_user(
    perf_db_session: AsyncSession,
    rbac_service: RBACService,
) -> User:
    """Create a user with Global Admin role for performance benchmarks."""
    user = User(
        username=f"perfadmin_{uuid4().hex[:8]}",
        password=get_password_hash("testpassword"),
        is_active=True,
        is_superuser=False,
    )
    perf_db_session.add(user)
    await perf_db_session.commit()
    await perf_db_session.refresh(user)

    # Assign Global Admin role
    await rbac_service.assign_role(
        user_id=user.id,
        role_name="Admin",
        scope_type="Global",
        scope_id=None,
        created_by=user.id,
        db=perf_db_session,
    )

    return user


@pytest.fixture
async def perf_test_project(
    perf_db_session: AsyncSession,
    perf_test_user: User,
) -> Folder:
    """Create a test project (folder) for performance benchmarks."""
    folder = Folder(
        name=f"PerfTestProject_{uuid4().hex[:8]}",
        description="Project for performance testing",
        user_id=perf_test_user.id,
    )
    perf_db_session.add(folder)
    await perf_db_session.commit()
    await perf_db_session.refresh(folder)
    return folder


@pytest.fixture
async def perf_test_flow(
    perf_db_session: AsyncSession,
    perf_test_user: User,
    perf_test_project: Folder,
) -> Flow:
    """Create a test flow for performance benchmarks."""
    flow = Flow(
        name=f"PerfTestFlow_{uuid4().hex[:8]}",
        description="Flow for performance testing",
        user_id=perf_test_user.id,
        folder_id=perf_test_project.id,
        data={},
    )
    perf_db_session.add(flow)
    await perf_db_session.commit()
    await perf_db_session.refresh(flow)
    return flow


@pytest.fixture
async def perf_user_with_flow_role(
    perf_db_session: AsyncSession,
    perf_test_user: User,
    perf_test_flow: Flow,
    rbac_service: RBACService,
    perf_superuser: User,
) -> User:
    """Create a test user with Owner role on a specific flow."""
    await rbac_service.assign_role(
        user_id=perf_test_user.id,
        role_name="Owner",
        scope_type="Flow",
        scope_id=perf_test_flow.id,
        created_by=perf_superuser.id,
        db=perf_db_session,
    )
    return perf_test_user


@pytest.fixture
async def perf_user_with_project_role(
    perf_db_session: AsyncSession,
    perf_test_user: User,
    perf_test_project: Folder,
    rbac_service: RBACService,
    perf_superuser: User,
) -> User:
    """Create a test user with Editor role on a specific project."""
    await rbac_service.assign_role(
        user_id=perf_test_user.id,
        role_name="Editor",
        scope_type="Project",
        scope_id=perf_test_project.id,
        created_by=perf_superuser.id,
        db=perf_db_session,
    )
    return perf_test_user


@pytest.fixture
async def multiple_flows_for_perf(
    perf_db_session: AsyncSession,
    perf_test_user: User,
    perf_test_project: Folder,
) -> list[Flow]:
    """Create multiple flows for batch permission check performance tests."""
    flows = []
    for i in range(100):
        flow = Flow(
            name=f"PerfFlow_{i}_{uuid4().hex[:8]}",
            description=f"Flow {i} for batch performance testing",
            user_id=perf_test_user.id,
            folder_id=perf_test_project.id,
            data={},
        )
        perf_db_session.add(flow)
        flows.append(flow)

    await perf_db_session.commit()
    for flow in flows:
        await perf_db_session.refresh(flow)

    return flows
