# RBAC Migration Guide

This guide helps you upgrade an existing LangBuilder deployment to include Role-Based Access Control (RBAC).

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Migration Timeline](#migration-timeline)
4. [Pre-Migration Checklist](#pre-migration-checklist)
5. [Migration Steps](#migration-steps)
6. [Verification](#verification)
7. [Post-Migration Tasks](#post-migration-tasks)
8. [Rollback Procedure](#rollback-procedure)
9. [Troubleshooting](#troubleshooting)
10. [Monitoring and Performance](#monitoring-and-performance)

## Overview

The RBAC migration adds fine-grained access control to your LangBuilder deployment while maintaining **full backward compatibility**. All existing users retain access to their resources.

### What Changes?

**Database Changes**:
- 4 new tables: `role`, `permission`, `role_permission`, `user_role_assignment`
- 1 modified table: `folder` (new `is_starter_project` column)
- Database indexes for performance
- Seed data for default roles and permissions

**Application Changes**:
- New RBAC Management UI in Admin Page
- Permission checks on all resource access
- New RBAC API endpoints
- Audit logging for role assignments

**No Breaking Changes**:
- Existing users keep access to their resources (auto-assigned Owner roles)
- Superusers remain admins
- All existing functionality preserved
- No API changes to existing endpoints

### Migration Duration

Estimated migration time based on deployment size:

| Deployment Size | Estimated Duration |
|----------------|-------------------|
| Small (< 100 flows) | 5 minutes |
| Medium (100-1000 flows) | 15 minutes |
| Large (1000-10000 flows) | 30 minutes |
| Enterprise (> 10000 flows) | 1-2 hours |

**Note**: Most time is spent on data migration (backfilling Owner role assignments).

## Prerequisites

### Version Requirements

- **Current Version**: LangBuilder v1.4.x or earlier
- **Target Version**: LangBuilder v1.5.0 or later

Check your current version:

```bash
# From LangBuilder root directory
cat VERSION

# Or via Python
python -c "import langbuilder; print(langbuilder.__version__)"
```

### System Requirements

- **Database**: SQLite 3.x or PostgreSQL 12+
- **Python**: 3.10, 3.11, 3.12, or 3.13
- **Disk Space**: At least 20% free space (for database backup and migration)
- **Downtime**: Schedule a maintenance window (estimated duration above)

### Access Requirements

- Root or sudo access to server
- Database administrator access
- Admin user account in LangBuilder (superuser)

### Backup Requirements

**Critical**: Take a full backup before proceeding.

#### SQLite Backup

```bash
# Navigate to LangBuilder data directory
cd /path/to/langbuilder/data

# Create timestamped backup
cp langbuilder.db langbuilder.db.backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -lh langbuilder.db*
```

#### PostgreSQL Backup

```bash
# Create full database dump
pg_dump -h localhost -U langbuilder_user langbuilder > langbuilder_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup
ls -lh langbuilder_backup*.sql
```

#### Backup Verification

```bash
# SQLite: Check file size is reasonable
ls -lh langbuilder.db.backup*

# PostgreSQL: Check SQL file is not empty
head -20 langbuilder_backup*.sql
tail -20 langbuilder_backup*.sql
```

## Migration Timeline

### Recommended Schedule

1. **Pre-Migration (1-2 days before)**:
   - Review this guide
   - Test migration on staging/dev environment
   - Schedule maintenance window
   - Communicate to users

2. **Migration Day**:
   - Maintenance window begins
   - Take database backup
   - Run migration
   - Verify results
   - Test RBAC functionality
   - Maintenance window ends

3. **Post-Migration (1 week after)**:
   - Monitor performance
   - Configure role assignments
   - Train administrators
   - Gather user feedback

### Communication Template

**Email to users (2 days before)**:

```
Subject: Scheduled Maintenance: LangBuilder RBAC Upgrade

Dear LangBuilder Users,

We will be upgrading LangBuilder to include Role-Based Access Control (RBAC)
on [DATE] at [TIME] ([TIMEZONE]).

Expected downtime: [DURATION] (e.g., 15 minutes)

What to expect:
- LangBuilder will be unavailable during the upgrade
- All your existing Projects and Flows will remain unchanged
- You will retain full access to your resources
- New Admin features will be available after the upgrade

No action is required from you.

If you have any questions, please contact [SUPPORT EMAIL].

Thank you for your patience.
```

## Pre-Migration Checklist

Complete this checklist before starting the migration:

### Technical Preparation

- [ ] **Backup completed** and verified (see [Backup Requirements](#backup-requirements))
- [ ] **Maintenance window scheduled** with users notified
- [ ] **Staging migration tested** (if applicable)
- [ ] **Disk space checked** (at least 20% free)
- [ ] **Database version verified** (SQLite 3.x or PostgreSQL 12+)
- [ ] **Python version verified** (3.10-3.13)
- [ ] **Admin credentials available** for post-migration verification

### Resource Audit

- [ ] **Count users**: How many users exist?
  ```bash
  # SQLite
  sqlite3 langbuilder.db "SELECT COUNT(*) FROM user;"

  # PostgreSQL
  psql -U langbuilder_user langbuilder -c "SELECT COUNT(*) FROM \"user\";"
  ```

- [ ] **Count Projects**: How many Projects (folders) exist?
  ```bash
  # SQLite
  sqlite3 langbuilder.db "SELECT COUNT(*) FROM folder;"

  # PostgreSQL
  psql -U langbuilder_user langbuilder -c "SELECT COUNT(*) FROM folder;"
  ```

- [ ] **Count Flows**: How many Flows exist?
  ```bash
  # SQLite
  sqlite3 langbuilder.db "SELECT COUNT(*) FROM flow;"

  # PostgreSQL
  psql -U langbuilder_user langbuilder -c "SELECT COUNT(*) FROM flow;"
  ```

### Rollback Plan

- [ ] **Rollback procedure reviewed** (see [Rollback Procedure](#rollback-procedure))
- [ ] **Rollback time estimated** (same as migration duration)
- [ ] **Rollback decision criteria defined** (what failures trigger rollback?)

## Migration Steps

### Step 1: Stop LangBuilder Services

Stop all running LangBuilder services to prevent data corruption during migration.

```bash
# Stop backend service
# Method 1: If using systemd
sudo systemctl stop langbuilder

# Method 2: If running via screen/tmux
# Find the process and kill it
pkill -f "uvicorn langbuilder"

# Method 3: If using Docker
docker stop langbuilder-backend

# Verify services are stopped
ps aux | grep langbuilder
# Should return no results
```

### Step 2: Backup Database

Follow the backup procedures in [Prerequisites](#backup-requirements).

**Critical**: Do not proceed until backup is complete and verified.

### Step 3: Update LangBuilder Code

Pull the latest version with RBAC support.

```bash
# Navigate to LangBuilder root directory
cd /path/to/langbuilder

# Stash any local changes (if applicable)
git stash

# Pull latest code
git pull origin main

# Verify you're on the correct version (v1.5.0+)
cat VERSION
```

### Step 4: Install Dependencies

Install updated backend and frontend dependencies.

```bash
# Install backend dependencies
make install_backend

# Or manually with uv
uv pip install -e src/backend/base/langbuilder

# Install frontend dependencies (if updating frontend)
make install_frontend

# Or manually with npm
cd src/frontend && npm install
```

### Step 5: Run Database Migrations

Apply RBAC database migrations using Alembic.

```bash
# Check current database version
make alembic-current

# Apply RBAC migrations
make alembic-upgrade

# Verify migrations completed successfully
make alembic-current
```

**Expected Output**:

```
Running: alembic upgrade head
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade <previous_rev> -> <rbac_rev>, Add RBAC tables
INFO  [alembic.runtime.migration] Running upgrade <rbac_rev> -> <rbac_rev2>, Add is_starter_project column

Running: alembic current
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
<current_revision_id> (head)
```

**What These Migrations Do**:

1. **Create RBAC Tables**:
   - `role`: Stores role definitions (Admin, Owner, Editor, Viewer)
   - `permission`: Stores permission definitions (Create, Read, Update, Delete)
   - `role_permission`: Links roles to permissions
   - `user_role_assignment`: Stores user role assignments

2. **Modify Existing Tables**:
   - Add `is_starter_project` column to `folder` table
   - Create database indexes for performance

3. **Seed Default Data**:
   - Insert 4 default roles
   - Insert 8 permissions (4 permissions × 2 scopes: Flow and Project)
   - Link roles to permissions (role_permission entries)

4. **Backfill Owner Assignments**:
   - Identify all existing users
   - For each user, assign Owner role on their Projects
   - For each user, assign Owner role on their Flows
   - Mark Starter Project Owner assignments as immutable

### Step 6: Verify Migration Data

Check that default roles and permissions were created correctly.

```bash
# Check roles
# SQLite
sqlite3 langbuilder.db "SELECT name, description FROM role;"

# PostgreSQL
psql -U langbuilder_user langbuilder -c "SELECT name, description FROM role;"
```

**Expected Output**:

```
Admin|Global administrator with full access
Owner|Full control over assigned resources
Editor|Create, read, and update access
Viewer|Read-only access
```

```bash
# Check permissions
# SQLite
sqlite3 langbuilder.db "SELECT name, scope FROM permission;"

# PostgreSQL
psql -U langbuilder_user langbuilder -c "SELECT name, scope FROM permission;"
```

**Expected Output**:

```
Create|Flow
Read|Flow
Update|Flow
Delete|Flow
Create|Project
Read|Project
Update|Project
Delete|Project
```

```bash
# Check user role assignments were backfilled
# SQLite
sqlite3 langbuilder.db "SELECT COUNT(*) FROM user_role_assignment;"

# PostgreSQL
psql -U langbuilder_user langbuilder -c "SELECT COUNT(*) FROM user_role_assignment;"
```

**Expected**: Number should be at least (number of users × 2) for Starter Project + Global Project.

### Step 7: Build Frontend (if applicable)

If you're deploying frontend changes, rebuild the frontend.

```bash
# Build frontend static files
make build_frontend

# Or manually
cd src/frontend
npm run build
```

### Step 8: Start LangBuilder Services

Restart LangBuilder services after migration.

```bash
# Start backend service
# Method 1: If using systemd
sudo systemctl start langbuilder
sudo systemctl status langbuilder

# Method 2: If running manually
make backend

# Method 3: If using Docker
docker start langbuilder-backend

# Verify services are running
ps aux | grep langbuilder
curl http://localhost:7860/api/v1/health
```

**Expected Health Check Response**:

```json
{
  "status": "healthy"
}
```

### Step 9: Verify RBAC Functionality

Test that RBAC features are working correctly.

#### A. Test RBAC Management UI Access

1. Log in as an Admin (superuser)
2. Navigate to Admin Page
3. Verify you see the "RBAC Management" tab
4. Click the RBAC Management tab
5. Verify the assignment list loads

**Expected**: You should see role assignments for all users on their Projects/Flows.

#### B. Test Permission Checks

```bash
# Test permission check endpoint
curl -X GET "http://localhost:7860/api/v1/rbac/check-permission?permission=Read&scope_type=Global" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**:

```json
{
  "has_permission": true
}
```

#### C. Test Creating a Role Assignment

1. In RBAC Management UI, click "New Assignment"
2. Follow the wizard to create a test assignment
3. Verify the assignment appears in the list

#### D. Verify User Access

1. Log in as a regular (non-admin) user
2. Verify the user can see their Projects and Flows
3. Verify the user cannot access other users' Projects/Flows (unless explicitly granted)

## Verification

### Automated Verification Script

Run the verification script to check migration results.

```bash
# Run verification script
uv run python scripts/verify_rbac_migration.py
```

**Expected Output**:

```
LangBuilder RBAC Migration Verification
========================================

✓ 4 default roles created
  - Admin
  - Owner
  - Editor
  - Viewer

✓ 8 permissions created
  - Create (Flow, Project)
  - Read (Flow, Project)
  - Update (Flow, Project)
  - Delete (Flow, Project)

✓ 32 role-permission mappings created

✓ 150 users migrated
✓ 300 Projects have Owner assignments
✓ 1200 Flows have Owner assignments

✓ All users have Owner role on their Starter Project
✓ Starter Project Owner assignments are immutable

========================================
Migration verification PASSED
```

### Manual Verification Checklist

- [ ] **Default roles exist**: 4 roles (Admin, Owner, Editor, Viewer)
- [ ] **Default permissions exist**: 8 permissions (Create/Read/Update/Delete × Flow/Project)
- [ ] **Users have role assignments**: All existing users have Owner roles on their resources
- [ ] **Starter Projects marked**: Starter Projects have `is_starter_project=True`
- [ ] **Immutable assignments protected**: Starter Project Owner assignments have `is_immutable=True`
- [ ] **RBAC Management UI accessible**: Admin users can access RBAC Management tab
- [ ] **Permission checks work**: `/api/v1/rbac/check-permission` endpoint responds correctly
- [ ] **Users can access resources**: Regular users can still access their Projects/Flows

## Post-Migration Tasks

### Task 1: Assign Roles for Shared Resources

If you have shared Projects or Flows that should be accessible to multiple users, create role assignments.

**Example**: Give marketing team access to "Marketing Campaigns" Project:

1. Navigate to RBAC Management
2. For each team member:
   - Click "New Assignment"
   - Select user
   - Select Project "Marketing Campaigns"
   - Assign appropriate role (Owner, Editor, or Viewer)

### Task 2: Configure Admin Role Assignments

Identify users who should have Admin privileges and assign Global Admin role.

**Example**: Assign Admin role to IT staff:

1. Navigate to RBAC Management
2. Click "New Assignment"
3. Select IT staff user
4. Select Global scope
5. Assign Admin role

### Task 3: Train Administrators

Provide training to administrators on using the RBAC Management UI:

- Review [Admin Guide](./admin-guide.md)
- Practice creating, editing, and deleting role assignments
- Understand role inheritance
- Learn about immutable assignments

### Task 4: Monitor Performance

Monitor RBAC performance metrics (see [Monitoring and Performance](#monitoring-and-performance)):

- Permission check latency (target: <50ms at p95)
- Assignment mutation latency (target: <200ms at p95)
- API error rates (target: <0.1%)

### Task 5: Communication to Users

Notify users that RBAC is now enabled:

**Email Template**:

```
Subject: LangBuilder RBAC Upgrade Complete

Dear LangBuilder Users,

The RBAC upgrade has been completed successfully. LangBuilder is now available
with new access control features.

What's new:
- Fine-grained role-based access control
- Administrators can now manage user permissions
- Improved security and compliance

What you need to do:
- Nothing! You retain full access to your existing Projects and Flows.
- If you need to share a Project or Flow with a colleague, contact your
  administrator.

For more information, see [RBAC Documentation Link].

Thank you for your patience.
```

## Rollback Procedure

If you encounter critical issues during or after migration, you can rollback.

**Warning**: Rollback should only be used if RBAC functionality is broken. Do not rollback just to revert role assignments (delete them via RBAC Management UI instead).

### When to Rollback

Rollback if:
- Database migration fails with errors
- Verification script reports failures
- Users cannot access their resources after migration
- Critical application errors related to RBAC

Do NOT rollback if:
- Users complain about new permission restrictions (this is expected behavior)
- Minor UI issues (these can be fixed without rollback)
- Performance is slightly slower (optimize queries instead)

### Rollback Steps

#### Step 1: Stop LangBuilder Services

```bash
# Stop backend service
sudo systemctl stop langbuilder
# Or kill the process
pkill -f "uvicorn langbuilder"
```

#### Step 2: Restore Database Backup

**SQLite**:

```bash
# Navigate to data directory
cd /path/to/langbuilder/data

# Restore backup (replace with your backup filename)
cp langbuilder.db.backup_20240115_103000 langbuilder.db

# Verify restoration
sqlite3 langbuilder.db "SELECT COUNT(*) FROM user;"
```

**PostgreSQL**:

```bash
# Drop existing database
psql -U postgres -c "DROP DATABASE langbuilder;"

# Create new database
psql -U postgres -c "CREATE DATABASE langbuilder OWNER langbuilder_user;"

# Restore from backup (replace with your backup filename)
psql -U langbuilder_user langbuilder < langbuilder_backup_20240115_103000.sql

# Verify restoration
psql -U langbuilder_user langbuilder -c "SELECT COUNT(*) FROM \"user\";"
```

#### Step 3: Rollback Code

```bash
# Navigate to LangBuilder root directory
cd /path/to/langbuilder

# Checkout previous version (replace with your previous version tag)
git checkout v1.4.5

# Or if you stashed changes
git stash pop

# Reinstall dependencies
make install_backend
```

#### Step 4: Restart LangBuilder Services

```bash
# Start backend service
sudo systemctl start langbuilder
sudo systemctl status langbuilder

# Verify services are running
curl http://localhost:7860/api/v1/health
```

#### Step 5: Verify Rollback

- Log in to LangBuilder
- Verify users can access their Projects and Flows
- Check that RBAC Management tab does not appear (expected after rollback)

### Post-Rollback Actions

1. **Document the issue**: Record what went wrong and why rollback was necessary
2. **Contact support**: Open a GitHub issue or email support@langbuilder.io with details
3. **Plan retry**: After the issue is resolved, plan a new migration attempt

## Troubleshooting

### Issue: Migration Fails with "Table already exists" Error

**Error Message**:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) table role already exists
```

**Cause**: RBAC tables already exist (partial migration or previous attempt).

**Solution**:

1. Check database state:
   ```bash
   # SQLite
   sqlite3 langbuilder.db ".tables" | grep -E "role|permission|assignment"

   # PostgreSQL
   psql -U langbuilder_user langbuilder -c "\dt" | grep -E "role|permission|assignment"
   ```

2. If RBAC tables exist but data is incomplete:
   ```bash
   # Rollback to clean state
   make alembic-downgrade

   # Re-run migration
   make alembic-upgrade
   ```

3. If you want to keep existing RBAC data:
   - Skip to verification step
   - Ensure data is correct

### Issue: Users Cannot Access Their Resources

**Symptoms**: Users report that their Projects/Flows are not visible after migration.

**Cause**: Owner role assignments were not backfilled correctly.

**Solution**:

```bash
# Run backfill script manually
uv run python scripts/backfill_owner_assignments.py
```

**Expected Output**:

```
Backfilling Owner role assignments...
✓ Created Owner assignment for user_id on project_id
✓ Created Owner assignment for user_id on flow_id
...
Backfill complete: 1500 assignments created
```

### Issue: Admin UI Shows "Access Denied"

**Symptoms**: Admin user cannot access RBAC Management tab.

**Cause**: User account is not recognized as Admin (not superuser and no Global Admin role).

**Solution**:

1. Check if user is superuser:
   ```bash
   # SQLite
   sqlite3 langbuilder.db "SELECT username, is_superuser FROM user WHERE username = 'admin_username';"

   # PostgreSQL
   psql -U langbuilder_user langbuilder -c "SELECT username, is_superuser FROM \"user\" WHERE username = 'admin_username';"
   ```

2. If `is_superuser=False`, set it to `True`:
   ```bash
   # SQLite
   sqlite3 langbuilder.db "UPDATE user SET is_superuser = 1 WHERE username = 'admin_username';"

   # PostgreSQL
   psql -U langbuilder_user langbuilder -c "UPDATE \"user\" SET is_superuser = true WHERE username = 'admin_username';"
   ```

3. Log out and log back in

### Issue: Verification Script Reports Missing Assignments

**Symptoms**: Verification script shows fewer assignments than expected.

**Cause**: Some resources (Projects/Flows) may not have owners or were created by deleted users.

**Solution**:

1. Identify orphaned resources:
   ```bash
   # SQLite
   sqlite3 langbuilder.db "SELECT id, name FROM flow WHERE user_id NOT IN (SELECT id FROM user);"

   # PostgreSQL
   psql -U langbuilder_user langbuilder -c "SELECT id, name FROM flow WHERE user_id NOT IN (SELECT id FROM \"user\");"
   ```

2. Assign orphaned resources to an admin:
   - Use RBAC Management UI
   - Assign Owner role on each orphaned resource to an admin user

### Issue: Performance Degradation

**Symptoms**: Permission checks are slow (>100ms).

**Cause**: Missing database indexes or inefficient queries.

**Solution**:

1. Check that indexes were created:
   ```bash
   # SQLite
   sqlite3 langbuilder.db ".indexes user_role_assignment"

   # PostgreSQL
   psql -U langbuilder_user langbuilder -c "\di" | grep assignment
   ```

2. Expected indexes:
   - `idx_user_role_assignment_user_id`
   - `idx_user_role_assignment_scope`
   - `idx_permission_name_scope`

3. If indexes are missing, recreate them:
   ```bash
   # Re-run migration (it's safe to re-run)
   make alembic-upgrade
   ```

4. Analyze query performance:
   ```bash
   # SQLite
   sqlite3 langbuilder.db "EXPLAIN QUERY PLAN SELECT * FROM user_role_assignment WHERE user_id = 'some_uuid';"
   ```

5. If still slow, contact support with query plans

### Issue: Immutable Assignments Not Protected

**Symptoms**: Able to delete Starter Project Owner assignments.

**Cause**: `is_immutable` flag not set correctly during migration.

**Solution**:

```bash
# Mark Starter Project Owner assignments as immutable
# SQLite
sqlite3 langbuilder.db "UPDATE user_role_assignment SET is_immutable = 1 WHERE scope_type = 'Project' AND scope_id IN (SELECT id FROM folder WHERE is_starter_project = 1);"

# PostgreSQL
psql -U langbuilder_user langbuilder -c "UPDATE user_role_assignment SET is_immutable = true WHERE scope_type = 'Project' AND scope_id IN (SELECT id FROM folder WHERE is_starter_project = true);"
```

## Monitoring and Performance

After migration, monitor RBAC system performance to ensure it meets SLA requirements.

### Key Metrics

**1. Permission Check Latency**

Target: p95 < 50ms (PRD requirement)

Monitor: `rbac_permission_check_duration_seconds`

**2. Assignment Mutation Latency**

Target: p95 < 200ms (PRD requirement)

Monitor: `rbac_assignment_create_duration_seconds`

**3. API Error Rate**

Target: < 0.1%

Monitor: `rbac_check_errors_total`

**4. System Uptime**

Target: 99.9% (PRD requirement)

Monitor: Overall service availability

### Monitoring Setup

If you use Prometheus/Grafana, add RBAC metrics:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'langbuilder'
    static_configs:
      - targets: ['localhost:7860']
```

Create Grafana dashboard with panels for:
- Permission check latency (p50, p95, p99)
- Assignment mutation rates (create/update/delete over time)
- Error rates by type
- Top 10 slowest permission checks

### Performance Optimization

If permission checks are slow:

1. **Check database indexes**: Ensure all RBAC indexes exist
2. **Analyze query plans**: Use `EXPLAIN` to identify slow queries
3. **Enable query caching**: Configure caching layer if available
4. **Increase database resources**: Allocate more CPU/memory to database

If assignment mutations are slow:

1. **Check database locks**: Ensure no long-running transactions
2. **Optimize database connection pool**: Increase pool size if needed
3. **Review concurrent writes**: Avoid creating many assignments simultaneously

### Health Checks

Add RBAC-specific health check to monitoring:

```bash
# Check RBAC system health
curl -X GET http://localhost:7860/api/v1/health/rbac
```

**Expected Response**:

```json
{
  "status": "healthy",
  "roles": 4
}
```

If health check fails, investigate:
- Database connectivity
- Default roles initialized
- Permission tables populated

## Support

If you encounter issues during migration:

1. **Review [Troubleshooting](#troubleshooting)** section above
2. **Check logs**: `tail -f logs/langbuilder.log`
3. **Open GitHub issue**: [LangBuilder Issues](https://github.com/cloudgeometry/langbuilder/issues)
4. **Contact support**: [support@langbuilder.io](mailto:support@langbuilder.io)

When contacting support, include:
- LangBuilder version (before and after)
- Database type and version
- Error messages and logs
- Output of verification script
- Database row counts (users, Projects, Flows, assignments)

## Next Steps

After successful migration:

1. **Review [Admin Guide](./admin-guide.md)**: Learn to manage role assignments
2. **Review [Getting Started](./getting-started.md)**: Understand RBAC concepts
3. **Review [API Reference](./api-reference.md)**: Automate role management
4. **Review [Architecture](./architecture.md)**: Understand technical implementation

Welcome to LangBuilder with RBAC!
