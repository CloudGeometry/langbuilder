# RBAC Admin Guide

This comprehensive guide explains how to use the LangBuilder RBAC Management UI to manage role assignments for your organization.

## Table of Contents

1. [Accessing the RBAC Management UI](#accessing-the-rbac-management-ui)
2. [Understanding the Interface](#understanding-the-interface)
3. [Creating Role Assignments](#creating-role-assignments)
4. [Viewing and Filtering Assignments](#viewing-and-filtering-assignments)
5. [Editing Role Assignments](#editing-role-assignments)
6. [Deleting Role Assignments](#deleting-role-assignments)
7. [Understanding Immutable Assignments](#understanding-immutable-assignments)
8. [Understanding Role Inheritance](#understanding-role-inheritance)
9. [Best Practices](#best-practices)
10. [Common Scenarios](#common-scenarios)

## Accessing the RBAC Management UI

### Prerequisites

To access the RBAC Management UI, you must have Admin privileges. This means you are either:
- A **superuser** (is_superuser=True in the database), or
- Assigned the **Global Admin** role

### Access Steps

1. **Log in to LangBuilder** with your Admin account
2. **Navigate to the Admin Page**:
   - Click the **Settings** icon in the navigation bar
   - Select **Admin** from the dropdown menu
   - Or directly navigate to `/admin`
3. **Switch to RBAC Management tab**:
   - The Admin Page has two tabs: User Management and RBAC Management
   - Click the **RBAC Management** tab

**Direct Link**: You can also bookmark `/admin/rbac` for direct access to the RBAC Management section.

### Access Denied?

If you see an "Access Denied" message:
- Verify you are logged in with an Admin account
- Contact your system administrator to be granted Admin privileges
- Superusers can be created via database modification or during initial setup

## Understanding the Interface

### Layout Overview

The RBAC Management interface consists of:

```
┌────────────────────────────────────────────────────┐
│  Role-Based Access Control                 [New Assignment] │
│  Manage role assignments for users...                        │
├────────────────────────────────────────────────────┤
│  ℹ️ Project-level assignments are inherited by      │
│     contained Flows and can be overridden...        │
├────────────────────────────────────────────────────┤
│  [Filters]                                          │
│  User: [All Users ▼]  Role: [All Roles ▼]          │
│  Scope: [All Scopes ▼]                              │
├────────────────────────────────────────────────────┤
│  Assignment List                                    │
│  ┌──────────────────────────────────────┐          │
│  │ User          Role    Scope           │ Actions  │
│  │ alice@co.com  Owner   Project: Marketing │ [Edit][Delete] │
│  │ bob@co.com    Editor  Flow: Pipeline     │ [Edit][Delete] │
│  │ charlie@co.com Viewer Project: Archive   │ [Edit][Delete] │
│  └──────────────────────────────────────┘          │
└────────────────────────────────────────────────────┘
```

### UI Components

**1. Header Section**
- Title and description of the RBAC Management page
- **"New Assignment"** button to create new role assignments

**2. Information Banner**
- Explains role inheritance behavior
- Key concept: Project-level roles are inherited by Flows

**3. Filter Section**
- **User Filter**: Show assignments for a specific user
- **Role Filter**: Show assignments for a specific role (Admin, Owner, Editor, Viewer)
- **Scope Filter**: Show assignments for a specific scope type (Global, Project, Flow)

**4. Assignment List**
- Displays all role assignments matching current filters
- Shows: User, Role, Scope (type and resource name), Actions
- **Edit Button**: Modify the role of an assignment
- **Delete Button**: Remove an assignment
- **Immutable Badge**: Indicates assignments that cannot be modified

## Creating Role Assignments

### Overview

Creating a role assignment grants a user specific permissions on a resource (Project or Flow).

### Step-by-Step Process

#### Step 1: Open the Create Assignment Modal

1. Click the **"New Assignment"** button in the top-right corner
2. The Create Assignment modal opens with a multi-step wizard

#### Step 2: Select User

```
┌─────────────────────────────────────┐
│  Create New Role Assignment         │
│  Step 1 of 4: Select User           │
├─────────────────────────────────────┤
│  User: [Select a user... ▼]        │
│                                     │
│  Dropdown shows:                    │
│  - alice@company.com (Alice Smith) │
│  - bob@company.com (Bob Jones)     │
│  - charlie@company.com (Charlie)   │
├─────────────────────────────────────┤
│  [Cancel]              [Next]      │
└─────────────────────────────────────┘
```

**Instructions**:
- Select the user who will receive the role assignment
- The dropdown shows all users in the system
- Use the search/filter to find users quickly
- Click **"Next"** to continue

**Tips**:
- If the user doesn't exist, create the user account first via User Management tab
- Users can be invited and will receive role assignments after they accept

#### Step 3: Select Scope

```
┌─────────────────────────────────────┐
│  Create New Role Assignment         │
│  Step 2 of 4: Select Scope          │
├─────────────────────────────────────┤
│  Scope Type: [Select scope... ▼]   │
│  Options: Global / Project / Flow   │
│                                     │
│  (After selecting scope type)       │
│  Resource: [Select resource... ▼]  │
├─────────────────────────────────────┤
│  [Back]  [Cancel]         [Next]   │
└─────────────────────────────────────┘
```

**Instructions**:

1. **Select Scope Type**:
   - **Global**: System-wide access (Admin role only)
   - **Project**: Access to a Project and all its Flows
   - **Flow**: Access to a specific Flow only

2. **Select Resource** (if Project or Flow scope):
   - For **Project**: Choose the target Project from dropdown
   - For **Flow**: Choose the target Flow from dropdown
   - Dropdown shows all available resources you can assign

3. Click **"Next"** to continue

**Tips**:
- Use **Project scope** for broad access (user gets access to all Flows in Project)
- Use **Flow scope** for specific access or to override Project inheritance
- **Global scope** is only for Admin role and should be used sparingly

#### Step 4: Select Role

```
┌─────────────────────────────────────┐
│  Create New Role Assignment         │
│  Step 3 of 4: Select Role           │
├─────────────────────────────────────┤
│  Role: [Select a role... ▼]        │
│                                     │
│  Options:                           │
│  - Admin (Global access)            │
│  - Owner (Full control)             │
│  - Editor (Create, read, update)    │
│  - Viewer (Read-only)               │
│                                     │
│  Role Description:                  │
│  [Description of selected role]     │
├─────────────────────────────────────┤
│  [Back]  [Cancel]         [Next]   │
└─────────────────────────────────────┘
```

**Instructions**:
- Select the role to assign
- Review the role description to ensure it matches the intended permissions
- Click **"Next"** to continue

**Role Selection Guide**:
- **Admin**: Only for system administrators (use Global scope)
- **Owner**: For project leads and resource owners
- **Editor**: For developers and content creators
- **Viewer**: For stakeholders and read-only users

#### Step 5: Review and Confirm

```
┌─────────────────────────────────────┐
│  Create New Role Assignment         │
│  Step 4 of 4: Confirm               │
├─────────────────────────────────────┤
│  Please review the assignment:      │
│                                     │
│  User: bob@company.com              │
│  Scope: Project "Marketing"         │
│  Role: Editor                       │
│                                     │
│  This will grant bob@company.com    │
│  Editor permissions on Project      │
│  "Marketing" and all Flows within.  │
├─────────────────────────────────────┤
│  [Back]  [Cancel]  [Create Assignment] │
└─────────────────────────────────────┘
```

**Instructions**:
- Review all details carefully
- Ensure the user, scope, and role are correct
- Click **"Create Assignment"** to confirm
- Or click **"Back"** to change any selections

**After Creation**:
- The modal closes
- A success message appears
- The new assignment appears in the assignment list
- The user immediately has the assigned permissions

### Common Creation Errors

**Error: "Duplicate assignment already exists"**
- **Cause**: An assignment with the same user, role, and scope already exists
- **Solution**: Check the assignment list; the user may already have this role

**Error: "User not found"**
- **Cause**: The user account doesn't exist
- **Solution**: Create the user account first via User Management tab

**Error: "Resource not found"**
- **Cause**: The selected Project or Flow no longer exists
- **Solution**: Refresh the page and select a different resource

**Error: "Invalid scope combination"**
- **Cause**: Invalid scope type/ID combination (e.g., Global scope with scope_id)
- **Solution**: Ensure Global scope has no resource selected

## Viewing and Filtering Assignments

### The Assignment List

The assignment list displays all role assignments in your system.

#### List Columns

| Column | Description | Example |
|--------|-------------|---------|
| **User** | User email and display name | alice@company.com |
| **Role** | Assigned role name | Owner |
| **Scope** | Scope type and resource name | Project: Marketing |
| **Created** | When the assignment was created | 2024-01-15 |
| **Actions** | Edit and Delete buttons | [Edit] [Delete] |

#### Badge Indicators

Assignments may display badges:

- **Immutable**: Assignment cannot be modified or deleted (e.g., Starter Project Owner)
- **Admin**: Global Admin role assignment

### Using Filters

Filters help you narrow down the assignment list to find specific assignments quickly.

#### Filter by User

```
User: [alice@company.com ▼]
```

**Use Cases**:
- View all role assignments for a specific user
- Audit what access a user has
- Verify a user's permissions before making changes

**Steps**:
1. Click the User filter dropdown
2. Select a user from the list (or type to search)
3. The list updates to show only that user's assignments
4. To clear: Select "All Users" from dropdown

#### Filter by Role

```
Role: [Editor ▼]
```

**Use Cases**:
- Find all users with Editor role
- Audit who has Owner access
- Identify all Admin role assignments

**Steps**:
1. Click the Role filter dropdown
2. Select a role: Admin, Owner, Editor, or Viewer
3. The list updates to show only assignments with that role
4. To clear: Select "All Roles" from dropdown

#### Filter by Scope Type

```
Scope: [Project ▼]
```

**Use Cases**:
- View all Project-level assignments
- Find Flow-specific assignments
- Identify Global Admin assignments

**Steps**:
1. Click the Scope filter dropdown
2. Select a scope type: Global, Project, or Flow
3. The list updates to show only assignments with that scope type
4. To clear: Select "All Scopes" from dropdown

#### Combining Filters

You can use multiple filters simultaneously:

```
User: bob@company.com
Role: Editor
Scope: Project

Result: Shows all Project-level Editor role assignments for bob@company.com
```

### Sorting

Click on column headers to sort the list:
- **User**: Alphabetical by email
- **Role**: Alphabetical by role name
- **Scope**: Alphabetical by scope type and resource name
- **Created**: Chronological by creation date

## Editing Role Assignments

### Overview

You can change the role of an existing assignment. The user and scope cannot be changed; to change those, delete the assignment and create a new one.

### Step-by-Step Process

#### Step 1: Locate the Assignment

1. Use filters to find the assignment you want to edit
2. Or scroll through the assignment list
3. Identify the correct assignment by user and scope

#### Step 2: Click Edit

1. Click the **Edit** button (pencil icon) on the assignment row
2. The Edit Assignment modal opens

```
┌─────────────────────────────────────┐
│  Edit Role Assignment               │
├─────────────────────────────────────┤
│  User: bob@company.com (read-only) │
│  Scope: Project "Marketing" (read-only) │
│                                     │
│  Current Role: Editor               │
│  New Role: [Select role... ▼]      │
│                                     │
│  Options: Owner / Editor / Viewer   │
├─────────────────────────────────────┤
│  [Cancel]           [Save Changes] │
└─────────────────────────────────────┘
```

#### Step 3: Select New Role

1. The User and Scope are displayed but cannot be changed
2. Select the new role from the dropdown
3. The current role is pre-selected
4. Choose a different role

#### Step 4: Save Changes

1. Click **"Save Changes"** to confirm
2. The modal closes
3. A success message appears
4. The assignment list updates with the new role
5. The user's permissions update immediately

### Common Edit Errors

**Error: "Assignment is immutable"**
- **Cause**: Trying to edit a protected assignment (e.g., Starter Project Owner)
- **Solution**: Immutable assignments cannot be edited by design

**Error: "Role not found"**
- **Cause**: The selected role doesn't exist (rare, system error)
- **Solution**: Refresh the page and try again

### Edit Use Cases

**Scenario 1: Promote Editor to Owner**
- Current: User has Editor role on Project
- New: User needs full control (Owner role)
- Action: Edit assignment, change role from Editor to Owner

**Scenario 2: Demote Owner to Viewer**
- Current: User is Owner but should only have read access
- New: Limit user to Viewer role
- Action: Edit assignment, change role from Owner to Viewer

**Scenario 3: Adjust Permissions**
- Current: User is Viewer but needs to make edits
- New: Upgrade to Editor role
- Action: Edit assignment, change role from Viewer to Editor

## Deleting Role Assignments

### Overview

Deleting a role assignment immediately revokes the user's access to the resource.

**Warning**: Deletion is immediate and irreversible. The user will lose access as soon as you confirm the deletion.

### Step-by-Step Process

#### Step 1: Locate the Assignment

1. Use filters to find the assignment you want to delete
2. Ensure you're deleting the correct assignment
3. Double-check the user and scope

#### Step 2: Click Delete

1. Click the **Delete** button (trash icon) on the assignment row
2. A confirmation dialog appears

```
┌─────────────────────────────────────┐
│  Confirm Deletion                   │
├─────────────────────────────────────┤
│  Are you sure you want to delete    │
│  this role assignment?              │
│                                     │
│  User: bob@company.com              │
│  Scope: Project "Marketing"         │
│  Role: Editor                       │
│                                     │
│  This action cannot be undone.      │
│  The user will immediately lose     │
│  access to this resource.           │
├─────────────────────────────────────┤
│  [Cancel]              [Delete]    │
└─────────────────────────────────────┘
```

#### Step 3: Confirm Deletion

1. Review the details one last time
2. Click **"Delete"** to confirm
3. Or click **"Cancel"** to abort

**After Deletion**:
- The assignment is permanently removed
- The assignment disappears from the list
- A success message appears
- The user immediately loses access to the resource

### Common Delete Errors

**Error: "Assignment is immutable"**
- **Cause**: Trying to delete a protected assignment (e.g., Starter Project Owner)
- **Solution**: Immutable assignments cannot be deleted by design
- **Reason**: These protect critical system functionality

**Error: "Assignment not found"**
- **Cause**: Assignment was already deleted or doesn't exist
- **Solution**: Refresh the page to see current state

### Accidental Deletion Recovery

If you accidentally delete an assignment:

1. There is no undo function
2. You must recreate the assignment manually:
   - Click "New Assignment"
   - Select the same user
   - Select the same scope
   - Select the same role
   - Create the assignment

**Tip**: Be very careful when deleting assignments. Always double-check before confirming.

## Understanding Immutable Assignments

### What are Immutable Assignments?

Immutable assignments are role assignments that cannot be modified or deleted through the UI. They are marked with an **"Immutable"** badge in the assignment list.

### Why Do They Exist?

Immutable assignments protect critical system functionality:
- **Starter Project Owner**: Each user owns their Starter Project
- This ensures users always have a workspace
- Prevents accidental lockout

### Identifying Immutable Assignments

In the assignment list, immutable assignments show:
```
User: alice@company.com
Role: Owner
Scope: Project "Starter Project (alice)"
Badge: [Immutable]
Actions: [Edit] (disabled) [Delete] (disabled)
```

**Visual Indicators**:
- **Badge**: Gray "Immutable" badge next to the assignment
- **Disabled Actions**: Edit and Delete buttons are grayed out or hidden
- **Tooltip**: Hovering over disabled buttons explains why they're disabled

### Can Immutable Assignments Be Changed?

Through the UI: **No**, immutable assignments cannot be modified or deleted via the RBAC Management UI.

Through the Database: **Yes**, but **not recommended**. Direct database modification can break system functionality.

**If you absolutely must**:
1. Back up the database
2. Use SQL to update the `user_role_assignment` table
3. Set `is_immutable = false` for the assignment
4. Then you can modify or delete via UI
5. **Risk**: May break user's access to Starter Project

### Best Practice

**Don't fight immutability**. These assignments exist for good reasons. If a user needs different permissions on their Starter Project, create a new Project and assign appropriate roles there.

## Understanding Role Inheritance

### How Inheritance Works

When you assign a role at the **Project** level, it automatically applies to all **Flows** within that Project.

**Visual Representation**:

```
Project: "Marketing Campaigns"
└── User: bob@company.com - Editor role

Flows:
├── "Email Campaign" → Editor (inherited)
├── "Social Media" → Editor (inherited)
└── "SEO Strategy" → Editor (inherited)
```

### Why Inheritance?

**Benefits**:
- **Efficiency**: Assign role once at Project level, applies to all Flows
- **Consistency**: All Flows in a Project have the same permissions
- **Ease of Management**: Fewer assignments to track and maintain

**Without Inheritance**:
```
❌ Must create separate assignments:
- bob@company.com - Editor on Flow "Email Campaign"
- bob@company.com - Editor on Flow "Social Media"
- bob@company.com - Editor on Flow "SEO Strategy"
(3 assignments to manage)
```

**With Inheritance**:
```
✅ Single assignment:
- bob@company.com - Editor on Project "Marketing Campaigns"
(Automatically applies to all Flows, now and future)
```

### Inheritance in the UI

**Assignment List Display**:
- **Only explicit assignments are shown** in the RBAC Management list
- **Inherited roles are not displayed** as separate entries

Example:
```
Assignment List:
┌───────────────────────────────────────────────┐
│ bob@company.com  Editor  Project: Marketing   │ ← Explicit assignment
└───────────────────────────────────────────────┘

Flows "Email Campaign", "Social Media", "SEO Strategy" inherit Editor role
but DO NOT appear as separate rows in the assignment list.
```

### Overriding Inheritance

You can override an inherited role by creating an **explicit Flow-level assignment**.

**Example**:

```
Assignments:
1. bob@company.com - Editor on Project "Marketing Campaigns"
2. bob@company.com - Owner on Flow "Email Campaign"

Result:
├── Flow "Email Campaign" → Owner (explicit, overrides inheritance)
├── Flow "Social Media" → Editor (inherited from Project)
└── Flow "SEO Strategy" → Editor (inherited from Project)
```

**When to Override**:
- User needs elevated permissions on a specific Flow
- User needs restricted permissions on a specific Flow
- Flow has special security requirements

**How to Override**:
1. Create a new assignment
2. Select the user
3. Select **Flow** scope (not Project)
4. Select the specific Flow
5. Assign the desired role

### Checking Effective Permissions

To understand what permissions a user has on a Flow:

1. Check for **explicit Flow-level assignment** → If exists, that's the role
2. If no Flow assignment, check for **Project-level assignment** → If exists, that's the inherited role
3. If no Project assignment, **user has no access**

**Tip**: The frontend UI automatically handles this logic. Users see the appropriate buttons and permissions based on their effective role.

## Best Practices

### 1. Audit Regularly

Schedule regular reviews of role assignments:

**Monthly Checklist**:
- [ ] Review all assignments in RBAC Management
- [ ] Identify assignments that are no longer needed
- [ ] Remove access for former employees or contractors
- [ ] Verify Admin role assignments are appropriate
- [ ] Check for overly permissive roles (Owner when Editor would suffice)

**Quarterly Checklist**:
- [ ] Generate report of all role assignments
- [ ] Review with team leads for accuracy
- [ ] Document any exceptions or unusual assignments
- [ ] Update role assignments based on team changes

### 2. Use Project-Level Roles

Prefer Project-level roles over Flow-level roles for easier management.

```
Good:
- Assign Editor role on Project "Team Workspace"
  → User inherits Editor on all Flows in Project
  → Easy to manage, consistent permissions

Avoid:
- Assigning Editor role on 50 individual Flows
  → Difficult to manage and maintain
  → Inconsistent, error-prone
```

**When to use Flow-level roles**:
- Specific security requirements for a Flow
- Temporary access to a single Flow
- Override inheritance for exceptional cases

### 3. Principle of Least Privilege

Always assign the minimum role required for the user to perform their job.

```
Good:
- Developer needs to edit Flows → Assign Editor role
- Stakeholder needs to view reports → Assign Viewer role
- Project lead needs full control → Assign Owner role

Avoid:
- Developer needs to edit Flows → Don't assign Owner role
- Stakeholder needs to view reports → Don't assign Editor role
```

### 4. Document Your Assignments

Keep a record of role assignments and business justification.

**Example Documentation**:
```
Role Assignment Log

User: alice@company.com
Role: Owner
Scope: Project "Marketing Campaigns"
Reason: Project lead, requires full control
Date Assigned: 2024-01-15
Assigned By: admin@company.com

User: consultant@external.com
Role: Viewer
Scope: Flow "Revenue Model"
Reason: External consultant review
Date Assigned: 2024-01-20
Expiration: 2024-02-20 (manual revocation required)
Assigned By: admin@company.com
```

### 5. Be Cautious with Admin Role

The Global Admin role grants full system access. Use it sparingly.

**Best Practices**:
- Only assign Admin role to IT staff and system administrators
- Minimize the number of Admin role assignments
- Audit Admin role assignments frequently
- Consider using Owner role for Project-specific administration instead

**Typical Admin Users**:
- IT administrators
- DevOps engineers
- System support staff

**Should NOT have Admin role**:
- Regular developers (use Editor or Owner on specific Projects)
- Project managers (use Owner on their Projects)
- Stakeholders (use Viewer or Editor as needed)

### 6. Test Before Production

Before assigning a role on production resources, test with non-production resources.

**Workflow**:
1. Create test/staging Project if not exists
2. Assign role on test Project first
3. Have user verify access and permissions
4. If correct, assign role on production Project
5. Have user verify production access

### 7. Communicate Changes

When you modify role assignments, inform the affected users.

**Example Communication**:
```
Subject: Your LangBuilder Access Has Been Updated

Hi Bob,

Your role on the "Marketing Campaigns" Project has been updated
from Editor to Owner. You now have full control over the Project
and all Flows within it.

If you have any questions or issues, please contact IT support.

Thanks,
Admin Team
```

## Common Scenarios

### Scenario 1: Onboarding a New Team Member

**Goal**: Give new developer access to team Projects.

**Steps**:
1. Navigate to RBAC Management
2. Create assignment:
   - User: newdeveloper@company.com
   - Scope: Project "Development"
   - Role: Editor
3. Create assignment:
   - User: newdeveloper@company.com
   - Scope: Project "Staging"
   - Role: Editor
4. Create assignment:
   - User: newdeveloper@company.com
   - Scope: Project "Archive"
   - Role: Viewer
5. Verify user can access Projects

**Result**: New developer has edit access to active Projects and read-only access to archives.

### Scenario 2: External Consultant Access

**Goal**: Share specific Flow with external consultant for review.

**Steps**:
1. Ensure consultant has user account
2. Navigate to RBAC Management
3. Create assignment:
   - User: consultant@external.com
   - Scope: Flow "Revenue Model"
   - Role: Viewer
4. Verify consultant can access the Flow
5. Set reminder to revoke access after engagement ends

**Result**: Consultant can view and execute the Flow but cannot modify anything.

### Scenario 3: Promoting a Team Member

**Goal**: Team member becomes project lead, needs Owner role.

**Steps**:
1. Navigate to RBAC Management
2. Filter by user: teammember@company.com
3. Find assignment: Project "Team Workspace" - Editor
4. Click Edit
5. Change role to Owner
6. Save changes
7. Verify user now has Owner permissions

**Result**: Team member now has full control over the Project.

### Scenario 4: Revoking Access

**Goal**: Remove access for former employee or contractor.

**Steps**:
1. Navigate to RBAC Management
2. Filter by user: formeremployee@company.com
3. Review all assignments
4. For each assignment:
   - Click Delete
   - Confirm deletion
5. Verify all assignments are removed
6. (Optional) Deactivate or delete user account via User Management

**Result**: Former employee has no access to any resources.

### Scenario 5: Temporary Access

**Goal**: Grant temporary access to contractor for 2 weeks.

**Steps**:
1. Navigate to RBAC Management
2. Create assignment:
   - User: contractor@temp.com
   - Scope: Project "Migration"
   - Role: Editor
3. Document assignment with expiration date
4. Set calendar reminder for expiration date
5. On expiration date:
   - Navigate to RBAC Management
   - Filter by user: contractor@temp.com
   - Delete the assignment

**Result**: Contractor has access for engagement period, then access is revoked.

**Note**: LangBuilder does not currently support automatic expiration. You must manually revoke access.

### Scenario 6: Bulk Role Updates

**Goal**: Change all Viewers on a Project to Editors.

**Steps**:
1. Navigate to RBAC Management
2. Apply filters:
   - Role: Viewer
   - Scope: Project
3. Identify assignments for the target Project
4. For each assignment:
   - Click Edit
   - Change role to Editor
   - Save changes
5. Verify all updates are complete

**Result**: All Viewers are now Editors on the Project.

**Note**: No bulk edit feature exists. Each assignment must be updated individually.

### Scenario 7: Sharing with Multiple Stakeholders

**Goal**: Give read-only access to 5 stakeholders for a Project.

**Steps**:
1. Navigate to RBAC Management
2. For each stakeholder (repeat 5 times):
   - Click "New Assignment"
   - Select stakeholder user
   - Select Project scope and target Project
   - Assign Viewer role
   - Create assignment
3. Verify all stakeholders can access the Project

**Result**: All 5 stakeholders have read-only access.

## Next Steps

- **[API Reference](./api-reference.md)**: Automate role management with the RBAC API
- **[Architecture](./architecture.md)**: Understand the technical implementation
- **[Getting Started](./getting-started.md)**: Basic RBAC concepts and examples

## Getting Help

If you need assistance:

1. Review the [README](./README.md) for RBAC concepts
2. Check [Troubleshooting](#troubleshooting) in the Getting Started guide
3. Open an issue on [GitHub](https://github.com/cloudgeometry/langbuilder/issues)
4. Contact [support@langbuilder.io](mailto:support@langbuilder.io)
