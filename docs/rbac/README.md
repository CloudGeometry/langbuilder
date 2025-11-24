# Role-Based Access Control (RBAC) in LangBuilder

## Overview

LangBuilder's RBAC system provides fine-grained, customizable access control for managing permissions across Projects and Flows. This enterprise-grade security feature enables organizations to structure access appropriately, enforce security policies, and manage team collaboration effectively.

## What is RBAC?

Role-Based Access Control (RBAC) is a security paradigm where access permissions are assigned to roles, and users are assigned to roles. Instead of granting permissions directly to individual users, you assign users to roles that have predefined permissions.

**Benefits:**
- **Security**: Enforce least-privilege access principles
- **Scalability**: Manage permissions for large teams efficiently
- **Auditability**: Track who has access to what resources
- **Compliance**: Meet regulatory requirements (SOC 2, GDPR, HIPAA)
- **Simplicity**: Assign roles instead of individual permissions

## Key Concepts

### Roles

LangBuilder provides four predefined system roles:

| Role | Description | Use Case |
|------|-------------|----------|
| **Admin** | Global administrator with full system access | System administrators, DevOps engineers |
| **Owner** | Full control over specific Projects/Flows | Project leads, resource owners |
| **Editor** | Create, read, and update access (no delete) | Developers, content creators |
| **Viewer** | Read-only access (can execute and export) | Stakeholders, QA testers, external collaborators |

### Permissions

Each role has a set of permissions that determine what actions users can perform:

| Permission | Admin | Owner | Editor | Viewer |
|------------|-------|-------|--------|--------|
| **Create** | All scopes | Own scope | Own scope | - |
| **Read** | All scopes | Own scope | Own scope | Own scope |
| **Update** | All scopes | Own scope | Own scope | - |
| **Delete** | All scopes | Own scope | - | - |

**Special Permissions:**
- **Read** includes: view, execute, save, export, and download
- **Update** includes: edit and import functionality

### Scopes

Scopes define the context where permissions apply:

| Scope | Description | Example |
|-------|-------------|---------|
| **Global** | System-wide access | Admin role only |
| **Project** | Access to a specific Project and its contents | Project: "Marketing Automation" |
| **Flow** | Access to a specific Flow within a Project | Flow: "Lead Scoring Pipeline" |

### Role Inheritance

Flows automatically inherit permissions from their parent Project:

```
Project: "Customer Analytics" (User has Editor role)
├── Flow: "Data Pipeline" (User inherits Editor role)
├── Flow: "Dashboard Generator" (User inherits Editor role)
└── Flow: "Report Builder" (User can be assigned Owner role explicitly)
```

**Inheritance Rules:**
1. If a user has a role assigned to a Project, they inherit that role for all Flows in the Project
2. Explicit Flow-level assignments override inherited Project-level roles
3. More specific scope assignments take precedence over general ones

## Quick Examples

### Example 1: Team Collaboration

**Scenario**: Marketing team needs collaborative access to shared Projects

```
User: alice@company.com
- Role: Owner on Project "Marketing Campaigns"
  → Can manage all Flows in the Project
  → Can create, edit, and delete Flows

User: bob@company.com
- Role: Editor on Project "Marketing Campaigns"
  → Can create and edit Flows
  → Cannot delete Flows or modify Project settings

User: charlie@company.com
- Role: Viewer on Flow "Email Campaign Q4"
  → Can view and execute only this specific Flow
  → No access to other Flows in the Project
```

### Example 2: External Collaboration

**Scenario**: Share a Flow with external consultant for review

```
User: consultant@external.com
- Role: Viewer on Flow "Revenue Forecast Model"
  → Can view the Flow logic
  → Can execute the Flow and see results
  → Can export and download the Flow
  → Cannot modify or delete anything
```

### Example 3: Administrative Access

**Scenario**: IT admin needs to manage all resources

```
User: admin@company.com
- Role: Admin (Global scope)
  → Full access to all Projects and Flows
  → Can manage role assignments for all users
  → Bypasses all permission checks
```

## Default Behavior

### New Installations

1. **Superuser Account**: The initial superuser account has Global Admin privileges
2. **New Projects**: When any user creates a Project, they automatically become the Owner
3. **New Flows**: When a user creates a Flow, they automatically become the Owner
4. **Starter Project**: Each user's Starter Project has an immutable Owner assignment

### Immutable Assignments

