"""Performance tests for RBAC batch permission checks.

This module contains performance benchmarks for batch permission check operations
in the RBAC system. It verifies that batch permission checks meet performance
requirements for efficient frontend rendering scenarios.

Batch permission checks are used when the frontend needs to determine
visibility/accessibility of multiple resources in a single request,
such as when rendering a list of flows with action buttons.

Test Scenarios:
1. Batch permission check for multiple flows (10, 50, 100 resources)
2. Batch permission check for mixed resource types
3. Sequential vs batch check comparison
4. Batch check with varying role complexity
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


def print_latency_report(test_name: str, stats: dict[str, float], target_ms: float = 100) -> None:
    """Print a formatted latency report.

    Args:
        test_name: Name of the test being reported
        stats: Dictionary of latency statistics
        target_ms: Target p95 latency in milliseconds
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
    print(f"P95:     {stats.get('p95', 0):.4f} ms (Target: <{target_ms}ms)")
    print(f"P99:     {stats.get('p99', 0):.4f} ms")
    print(f"{'=' * 60}")


async def batch_permission_check(
    rbac_service: RBACService,
    user_id,
    checks: list[dict],
    db: AsyncSession,
) -> list[dict]:
    """Perform batch permission checks.

    This simulates the batch permission check API endpoint functionality.

    Args:
        rbac_service: The RBAC service instance
        user_id: User ID to check permissions for
        checks: List of permission checks with action, resource_type, resource_id
        db: Database session

    Returns:
        List of results with action, resource_type, resource_id, allowed
    """
    results = []
    for check in checks:
        has_permission = await rbac_service.can_access(
            user_id,
            check["action"],
            check["resource_type"],
            check.get("resource_id"),
            db,
        )
        results.append(
            {
                "action": check["action"],
                "resource_type": check["resource_type"],
                "resource_id": check.get("resource_id"),
                "allowed": has_permission,
            }
        )
    return results


