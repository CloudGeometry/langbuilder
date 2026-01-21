# Capabilities Matrix - LangBuilder

## Overview

This document maps LangBuilder capabilities to different user roles, showing what actions each role can perform within the platform.

---

## User Roles

### Role Definitions

| Role | Description | Typical User |
|------|-------------|--------------|
| **Developer** | Primary users who build and deploy AI workflows | AI Engineers, Backend Developers, Data Scientists |
| **Administrator** | Manages platform, users, and system configuration | DevOps, Platform Team Leads, IT Admins |
| **End User** | Consumes AI workflows via API or published interfaces | Application users, API consumers |
| **Viewer** | Read-only access to flows and execution results | Stakeholders, Reviewers, Auditors |

---

## Capabilities by Category

### 1. Flow Management

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Create flows | Yes | Yes | No | No |
| Edit flows | Yes | Yes | No | No |
| Delete flows | Yes | Yes | No | No |
| View flows | Yes | Yes | No | Yes |
| Duplicate flows | Yes | Yes | No | No |
| Import flows | Yes | Yes | No | No |
| Export flows | Yes | Yes | No | Yes |
| Organize into folders | Yes | Yes | No | No |
| Search flows | Yes | Yes | No | Yes |

### 2. Flow Execution

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Run flows from UI | Yes | Yes | No | No |
| Run flows via API | Yes | Yes | Yes | No |
| Cancel running flows | Yes | Yes | No | No |
| View execution results | Yes | Yes | Limited | Yes |
| View streaming output | Yes | Yes | Yes | No |
| Access execution history | Yes | Yes | No | Yes |

### 3. Component Management

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Browse components | Yes | Yes | No | Yes |
| Configure components | Yes | Yes | No | No |
| Create custom components | Yes | Yes | No | No |
| Install component packages | No | Yes | No | No |

### 4. API Access

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Use REST API (v1) | Yes | Yes | Limited | No |
| Use OpenAI-compatible API | Yes | Yes | Yes | No |
| Access MCP endpoints | Yes | Yes | Yes | No |
| Use webhooks | Yes | Yes | Yes | No |
| View API documentation | Yes | Yes | Yes | Yes |

### 5. Credentials & Variables

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Create API keys | Yes | Yes | No | No |
| Manage own API keys | Yes | Yes | No | No |
| Manage all API keys | No | Yes | No | No |
| Create encrypted variables | Yes | Yes | No | No |
| View variable names | Yes | Yes | No | No |
| View variable values | No | No | No | No |
| Delete variables | Yes | Yes | No | No |

### 6. User Management

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Create user accounts | No | Yes | No | No |
| Edit user profiles | Own | All | Own | Own |
| Delete user accounts | No | Yes | No | No |
| View user list | No | Yes | No | No |
| Assign roles | No | Yes | No | No |
| Reset passwords | No | Yes | No | No |

### 7. System Administration

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Configure system settings | No | Yes | No | No |
| View system health | No | Yes | No | No |
| Manage database | No | Yes | No | No |
| Configure authentication | No | Yes | No | No |
| View audit logs | No | Yes | No | No |
| Manage integrations | No | Yes | No | No |

### 8. Monitoring & Analytics

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| View own executions | Yes | Yes | Yes | No |
| View all executions | No | Yes | No | Yes |
| View build status | Yes | Yes | No | Yes |
| View transaction logs | Yes | Yes | No | Yes |
| View message history | Yes | Yes | No | Yes |
| Access observability data | No | Yes | No | No |

### 9. Publishing & Sharing

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Publish to OpenWebUI | Yes | Yes | No | No |
| Share flow URLs | Yes | Yes | No | No |
| View publication status | Yes | Yes | No | Yes |
| Manage MCP projects | Yes | Yes | No | No |

### 10. File Management

| Capability | Developer | Administrator | End User | Viewer |
|------------|:---------:|:-------------:|:--------:|:------:|
| Upload files | Yes | Yes | Yes | No |
| Download files | Yes | Yes | Yes | Yes |
| Delete files | Yes | Yes | No | No |
| View file list | Yes | Yes | Limited | Yes |

---

## Role-Based Feature Access Summary

### Developer Role
**Full access to:**
- All flow creation, editing, and execution
- Component configuration and customization
- API access (REST and OpenAI-compatible)
- Own credentials and variables
- File operations
- Publishing capabilities

**No access to:**
- System administration
- User management (except own profile)
- View other users' API keys

### Administrator Role
**Full access to:**
- Everything Developers can do
- System configuration
- User management
- All API keys and variables
- Audit and monitoring
- Integration management

### End User Role
**Limited access to:**
- Executing flows via API
- Using published endpoints
- Uploading files for processing
- Viewing own execution results

**No access to:**
- Flow creation or editing
- System administration
- Credential management

### Viewer Role
**Read-only access to:**
- Viewing flows (without editing)
- Viewing execution history
- Viewing transaction logs
- Downloading files and exports

**No access to:**
- Creating or modifying anything
- Executing flows
- API access for execution

---

## Permission Inheritance

```
Administrator
    |
    +---> Developer
              |
              +---> Viewer
              |
              +---> End User
```

- **Administrators** inherit all Developer permissions plus administrative functions
- **Developers** have full workflow development capabilities
- **Viewers** have subset of Developer's read-only capabilities
- **End Users** have limited execution-focused capabilities

---

## Implementation Notes

### Current State
- Basic role separation exists between users and system operators
- API key-based access control for programmatic access
- Auto-login mode for single-user deployments

### Recommended Enhancements
1. **Formal RBAC** - Implement role-based access control system
2. **Permission Granularity** - Fine-grained permissions per resource
3. **Team/Organization Support** - Multi-tenant role management
4. **Audit Trail** - Comprehensive action logging by role

---

*Document generated: 2026-01-21*
*Source: LangBuilder v1.6.5 codebase analysis*
