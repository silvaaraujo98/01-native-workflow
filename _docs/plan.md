# Weekly Project Feedback Tool - Scope & Technical Specification

## 1. Executive Summary

This document defines the precise product scope and initial technical specification for a **Chat-First, Internal Weekly Feedback Tool**. The tool enables team members to complete brief, structured weekly check-ins directly within their chat environment (Slack/Teams), while providing project leads and managers with real-time blocker alerts and a web dashboard for trend analysis.

---

## 2. Product Scope Overview

| Dimension | Selected Strategy | Description |
| :--- | :--- | :--- |
| **Audience** | Internal Team-Focused | Designed for internal cross-functional project teams, developers, designers, and leads. |
| **Input Format** | Lightweight & Structured | 1–2 minute updates: 3 quantitative ratings + 2 qualitative text fields. |
| **Review & Alerts** | Dashboard + Real-Time Alerts | Central dashboard for metrics/trends + immediate chat notifications for flagged blockers. |
| **Interface** | Chat-First (Slack/Teams Bot) | Interactive chat bot handles check-in prompts, modals, and reminder nudges natively. |
| **Schedule** | Asynchronous / On-Demand | Flexible submission anytime during the check-in window; targeted nudges prior to cutoff. |
| **Tech Stack** | Django (Selected Option 2) | Django backend and templates, HTMX, Chart.js, PostgreSQL, Django ORM, Django Q2, and Slack Bolt for Python. |

---

## 3. User Experience & Core Workflows

### 3.1 Weekly Member Workflow (Chat Bot)
1. **Window Opening:** On the designated check-in day (e.g., Thursday morning), the bot posts a friendly notification or direct message opening the feedback window.
2. **On-Demand Submission:** Users click a "Submit Feedback" button in chat, opening an interactive native modal.
3. **Structured Fields:**
   - **Progress Rating:** 1–5 scale (How did this week go?)
   - **Workload Rating:** 1–5 scale (1 = Underutilized, 3 = Balanced, 5 = Overloaded)
   - **Morale Rating:** 1–5 scale (Team sentiment/confidence)
   - **Highlights:** Text field (What went well / key wins)
   - **Blockers / Risks:** Text field (What is slowing you down?)
4. **Targeted Nudges:** On Friday afternoon, automated background jobs query missing submissions for active projects and send lightweight direct-message nudges *only* to pending users.

### 3.2 Lead & Manager Workflow
1. **Immediate Blocker Escalation:** When a team member flags a blocker in their submission, the bot immediately posts an alert into the designated Lead channel or DM with an actionable "Acknowledge / Mark Resolved" button.
2. **Dashboard Review:** Leads access a web-based portal to view aggregated team health, workload trends over time, historical check-ins, and recurring blocker categories.

---

## 4. Technical Architecture Plan

### Selected Stack: Option 2 — Django

| Component | Selected Technology | Responsibility |
| :--- | :--- | :--- |
| Backend and dashboard | Django | Business logic, webhook endpoints, and server-rendered dashboard views. |
| Interactive UI | Django templates + HTMX | Forms, filters, pagination, and partial page updates. |
| Charts | Chart.js | Progress, workload, and morale trends. |
| Database | PostgreSQL | Persistent application data and background job broker. |
| Models and migrations | Django ORM | Data access, relationships, constraints, and schema migrations. |
| Background jobs and scheduling | Django Q2 with the Django ORM broker | Feedback windows, targeted reminders, and blocker notifications. |
| Initial chat integration | Slack Bolt for Python | Slack commands, interactive modals, and action handlers. |
| Administration | Django Admin | Manage projects, memberships, and feedback cycles. |
| Authentication | Django sessions | Dashboard sign-in, with company SSO integration if required. |

This stack was selected for efficient internal-tool development, using Django's built-in authentication, ORM, and administration alongside a custom manager dashboard. The web application and Django Q2 worker will run as separate processes from one repository and share PostgreSQL. Redis is not required for the selected database-backed broker.

Slack is the initial integration assumption. Microsoft Teams remains a possible follow-up integration and requires its own SDK and interaction handlers; Slack Bolt does not support Teams. Project-level permissions must be enforced in backend queries for access to individual feedback.