@pytest.mark.performance
@pytest.mark.asyncio
class TestBatchPermissionCheckLatency:
    """Performance tests for batch permission check operations.

    PRD Requirement (Epic 5):
    - Batch permission check for multiple resources
    - Target: <100ms for 10 permission checks

    These tests simulate real-world scenarios where the frontend needs
    to check permissions for multiple resources in a single request.
    """

    WARMUP_ITERATIONS = 5
    BENCHMARK_ITERATIONS = 100

    async def test_batch_check_10_resources(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test batch permission check for 10 resources.

        Gherkin Scenario: Batch Permission Check (10 Resources)
        Given a user with Project-level Editor role
        And 10 flows in the project
        When the frontend requests permission checks for all 10 flows
        Then the response should be returned in less than 100ms (p95)
        """
        # Create user with Project-level Editor role
        user = User(
            username=f"batch_user_10_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        # Assign Editor role on project
        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Editor",
            scope_type="Project",
            scope_id=perf_test_project.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        # Create 10 flows
        flows = []
        for i in range(10):
            flow = Flow(
                name=f"BatchFlow10_{i}_{uuid4().hex[:8]}",
                description=f"Flow {i} for batch check test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            flows.append(flow)

        await perf_db_session.commit()
        for flow in flows:
            await perf_db_session.refresh(flow)

        # Prepare batch check requests
        checks = [{"action": "Read", "resource_type": "Flow", "resource_id": flow.id} for flow in flows]

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

            # All checks should pass (Editor has Read permission)
            assert len(results) == 10
            assert all(r["allowed"] for r in results)

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - 10 Resources", stats, target_ms=100)

        # Assert p95 < 100ms for 10 resources
        assert stats["p95"] < 100, (
            f"Batch check (10 resources) p95 latency {stats['p95']:.2f}ms exceeds 100ms requirement"
        )

    async def test_batch_check_50_resources(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test batch permission check for 50 resources.

        Gherkin Scenario: Batch Permission Check (50 Resources)
        Given a user with Project-level role
        And 50 flows in the project
        When the frontend requests permission checks for all 50 flows
        Then the response should be returned in reasonable time
        """
        # Create user with Project-level Viewer role
        user = User(
            username=f"batch_user_50_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Viewer",
            scope_type="Project",
            scope_id=perf_test_project.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        # Create 50 flows
        flows = []
        for i in range(50):
            flow = Flow(
                name=f"BatchFlow50_{i}_{uuid4().hex[:8]}",
                description=f"Flow {i} for batch check test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            flows.append(flow)

        await perf_db_session.commit()
        for flow in flows:
            await perf_db_session.refresh(flow)

        # Prepare batch check requests
        checks = [{"action": "Read", "resource_type": "Flow", "resource_id": flow.id} for flow in flows]

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)
            assert len(results) == 50

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - 50 Resources", stats, target_ms=500)

        # Assert p95 < 500ms for 50 resources (5x the 10-resource target)
        assert stats["p95"] < 500, (
            f"Batch check (50 resources) p95 latency {stats['p95']:.2f}ms exceeds 500ms requirement"
        )

    async def test_batch_check_100_resources(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        multiple_flows_for_perf: list[Flow],
    ):
        """Test batch permission check for 100 resources.

        Gherkin Scenario: Batch Permission Check (100 Resources - Maximum)
        Given a user with Global Admin role
        And 100 flows exist
        When the frontend requests permission checks for all 100 flows
        Then the response should be returned in reasonable time

        Note: This tests the maximum batch size allowed by the API (100).
        """
        # Create user with Global Admin role for fastest path
        user = User(
            username=f"batch_user_100_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Admin",
            scope_type="Global",
            scope_id=None,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        flows = multiple_flows_for_perf

        # Prepare batch check requests
        checks = [{"action": "Read", "resource_type": "Flow", "resource_id": flow.id} for flow in flows]

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

            # Admin should have all permissions
            assert len(results) == 100
            assert all(r["allowed"] for r in results)

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - 100 Resources", stats, target_ms=1000)

        # Assert p95 < 1000ms for 100 resources (10x the 10-resource target)
        assert stats["p95"] < 1000, (
            f"Batch check (100 resources) p95 latency {stats['p95']:.2f}ms exceeds 1000ms requirement"
        )

    async def test_batch_check_mixed_permissions(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Test batch permission check with mixed permission types.

        Gherkin Scenario: Batch Permission Check (Mixed Actions)
        Given a user with Editor role
        When the frontend checks Create, Read, Update, Delete permissions on flows
        Then the response should correctly identify allowed/denied permissions
        """
        # Create user with Editor role
        user = User(
            username=f"batch_user_mixed_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Editor",
            scope_type="Project",
            scope_id=perf_test_project.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        # Create flows
        flows = []
        for i in range(5):
            flow = Flow(
                name=f"BatchFlowMixed_{i}_{uuid4().hex[:8]}",
                description=f"Flow {i} for mixed batch test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            flows.append(flow)

        await perf_db_session.commit()
        for flow in flows:
            await perf_db_session.refresh(flow)

        # Prepare mixed permission checks (all CRUD actions for each flow)
        checks = []
        for flow in flows:
            for action in ["Create", "Read", "Update", "Delete"]:
                checks.append(
                    {
                        "action": action,
                        "resource_type": "Flow",
                        "resource_id": flow.id,
                    }
                )

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

            # Verify correct permission results
            assert len(results) == 20  # 5 flows x 4 actions
            for result in results:
                if result["action"] == "Delete":
                    # Editor does NOT have Delete permission
                    assert result["allowed"] is False
                else:
                    # Editor has Create, Read, Update permissions
                    assert result["allowed"] is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - Mixed Permissions (20 checks)", stats, target_ms=200)

        # Assert p95 < 200ms for 20 mixed checks
        assert stats["p95"] < 200, f"Batch check (mixed 20) p95 latency {stats['p95']:.2f}ms exceeds 200ms requirement"

    async def test_batch_check_mixed_resource_types(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
        perf_test_flow: Flow,
    ):
        """Test batch permission check with mixed resource types.

        Gherkin Scenario: Batch Permission Check (Mixed Resource Types)
        Given a user with roles on both Project and Flow
        When the frontend checks permissions on mixed resource types
        Then the response should be returned efficiently
        """
        user = User(
            username=f"batch_user_types_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        # Assign different roles for different scopes
        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Editor",
            scope_type="Project",
            scope_id=perf_test_project.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Owner",
            scope_type="Flow",
            scope_id=perf_test_flow.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        # Prepare checks for both Project and Flow
        checks = [
            {"action": "Read", "resource_type": "Project", "resource_id": perf_test_project.id},
            {"action": "Update", "resource_type": "Project", "resource_id": perf_test_project.id},
            {"action": "Delete", "resource_type": "Project", "resource_id": perf_test_project.id},
            {"action": "Read", "resource_type": "Flow", "resource_id": perf_test_flow.id},
            {"action": "Update", "resource_type": "Flow", "resource_id": perf_test_flow.id},
            {"action": "Delete", "resource_type": "Flow", "resource_id": perf_test_flow.id},
        ]

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

            # Verify correct results
            assert len(results) == 6
            # Project: Editor has Read, Update but not Delete
            assert results[0]["allowed"] is True  # Project Read
            assert results[1]["allowed"] is True  # Project Update
            assert results[2]["allowed"] is False  # Project Delete (Editor can't delete)
            # Flow: Owner has all permissions
            assert results[3]["allowed"] is True  # Flow Read
            assert results[4]["allowed"] is True  # Flow Update
            assert results[5]["allowed"] is True  # Flow Delete

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - Mixed Resource Types", stats, target_ms=100)

        # Assert p95 < 100ms
        assert stats["p95"] < 100, (
            f"Batch check (mixed types) p95 latency {stats['p95']:.2f}ms exceeds 100ms requirement"
        )

    async def test_sequential_vs_batch_comparison(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_project: Folder,
    ):
        """Compare sequential permission checks vs batch approach.

        This test demonstrates the efficiency of batch permission checking
        compared to making individual API calls.
        """
        user = User(
            username=f"batch_compare_{uuid4().hex[:8]}",
            password=get_password_hash("testpassword"),
            is_active=True,
            is_superuser=False,
        )
        perf_db_session.add(user)
        await perf_db_session.commit()
        await perf_db_session.refresh(user)

        await rbac_service.assign_role(
            user_id=user.id,
            role_name="Editor",
            scope_type="Project",
            scope_id=perf_test_project.id,
            created_by=perf_superuser.id,
            db=perf_db_session,
        )

        # Create 10 flows
        flows = []
        for i in range(10):
            flow = Flow(
                name=f"BatchCompare_{i}_{uuid4().hex[:8]}",
                description=f"Flow {i} for comparison test",
                user_id=perf_superuser.id,
                folder_id=perf_test_project.id,
                data={},
            )
            perf_db_session.add(flow)
            flows.append(flow)

        await perf_db_session.commit()
        for flow in flows:
            await perf_db_session.refresh(flow)

        # Measure sequential checks (simulating 10 individual API calls)
        sequential_latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            total_time = 0
            for flow in flows:
                start = time.perf_counter()
                await rbac_service.can_access(user.id, "Read", "Flow", flow.id, perf_db_session)
                end = time.perf_counter()
                total_time += (end - start) * 1000

            sequential_latencies.append(total_time)

        # Measure batch check
        checks = [{"action": "Read", "resource_type": "Flow", "resource_id": flow.id} for flow in flows]

        batch_latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            await batch_permission_check(rbac_service, user.id, checks, perf_db_session)
            end = time.perf_counter()
            batch_latencies.append((end - start) * 1000)

        sequential_stats = calculate_latency_stats(sequential_latencies)
        batch_stats = calculate_latency_stats(batch_latencies)

        print("\n" + "=" * 60)
        print("Sequential vs Batch Permission Check Comparison")
        print("=" * 60)
        print_latency_report("Sequential (10 individual calls)", sequential_stats)
        print_latency_report("Batch (1 combined call)", batch_stats)

        improvement = ((sequential_stats["mean"] - batch_stats["mean"]) / sequential_stats["mean"]) * 100
        print(f"\nBatch approach improvement: {improvement:.1f}% faster (mean)")
        print("=" * 60)

        # Both should meet performance requirements
        assert batch_stats["p95"] < 100, "Batch check should be under 100ms"

    async def test_batch_check_superuser_fast_path(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        multiple_flows_for_perf: list[Flow],
    ):
        """Test batch permission check with superuser (fast bypass path).

        This test verifies that superuser bypass provides consistent
        fast performance even for large batch sizes.
        """
        flows = multiple_flows_for_perf[:50]  # Use 50 flows

        checks = [{"action": "Delete", "resource_type": "Flow", "resource_id": flow.id} for flow in flows]

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await batch_permission_check(rbac_service, perf_superuser.id, checks, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            results = await batch_permission_check(rbac_service, perf_superuser.id, checks, perf_db_session)
            end = time.perf_counter()

            latencies.append((end - start) * 1000)

            # Superuser should have all permissions
            assert len(results) == 50
            assert all(r["allowed"] for r in results)

        stats = calculate_latency_stats(latencies)
        print_latency_report("Batch Check - Superuser Fast Path (50 resources)", stats, target_ms=250)

        # Superuser should be faster due to early bypass
        # Target: <250ms for 50 resources (should be much faster due to bypass)
        assert stats["p95"] < 250, f"Batch check (superuser 50) p95 latency {stats['p95']:.2f}ms exceeds 250ms"
