"""Performance tests for RBAC can_access() latency.

This module contains performance benchmarks for the can_access() method
of the RBACService. It verifies that permission checks meet the
performance requirements specified in Epic 5 of the PRD:
- can_access() latency: <50ms p95

Test Scenarios:
1. can_access() for user with direct Flow-level role
2. can_access() for user with inherited Project-level role (Flow access)
3. can_access() for superuser (bypass path)
4. can_access() for Global Admin role (bypass path)
5. can_access() for user without permission (negative path)
"""

from __future__ import annotations

import time
from statistics import mean, quantiles, stdev
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from langbuilder.services.database.models.flow.model import Flow
    from langbuilder.services.database.models.folder.model import Folder
    from langbuilder.services.database.models.user.model import User
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
    percentiles = quantiles(sorted_latencies, n=100)

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
    print(f"P95:     {stats.get('p95', 0):.4f} ms (Target: <50ms)")
    print(f"P99:     {stats.get('p99', 0):.4f} ms")
    print(f"{'=' * 60}")


@pytest.mark.performance
@pytest.mark.asyncio
class TestCanAccessLatency:
    """Performance tests for can_access() method.

    PRD Requirement (Epic 5):
    - can_access() latency: <50ms p95
    """

    # Number of iterations for benchmarking
    WARMUP_ITERATIONS = 10
    BENCHMARK_ITERATIONS = 1000

    async def test_can_access_direct_flow_role_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_user_with_flow_role: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency for user with direct Flow-level role.

        Gherkin Scenario: Latency for CanAccess Check (Direct Flow Role)
        Given a user has an Owner role on a specific Flow
        When the AuthService.CanAccess method is called for Read permission
        Then the check must return a response in less than 50 milliseconds (p95)
        """
        user = perf_user_with_flow_role
        flow = perf_test_flow

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Read", "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Read", "Flow", flow.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - Direct Flow Role", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_inherited_project_role_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_user_with_project_role: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency for user with inherited Project-level role.

        Gherkin Scenario: Latency for CanAccess Check (Inherited Project Role)
        Given a user has an Editor role on a Project
        And the Flow belongs to that Project
        When the AuthService.CanAccess method is called for Read permission on the Flow
        Then the check must return a response in less than 50 milliseconds (p95)

        Note: This test covers the role inheritance path where Flow permissions
        are inherited from Project-level role assignments.
        """
        user = perf_user_with_project_role
        flow = perf_test_flow

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Read", "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Read", "Flow", flow.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)

            # Editor role should have Read permission
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - Inherited Project Role", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_superuser_bypass_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_superuser: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency for superuser (bypass path).

        Gherkin Scenario: Latency for CanAccess Check (Superuser Bypass)
        Given a user is marked as superuser
        When the AuthService.CanAccess method is called
        Then the check should bypass RBAC and return True quickly
        And the latency must be less than 50 milliseconds (p95)

        Note: Superuser bypass should be faster than regular permission checks
        as it short-circuits after checking the is_superuser flag.
        """
        user = perf_superuser
        flow = perf_test_flow

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - Superuser Bypass", stats)

        # Assert p95 < 50ms (should be much faster due to bypass)
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_global_admin_bypass_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_admin_user: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency for Global Admin role (bypass path).

        Gherkin Scenario: Latency for CanAccess Check (Global Admin Bypass)
        Given a user has the Global Admin role
        When the AuthService.CanAccess method is called
        Then the check should bypass scope-specific checks and return True
        And the latency must be less than 50 milliseconds (p95)
        """
        user = perf_admin_user
        flow = perf_test_flow

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - Global Admin Bypass", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_no_permission_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_test_user: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency when user has no permission (negative path).

        Gherkin Scenario: Latency for CanAccess Check (No Permission)
        Given a user has no role assignments
        When the AuthService.CanAccess method is called
        Then the check should return False
        And the latency must be less than 50 milliseconds (p95)

        Note: This tests the worst-case scenario where all checks fail
        and no permission is found.
        """
        user = perf_test_user
        flow = perf_test_flow

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Delete", "Flow", flow.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)

            # User without role should not have permission
            assert result is False

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - No Permission (Negative)", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_project_scope_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_user_with_project_role: User,
        perf_test_project: Folder,
    ):
        """Test can_access() latency for Project scope permissions.

        Gherkin Scenario: Latency for CanAccess Check (Project Scope)
        Given a user has an Editor role on a Project
        When the AuthService.CanAccess method is called for Update permission on the Project
        Then the check must return a response in less than 50 milliseconds (p95)
        """
        user = perf_user_with_project_role
        project = perf_test_project

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user.id, "Update", "Project", project.id, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user.id, "Update", "Project", project.id, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - Project Scope", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"

    async def test_can_access_string_uuid_conversion_latency(
        self,
        rbac_service: RBACService,
        perf_db_session: AsyncSession,
        perf_user_with_flow_role: User,
        perf_test_flow: Flow,
    ):
        """Test can_access() latency with string UUIDs (conversion overhead).

        This test verifies that UUID string-to-UUID conversion does not
        add significant overhead to permission checks.
        """
        user = perf_user_with_flow_role
        flow = perf_test_flow

        # Convert UUIDs to strings
        user_id_str = str(user.id)
        flow_id_str = str(flow.id)

        # Warm up
        for _ in range(self.WARMUP_ITERATIONS):
            await rbac_service.can_access(user_id_str, "Read", "Flow", flow_id_str, perf_db_session)

        # Benchmark
        latencies = []
        for _ in range(self.BENCHMARK_ITERATIONS):
            start = time.perf_counter()
            result = await rbac_service.can_access(user_id_str, "Read", "Flow", flow_id_str, perf_db_session)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
            assert result is True

        stats = calculate_latency_stats(latencies)
        print_latency_report("can_access() - String UUID Conversion", stats)

        # Assert p95 < 50ms
        assert stats["p95"] < 50, f"can_access() p95 latency {stats['p95']:.2f}ms exceeds 50ms requirement"