```
 Slack Clients                         Dashboard Browser
      |                                       |
      | Webhooks                              | HTML / HTMX / Chart JSON
      v                                       v
 +--------------------------------------------------------+
 | Django Application                                     |
 | Slack Bolt for Python | Templates + HTMX | Django Admin |
 | Business Logic | Session Auth | Project Permissions     |
 +---------------------------+----------------------------+
                             | Django ORM
                             v
 +--------------------------------------------------------+
 | PostgreSQL: Application Data + Django Q2 ORM Broker     |
 +---------------------------+----------------------------+
                             ^
                             | Jobs / Schedules / Data
 +---------------------------+----------------------------+
 | Django Q2 Worker: Windows, Reminders, Blocker Alerts    |
 +---------------------------+----------------------------+
                             | Slack API
                             v
                        Slack Clients
```

### 4.1 Data Models (Database Schema Draft)

#### `users`
* `id` (UUID, Primary Key)
* `external_chat_id` (String - Slack/Teams User ID)
* `email` (String)
* `name` (String)
* `role` (Enum: `MEMBER`, `LEAD`, `ADMIN`)
* `created_at` (Timestamp)

#### `projects`
* `id` (UUID, Primary Key)
* `name` (String)
* `slack_channel_id` (String)
* `lead_id` (UUID, Foreign Key -> `users.id`)
* `created_at` (Timestamp)

#### `project_members`
* `project_id` (UUID, Foreign Key -> `projects.id`)
* `user_id` (UUID, Foreign Key -> `users.id`)
* Primary Key: (`project_id`, `user_id`)

#### `feedback_cycles`
* `id` (UUID, Primary Key)
* `project_id` (UUID, Foreign Key -> `projects.id`)
* `start_time` (Timestamp)
* `end_time` (Timestamp)
* `status` (Enum: `OPEN`, `CLOSED`)

#### `submissions`
* `id` (UUID, Primary Key)
* `cycle_id` (UUID, Foreign Key -> `feedback_cycles.id`)
* `user_id` (UUID, Foreign Key -> `users.id`)
* `progress_rating` (Integer 1-5)
* `workload_rating` (Integer 1-5)
* `morale_rating` (Integer 1-5)
* `highlights` (Text)
* `blockers` (Text)
* `has_blocker` (Boolean)
* `submitted_at` (Timestamp)

---

## 5. API & Integration Endpoints

### 5.1 Chat Webhooks / Slack Bolt Handlers
* `POST /api/slack/events` - Django endpoint using the Slack Bolt for Python adapter for events, slash commands, interactive buttons, and modal submissions. Configure the relevant Slack request URLs to use this endpoint.
* Blocker acknowledgment and resolution buttons are routed to Bolt action handlers through the same endpoint.
* Acknowledge Slack interactions promptly; enqueue notification delivery through Django Q2.

### 5.2 Dashboard Views and Chart Data
* `GET /projects/` - Django template listing active projects and member counts.
* `GET /projects/<uuid:project_id>/` - Custom project dashboard with HTMX filters and Chart.js visualizations.
* `GET /projects/<uuid:project_id>/metrics/` - JSON containing aggregated ratings over custom date ranges for Chart.js.
* `GET /projects/<uuid:project_id>/blockers/` - HTML page or HTMX partial showing recent and unresolved blockers.
* `GET /submissions/` - Paginated historical entries rendered as HTML or an HTMX partial.
* `/admin/` - Django Admin for authorized administrative users.

All dashboard views and chart endpoints require authentication and project-level authorization. The initial dashboard uses Django views rather than a separate frontend application or GraphQL API.

---

## 6. Implementation Roadmap

### Phase 1: Core Bot & Database
* Set up the Django project, PostgreSQL database, and Django ORM models and migrations.
* Register projects, memberships, and feedback cycles in Django Admin.
* Configure the Slack application and Slack Bolt for Python integration with Django.
* Implement Modal form creation & submission handling.

### Phase 2: Reminders & Escalations
* Configure Django Q2 scheduling and a separate worker process using PostgreSQL through the Django ORM broker.
* Build targeted logic for missing submission nudges.
* Develop real-time blocker notification routing to project leads.

### Phase 3: Web Dashboard 
* Develop the custom analytics dashboard using Django templates and HTMX.
* Build Chart.js visualizations for progress, workload, and morale trends across sprints/weeks.
* Implement Django session authentication and project-level permissions for leads and admins; integrate company SSO if required.
