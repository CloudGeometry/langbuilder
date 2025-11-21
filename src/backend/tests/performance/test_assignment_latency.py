"""Performance tests for RBAC assignment creation latency.

This module contains performance benchmarks for role assignment operations
in the RBACService. It verifies that assignment operations meet the
performance requirements specified in Epic 5 of the PRD:
- Assignment creation latency: <200ms p95

Test Scenarios:
1. assign_role() for Flow scope
2. assign_role() for Project scope
3. assign_role() for Global scope
4. update_role() for existing assignment
5. remove_role() for assignment deletion
6. list_user_assignments() for assignment retrieval
"""

from __future__ import annotations

import time
from statistics import mean, quantiles, stdev
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from langbuilder.services.auth.utils import get_password_hash
from langbuilder.services.database.models.flow.model import Flow
from langbuilder.services.database.models.folder.model import Folder
from langbuilder.services.database.models.user.model import User

if TYPE_CHECKING:
    from langbuilder.services.rbac.service import RBACService
    from sqlmodel.ext.asyncio.session import AsyncSession


def calculate_latency_stats(latencies: list[float]) -> dict[str, float]:
    """Calculate comprehensive latency statistics.

    Args:
        latencies: List of latency measurements in milliseconds

    Returns:
        Dictionary with min, max, mean, stdev, p50, p95, p99 values
    """
    if not latencies:
        return {}

    sorted_latencies = sorted(latencies)
    percentiles = quantiles(sorted_latencies, n=100) if len(sorted_latencies) >= 100 else []

    return {
        "min": min(latencies),
        "max": max(latencies),
        "mean": mean(latencies),
        "stdev": stdev(latencies) if len(latencies) > 1 else 0.0,
        "p50": percentiles[49] if len(percentiles) >= 50 else sorted_latencies[len(sorted_latencies) // 2],
        "p95": percentiles[94] if len(percentiles) >= 95 else sorted_latencies[int(len(sorted_latencies) * 0.95)],
        "p99": percentiles[98] if len(percentiles) >= 99 else sorted_latencies[int(len(sorted_latencies) * 0.99)],
        "count": len(latencies),
    }


def print_latency_report(test_name: str, stats: dict[str, float]) -> None:
    """Print a formatted latency report.

    Args:
        test_name: Name of the test being reported
        stats: Dictionary of latency statistics
    """
    print(f"\n{'=' * 60}")
    print(f"Performance Report: {test_name}")
    print(f"{'=' * 60}")
    print(f"Sample Count: {stats.get('count', 0)}")
    print(f"Min:     {stats.get('min', 0):.4f} ms")
    print(f"Max:     {stats.get('max', 0):.4f} ms")
    print(f"Mean:    {stats.get('mean', 0):.4f} ms")
    print(f"Std Dev: {stats.get('stdev', 0):.4f} ms")
    print(f"P50:     {stats.get('p50', 0):.4f} ms")
    print(f"P95:     {stats.get('p95', 0):.4f} ms (Target: <200ms)")
    print(f"P99:     {stats.get('p99', 0):.4f} ms")
    print(f"{'=' * 60}")


@pytest.mark.performance
@pytest.mark.asyncio
class TestAssignmentLatency:
    """Performance tests for role assignment operations.

    PRD Requirement (Epic 5):
    - Assignment creation latency: <200ms p95
    """

    # Number of iterations for benchmarking
    # Note: Assignment creation is more expensive than permission checks
    # so we use fewer iterations
    WARMUP_ITERATIONS = 5
    BENCHMARK_ITERATIONS = 100

    async def test_assign_role_flow_scope_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test assign_role() latency for Flow scope.

        Gherkin Scenario: Latency for Assignment Creation (Flow Scope)
        Given an Admin creates a role assignment for a Flow
        When the Core Role Assignment Logic is executed
        Then the API response time should be less than 200 milliseconds (p95)
        """
        # Create test users and flows for each iteration
        latencies = []

        for i in range(self.BENCHMARK_ITERATIONS):
            # Create a new user for each iteration
            user = User(
                username=f"perf_user_flow_{i}_{uuid4().hex[:8]}",
                password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
            )
            perf_db_session.add(user)

            # Create a new flow for each iteration
            flow = Flow(
                name=f"PerfFlow_{i}_{uuid4().hex[:8]}",
                description="Flow for assignment latency test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            await perf_db_session.commit()
            await perf_db_session.refresh(user)
            await perf_db_session.refresh(flow)

            # Benchmark assignment creation
            start = time.perf_counter()
            assignment = await rbac_service.assign_role(
                user_id=user.id,
                role_name="Viewer",
                scope_type="Flow",
                scope_id=flow.id,
                created_by=perf_superuser.id,
                db=perf_db_session,
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)  # Convert to ms
            assert assignment is not None
            assert assignment.scope_type == "Flow"

        stats = calculate_latency_stats(latencies)
        print_latency_report("assign_role() - Flow Scope", stats)

        # Assert p95 < 200ms
        assert stats["p95"] < 200, f"assign_role() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_assign_role_project_scope_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
    ):
        """Test assign_role() latency for Project scope.

        Gherkin Scenario: Latency for Assignment Creation (Project Scope)
        Given an Admin creates a role assignment for a Project
        When the Core Role Assignment Logic is executed
        Then the API response time should be less than 200 milliseconds (p95)
        """
        latencies = []

        for i in range(self.BENCHMARK_ITERATIONS):
            # Create a new user for each iteration
            user = User(
                username=f"perf_user_project_{i}_{uuid4().hex[:8]}",
                password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
            )
            perf_db_session.add(user)

            # Create a new project for each iteration
            project = Folder(
                name=f"PerfProject_{i}_{uuid4().hex[:8]}",
                description="Project for assignment latency test",
                user_id=perf_superuser.id,
            )
            perf_db_session.add(project)
            await perf_db_session.commit()
            await perf_db_session.refresh(user)
            await perf_db_session.refresh(project)

            # Benchmark assignment creation
            start = time.perf_counter()
            assignment = await rbac_service.assign_role(
                user_id=user.id,
                role_name="Editor",
                scope_type="Project",
                scope_id=project.id,
                created_by=perf_superuser.id,
                db=perf_db_session,
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert assignment is not None
            assert assignment.scope_type == "Project"

        stats = calculate_latency_stats(latencies)
        print_latency_report("assign_role() - Project Scope", stats)

        # Assert p95 < 200ms
        assert stats["p95"] < 200, f"assign_role() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_assign_role_global_scope_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
    ):
        """Test assign_role() latency for Global scope.

        Gherkin Scenario: Latency for Assignment Creation (Global Scope)
        Given an Admin creates a Global Admin role assignment
        When the Core Role Assignment Logic is executed
        Then the API response time should be less than 200 milliseconds (p95)
        """
        latencies = []

        for i in range(self.BENCHMARK_ITERATIONS):
            # Create a new user for each iteration
            user = User(
                username=f"perf_user_global_{i}_{uuid4().hex[:8]}",
                password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
            )
            perf_db_session.add(user)
            await perf_db_session.commit()
            await perf_db_session.refresh(user)

            # Benchmark assignment creation
            start = time.perf_counter()
            assignment = await rbac_service.assign_role(
                user_id=user.id,
                role_name="Admin",
                scope_type="Global",
                scope_id=None,
                created_by=perf_superuser.id,
                db=perf_db_session,
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert assignment is not None
            assert assignment.scope_type == "Global"
            assert assignment.scope_id is None

        stats = calculate_latency_stats(latencies)
        print_latency_report("assign_role() - Global Scope", stats)

        # Assert p95 < 200ms
        assert stats["p95"] < 200, f"assign_role() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_update_role_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test update_role() latency for changing role on existing assignment.

        Gherkin Scenario: Latency for Assignment Update
        Given an existing role assignment
        When the Admin changes the role
        Then the API response time should be less than 200 milliseconds (p95)
        """
        # Create assignments first
        assignments = []
        for i in range(self.BENCHMARK_ITERATIONS):
            user = User(
                username=f"perf_user_update_{i}_{uuid4().hex[:8]}",
                password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
            )
            perf_db_session.add(user)

            flow = Flow(
                name=f"PerfFlowUpdate_{i}_{uuid4().hex[:8]}",
                description="Flow for update latency test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            await perf_db_session.commit()
            await perf_db_session.refresh(user)
            await perf_db_session.refresh(flow)

            # Create initial assignment with Viewer role
            assignment = await rbac_service.assign_role(
                user_id=user.id,
                role_name="Viewer",
                scope_type="Flow",
                scope_id=flow.id,
                created_by=perf_superuser.id,
                db=perf_db_session,
            )
            assignments.append(assignment)

        # Benchmark role updates
        latencies = []
        for assignment in assignments:
            start = time.perf_counter()
            updated = await rbac_service.update_role(
                assignment_id=assignment.id,
                new_role_name="Editor",
                db=perf_db_session,
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert updated is not None

        stats = calculate_latency_stats(latencies)
        print_latency_report("update_role()", stats)

        # Assert p95 < 200ms
        assert stats["p95"] < 200, f"update_role() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_remove_role_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test remove_role() latency for deleting assignments.

        Gherkin Scenario: Latency for Assignment Deletion
        Given an existing role assignment
        When the Admin deletes the assignment
        Then the API response time should be less than 200 milliseconds (p95)
        """
        # Create assignments first
        assignments = []
        for i in range(self.BENCHMARK_ITERATIONS):
            user = User(
                username=f"perf_user_remove_{i}_{uuid4().hex[:8]}",
                password=get_password_hash("testpassword"),
                is_active=True,
                is_superuser=False,
            )
            perf_db_session.add(user)

            flow = Flow(
                name=f"PerfFlowRemove_{i}_{uuid4().hex[:8]}",
                description="Flow for remove latency test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            await perf_db_session.commit()
            await perf_db_session.refresh(user)
            await perf_db_session.refresh(flow)

            # Create assignment (not immutable so it can be deleted)
            assignment = await rbac_service.assign_role(
                user_id=user.id,
                role_name="Viewer",
                scope_type="Flow",
                scope_id=flow.id,
                created_by=perf_superuser.id,
                db=perf_db_session,
                is_immutable=False,
            )
            assignments.append(assignment)

        # Benchmark role removal
        latencies = []
        for assignment in assignments:
            start = time.perf_counter()
            await rbac_service.remove_role(
                assignment_id=assignment.id,
                db=perf_db_session,
            )
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

        stats = calculate_latency_stats(latencies)
        print_latency_report("remove_role()", stats)

        # Assert p95 < 200ms
        assert stats["p95"] < 200, f"remove_role() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_list_user_assignments_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test list_user_assignments() latency.

        Gherkin Scenario: Latency for Assignment Listing
        Given a user with multiple role assignments
        When the Admin lists the user's assignments
        Then the API response time should be reasonable
        """
        # Create a user with multiple assignments
        user = User(
            username=f"perf_user_list_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        # Create 20 assignments for the user
        for i in range(20):
            flow = Flow(
                name=f"PerfFlowList_{i}_{uuid4().hex[:8]}",
                description="Flow for list latency test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            await perf_db_session.commit()
            await perf_db_session.refresh(flow)

            await rbac_service.assign_role(
                user_id=user.id,
                role_name="Viewer",
                scope_type="Flow",
                scope_id=flow.id,
                created_by=perf_superuser.id,
                db=perf_db_session,
            )

        # Warm up
        for _ in range(5):
            await rbac_service.list_user_assignments(user.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            assignments = await rbac_service.list_user_assignments(user.id, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert len(assignments) == 20

        stats = calculate_latency_stats(latencies)
        print_latency_report("list_user_assignments()", stats)

        # Assert p95 < 200ms (generous for list operations)
        assert stats["p95"] < 200, f"list_user_assignments() p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_get_user_permissions_for_scope_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_user_with_flow_role: User,
        perf_test_flow: Flow,
    ):
        """Test get_user_permissions_for_scope() latency.

        This tests the latency of retrieving all permissions a user has
        for a specific scope.
        """
        user = perf_user_with_flow_role
        flow = perf_test_flow

        # Warm up
        for _ in range(10):
            await rbac_service.get_user_permissions_for_scope(user.id, "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS * 10):  # More iterations for this lighter operation
            start = time.perf_counter()
            permissions = await rbac_service.get_user_permissions_for_scope(user.id, "Flow", flow.id, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert len(permissions) > 0  # Owner has all permissions

        stats = calculate_latency_stats(latencies)
        print_latency_report("get_user_permissions_for_scope()", stats)

        # Assert p95 < 50ms (similar to can_access requirement)
        assert stats["p95"] < 50, (
            f"get_user_permissions_for_scope() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"
        )