Certain role assignments cannot be modified or deleted to preserve system integrity:

- **Starter Project Owner**: Every user is permanently assigned as Owner of their Starter Project
- These assignments are marked with an "Immutable" badge in the Admin UI

## Access Control Behavior

### Project Access

When accessing a Project:
- Users only see Projects where they have at least Viewer role
- Projects without any role assignment are invisible to the user
- Admin role bypasses all restrictions

### Flow Access

When accessing a Flow:
1. System checks for explicit Flow-level role assignment
2. If none exists, inherits role from parent Project
3. If no Project role exists, access is denied
4. Admin role bypasses all restrictions

### UI Behavior

The UI dynamically adapts based on user permissions:

| UI Element | Required Permission | Behavior if Missing |
|------------|---------------------|---------------------|
| Project/Flow list | Read | Resource not shown in list |
| Edit button | Update | Button hidden or disabled |
| Delete button | Delete | Button hidden or disabled |
| Create New Flow button | Create (on Project) | Button hidden or disabled |
| Flow editor | Update | Editor loads in read-only mode |
| Import function | Update | Function disabled |

## Performance Characteristics

The RBAC system is designed for high performance:

- **Permission checks**: <50ms at p95 latency
- **Role assignments**: <200ms at p95 for create/update/delete operations
- **Editor load time**: <2.5s at p95 for page load including RBAC checks
- **Batch permission checks**: Optimized for checking multiple resources at once
- **System uptime**: 99.9% availability target

## Security Features

1. **Audit Logging**: All role assignments and permission checks are logged
2. **Immutability**: Critical assignments (Starter Project Owner) cannot be modified
3. **Admin-Only Management**: Only Admin users can manage role assignments
4. **Session Caching**: Permission checks are cached for performance
5. **Database Constraints**: Unique constraints prevent duplicate assignments

## Getting Started

Ready to use RBAC in your LangBuilder deployment?

1. **New Users**: See [Getting Started Guide](./getting-started.md)
2. **Administrators**: See [Admin Guide](./admin-guide.md)
3. **Developers**: See [API Reference](./api-reference.md)
4. **Upgrading**: See [Migration Guide](./migration-guide.md)
5. **Technical Details**: See [Architecture Documentation](./architecture.md)

## Common Use Cases

### Team Collaboration
Assign Editor roles to team members on shared Projects for collaborative development.

### External Access
Grant Viewer roles to external stakeholders for read-only access to specific Flows.

### Hierarchical Access
Use Project-level roles for broad access, override with Flow-level roles for exceptions.

### Administrative Management
Assign Admin role to IT staff for centralized user and permission management.

### Compliance and Auditing
Use role assignments and audit logs to demonstrate access controls for compliance.

## FAQs

### Can I create custom roles?

Not in the current version. The MVP provides four predefined roles (Admin, Owner, Editor, Viewer) that cover most use cases. Custom roles are planned for future releases.

### Can users share Flows themselves?

Not yet. All role assignments must be managed by Admin users through the RBAC Management UI. User-triggered sharing is out of scope for the MVP.

### What happens to existing Projects and Flows after RBAC is enabled?

All existing users automatically receive Owner roles on their existing Projects and Flows during migration. Nothing is lost, and existing functionality is preserved.

### How do I give someone access to just one Flow in a Project?

Create a Flow-specific role assignment for that user. This overrides the Project-level inheritance.

### Can I remove the Admin role from a user?

Yes, if you are an Admin. Simply delete the Global Admin role assignment for that user. However, superuser accounts (is_superuser=True in database) always have admin access regardless of role assignments.

### What happens if I accidentally delete a role assignment?

The user immediately loses access to that resource. You can restore access by creating a new role assignment with the appropriate role.

## Support

For issues or questions:
- Check the documentation in this directory
- Open an issue on [GitHub](https://github.com/cloudgeometry/langbuilder/issues)
- Join our [Community Discord](https://discord.gg/langbuilder)
- Contact [support@langbuilder.io](mailto:support@langbuilder.io)

## Next Steps

- [Quick Start Guide](./getting-started.md) - Set up RBAC for the first time
- [Admin Guide](./admin-guide.md) - Manage role assignments in the UI
- [API Reference](./api-reference.md) - Programmatic access management
- [Migration Guide](./migration-guide.md) - Upgrade existing deployments
- [Architecture](./architecture.md) - Technical implementation details
