# RBAC Getting Started Guide

This guide will help you quickly understand and start using LangBuilder's Role-Based Access Control (RBAC) system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Understanding RBAC Basics](#understanding-rbac-basics)
3. [Your First Role Assignment](#your-first-role-assignment)
4. [Understanding Role Inheritance](#understanding-role-inheritance)
5. [Common Use Cases](#common-use-cases)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- LangBuilder version 1.5.0 or higher with RBAC enabled
- Admin access (superuser account or Global Admin role)
- At least one other user account for testing

## Understanding RBAC Basics

### The Four Roles

LangBuilder provides four predefined roles with different permission levels:

```
Admin (Global)
├── Full system access
├── Manage all resources
└── Assign roles to users

Owner (Project/Flow)
├── Full control over assigned resources
├── Create, read, update, and delete
└── Manage resource settings

Editor (Project/Flow)
├── Create and modify resources
├── Read and update
└── Cannot delete

Viewer (Project/Flow)
├── Read-only access
├── Can execute Flows
├── Can export and download
└── Cannot modify anything
```

### Permission Matrix

| Action | Admin | Owner | Editor | Viewer |
|--------|-------|-------|--------|--------|
| View resources | All | Assigned | Assigned | Assigned |
| Execute Flows | All | Assigned | Assigned | Assigned |
| Create new Flows | All | In assigned Projects | In assigned Projects | No |
| Edit Flows/Projects | All | Assigned | Assigned | No |
| Delete Flows/Projects | All | Assigned | No | No |
| Manage role assignments | Yes | No | No | No |

### Scopes Explained

**Global Scope**: System-wide access (Admin role only)
```
Global
└── Entire LangBuilder instance
```

**Project Scope**: Access to a Project and all its Flows
```
Project: "Marketing Analytics"
├── Flow: "Lead Scoring"
├── Flow: "Customer Segmentation"
└── Flow: "Campaign Performance"
```

**Flow Scope**: Access to a specific Flow only
```
Flow: "Revenue Forecast"
└── Single Flow, independent of Project permissions
```

## Your First Role Assignment

### Step 1: Access the RBAC Management UI

1. Log in to LangBuilder with an Admin account
2. Navigate to the **Admin Page** (Settings > Admin)
3. Click the **RBAC Management** tab

You should see the RBAC Management interface with:
- A "New Assignment" button
- A list of existing role assignments
- Filter options for users, roles, and scopes

### Step 2: Create a Role Assignment

Let's give a team member Editor access to a Project.

1. Click **"New Assignment"** button
2. Follow the wizard:

**Step 1: Select User**
```
Select a user from the dropdown
Example: bob@company.com
```

**Step 2: Select Scope**
```
Choose scope type: Project
Select Project: "Marketing Campaigns"
```

**Step 3: Select Role**
```
Choose role: Editor
```

**Step 4: Confirm**
```
Review the assignment:
- User: bob@company.com
- Scope: Project "Marketing Campaigns"
- Role: Editor

Click "Create Assignment"
```

### Step 3: Verify the Assignment

1. Log in as the user you just assigned (bob@company.com)
2. Navigate to the Projects page
3. Verify that:
   - The "Marketing Campaigns" Project is visible
   - All Flows in the Project are visible
   - Edit buttons are available
   - Delete buttons are hidden (Editor cannot delete)

Congratulations! You've created your first role assignment.

## Understanding Role Inheritance

Role inheritance is a powerful feature that simplifies permission management.

### How Inheritance Works

When you assign a role at the Project level, it automatically applies to all Flows within that Project.

**Example:**

```
User: alice@company.com
Role Assignment: Editor on Project "Customer Analytics"

Result:
├── Project "Customer Analytics" → Editor permissions
│   ├── Flow "Data Pipeline" → Editor permissions (inherited)
│   ├── Flow "ML Model" → Editor permissions (inherited)
│   └── Flow "Dashboard" → Editor permissions (inherited)
```

### Overriding Inherited Roles

You can override an inherited role with a more specific Flow-level assignment.

**Example:**

```
User: alice@company.com
- Editor on Project "Customer Analytics" (inherited by all Flows)
- Owner on Flow "ML Model" (explicit assignment)

Result:
├── Project "Customer Analytics" → Editor
│   ├── Flow "Data Pipeline" → Editor (inherited)
│   ├── Flow "ML Model" → Owner (overridden)
│   └── Flow "Dashboard" → Editor (inherited)
```

**Use Case**: Alice is an Editor on the Project but needs Owner permissions on a specific critical Flow to manage its deployment settings.

### Inheritance Best Practices

1. **Use Project-level roles for broad access**: Assign roles at Project level when users need consistent access
2. **Use Flow-level roles for exceptions**: Override with Flow-level roles only when needed
3. **Keep it simple**: Minimize the number of exceptions to make permissions easier to understand
4. **Document exceptions**: Keep track of why certain Flows have explicit role overrides

## Common Use Cases

### Use Case 1: Onboarding a New Team Member

**Scenario**: New developer joins the team and needs access to active Projects.

**Solution**:
```
1. Create role assignments for the developer:
   - Editor on Project "Production Workflows"
   - Editor on Project "Staging Environment"
   - Viewer on Project "Archive"

2. The developer now has:
   - Edit access to active Projects
   - Read-only access to archived Projects
   - Ability to create new Flows in active Projects
```

**Steps**:
1. Go to RBAC Management
2. Click "New Assignment"
3. Select the new user
4. Assign Editor role on each active Project
5. Assign Viewer role on Archive Project

### Use Case 2: External Collaboration

**Scenario**: Share a specific Flow with external consultant for review.

**Solution**:
```
1. Create external user account (if not exists)
2. Assign Viewer role on specific Flow:
   - User: consultant@external.com
   - Scope: Flow "Revenue Model"
   - Role: Viewer

3. Consultant can:
   - View the Flow logic
   - Execute the Flow
   - Export the Flow
   - Cannot modify or delete
```

**Steps**:
1. Create user account for consultant
2. Go to RBAC Management
3. Create new assignment
4. Select consultant user
5. Select Flow scope, choose specific Flow
6. Assign Viewer role

### Use Case 3: Project Lead with Full Control

**Scenario**: Project manager needs full control over their Project.

**Solution**:
```
1. Assign Owner role at Project level:
   - User: manager@company.com
   - Scope: Project "Customer Success"
   - Role: Owner

2. Manager can:
   - Create, edit, and delete Flows
   - Manage Project settings
   - Full control over all Flows in Project
```

**Steps**:
1. Go to RBAC Management
2. Create new assignment
3. Select manager user
4. Select Project scope
5. Assign Owner role

### Use Case 4: Read-Only Access for Stakeholders

**Scenario**: Business stakeholders need to view and execute Flows without modification.

**Solution**:
```
1. Assign Viewer role at Project level:
   - Users: stakeholder1@, stakeholder2@, stakeholder3@
   - Scope: Project "Business Reporting"
   - Role: Viewer

2. Stakeholders can:
   - View all Flows in Project
   - Execute Flows and see results
   - Export and download Flows
   - Cannot modify anything
```

**Steps**:
1. For each stakeholder:
   - Go to RBAC Management
   - Create new assignment
   - Select stakeholder user
   - Select Project scope
   - Assign Viewer role

### Use Case 5: Temporary Access

**Scenario**: Contractor needs temporary access for 2 weeks.

**Solution**:
```
1. Assign appropriate role:
   - User: contractor@temp.com
   - Scope: Project "Migration Project"
   - Role: Editor

2. Set a reminder to revoke access after 2 weeks

3. After 2 weeks:
   - Go to RBAC Management
   - Find the assignment
   - Click delete icon
   - Confirm deletion
```

**Note**: LangBuilder does not currently support automatic expiration of role assignments. You must manually revoke access.

## Best Practices

### 1. Principle of Least Privilege

Always assign the minimum role required for the user to perform their job.

```
Good:
- Developer needs to edit Flows → Assign Editor role
- Stakeholder needs to view reports → Assign Viewer role

Avoid:
- Developer needs to edit Flows → Don't assign Owner role (too much access)
- Stakeholder needs to view reports → Don't assign Editor role (unnecessary write access)
```

### 2. Use Project-Level Roles

Prefer Project-level roles over individual Flow-level roles for easier management.

```
Good:
- Assign Editor role on Project "Team Workspace"
  → User inherits Editor on all 50 Flows in Project

Avoid:
- Assigning Editor role on 50 individual Flows
  → Difficult to manage and maintain
```

### 3. Document Your Assignments

Keep a record of role assignments and the business justification.

```
Example documentation:
- alice@company.com: Owner on "Marketing" → Project lead
- bob@company.com: Editor on "Marketing" → Team member
- consultant@external.com: Viewer on "Campaign Flow" → External review, expires 2024-02-15
```

### 4. Regular Audits

Periodically review role assignments to ensure they're still appropriate.

**Monthly checklist**:
- [ ] Review all role assignments in RBAC Management
- [ ] Identify assignments that are no longer needed
- [ ] Remove access for former employees or contractors
- [ ] Update roles that need to change

### 5. Test Access Before Deploying

Before giving a user access to production resources, test with staging resources.

```
Workflow:
1. Assign role on Staging Project
2. Have user verify access
3. If correct, assign role on Production Project
4. Have user verify production access
```

### 6. Use Descriptive Project Names

Clear Project names make it easier to assign and audit roles.

```
Good:
- "Marketing Campaigns - Q1 2024"
- "Customer Success - Production"
- "Data Engineering - Staging"

Avoid:
- "Project1"
- "New Folder"
- "Test"
```

## Troubleshooting

### Issue: User Cannot See a Project

**Symptoms**: User reports that a Project is not visible in their Projects list.

**Solutions**:
1. Verify role assignment exists:
   - Go to RBAC Management
   - Filter by the user
   - Check if assignment exists for the Project

2. If no assignment exists, create one:
   - Determine appropriate role (Owner, Editor, or Viewer)
   - Create new assignment

3. Have user refresh the page or log out and log back in

### Issue: User Can View but Cannot Edit

**Symptoms**: User can see a Flow but edit buttons are disabled or missing.

**Solutions**:
1. Check the user's role:
   - Viewer role only allows read access
   - Editor or Owner role required for editing

2. Upgrade the role if appropriate:
   - Go to RBAC Management
   - Find the assignment
   - Click edit icon
   - Change role to Editor or Owner

### Issue: Cannot Delete a Role Assignment

**Symptoms**: Delete button is disabled or shows an error about immutability.

**Cause**: The assignment is marked as immutable (e.g., Starter Project Owner).

**Solutions**:
- Immutable assignments cannot be deleted by design
- These protect critical system functionality
- Examples: User's own Starter Project Owner role

**If you really need to change it**:
- Contact a database administrator
- Requires direct database modification (not recommended)

### Issue: User Has Wrong Permissions on a Flow

**Symptoms**: User has unexpected permissions on a Flow.

**Diagnosis**:
1. Check for explicit Flow-level assignment (takes priority)
2. Check for inherited Project-level assignment
3. Check if user has Global Admin role (bypasses all checks)

**Solutions**:
- If wrong explicit assignment: Edit or delete the Flow-level assignment
- If wrong inherited assignment: Edit the Project-level assignment
- If Admin role not needed: Remove Global Admin assignment

### Issue: Changes Not Taking Effect

**Symptoms**: Role assignment created but user still doesn't have access.

**Solutions**:
1. Have user refresh the page (F5 or Cmd+R)
2. Have user log out and log back in
3. Clear browser cache
4. Check for browser console errors
5. Verify assignment was created successfully (check RBAC Management list)

### Issue: Too Many Assignments to Manage

**Symptoms**: RBAC Management UI showing hundreds of assignments.

**Solutions**:
1. Use filters to narrow down:
   - Filter by user
   - Filter by role
   - Filter by scope type

2. Consolidate assignments:
   - Replace multiple Flow-level assignments with single Project-level assignment
   - Use role inheritance where possible

3. Clean up obsolete assignments:
   - Remove assignments for former employees
   - Remove duplicate assignments

## Next Steps

Now that you understand the basics, explore these advanced topics:

- **[Admin Guide](./admin-guide.md)**: Detailed guide to RBAC Management UI features
- **[API Reference](./api-reference.md)**: Programmatically manage role assignments via API
- **[Architecture](./architecture.md)**: Understand how RBAC works under the hood

## Getting Help

If you're stuck or have questions:

1. Check the [README](./README.md) for conceptual overview
2. Review the [Admin Guide](./admin-guide.md) for UI instructions
3. Check [Troubleshooting](#troubleshooting) section above
4. Open an issue on [GitHub](https://github.com/cloudgeometry/langbuilder/issues)
5. Contact [support@langbuilder.io](mailto:support@langbuilder.io)
