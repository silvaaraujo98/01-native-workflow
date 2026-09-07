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
| **Tech Stack** | Full-Stack Custom | Custom backend, official Chat API SDKs (e.g., Slack Bolt), custom SQL database, and web dashboard. |

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

```
                   +---------------------------------------+
                   |       Slack / MS Teams Clients        |
                   +-------------------+-------------------+
                                       |
                         Webhook / Bolt SDK Events
                                       v
                   +---------------------------------------+
                   |          Backend API Service          |
                   |    (Node.js / Express or Python)     |
                   +---------+-------------------+---------+
                             |                   |
               Database Queries                 REST / GraphQL API
                             v                   v
                   +-------------------+   +---------------+
                   |    PostgreSQL     |   | Next.js / React|
                   |     Database      |   | Admin Dashboard|
                   +-------------------+   +---------------+
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
* `POST /api/slack/events` - Handles slash commands, interactive buttons, and modal submissions.
* `POST /api/slack/actions` - Processes blocker resolution button clicks.

### 5.2 Dashboard REST API
* `GET /api/v1/projects` - List active projects and member counts.
* `GET /api/v1/projects/:id/metrics` - Fetch aggregated ratings (morale, workload, progress) over custom date ranges.
* `GET /api/v1/projects/:id/blockers` - Retrieve recent and unresolved blockers.
* `GET /api/v1/submissions` - Paginated list of historical weekly entries.

---

## 6. Implementation Roadmap

### Phase 1: Core Bot & Database (Weeks 1–2)
* Setup PostgreSQL database and ORM migrations.
* Build Slack/Teams Bolt application setup.
* Implement Modal form creation & submission handling.

### Phase 2: Reminders & Escalations (Weeks 3–4)
* Configure scheduled background cron jobs (e.g., BullMQ / Celery).
* Build targeted logic for missing submission nudges.
* Develop real-time blocker notification routing to project leads.

### Phase 3: Web Dashboard (Weeks 5–6)
* Develop Next.js / React analytics dashboard.
* Build chart visualizers for workload and morale trends across sprints/weeks.
* Implement authentication (OAuth / SSO) for leads and admins.
