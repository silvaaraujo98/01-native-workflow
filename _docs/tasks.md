# Weekly Project Feedback Tool — Backlog

This backlog implements the Django option in `_docs/plan.md`: Django templates, HTMX, Chart.js, PostgreSQL, Django ORM, Django Q2 with its ORM broker, and Slack Bolt for Python. Tasks are ordered for implementation; each description states the prerequisite capabilities needed for handoff, which does not imply that every task can run in parallel. Slack is the initial integration assumption; Teams and company SSO remain outside the initial implementation unless explicitly selected.

## 1. Set up an empty Django project with a passing test
Goal: Establish a runnable project with a working test command.
Description: Create an empty Django project with declared Python dependencies and a smoke test that verifies Django configuration loads successfully without requiring a database or Slack credentials. Document environment setup, the development server command, and the test command; completion requires that the smoke test passes from a fresh environment.

## 2. Configure PostgreSQL and environment settings
Goal: Connect Django to a reproducible local PostgreSQL environment.
Description: Using the empty Django project, configure database access and Django settings through environment variables, with a placeholder-only environment example and local database startup instructions. Verify database connectivity using Django's test database, and document that application migrations will follow after the custom user model is defined.

## 3. Define users and Slack identities
Goal: Store application users with Django-compatible authentication and Slack identity mapping.
Description: Using the configured Django project and PostgreSQL connection, introduce a custom user model before the first application migration, with UUID identity, email, name, MEMBER/LEAD/ADMIN role, creation time, and an optional unique Slack user ID for the initial workspace. Configure Django authentication to use this model, create its migration, and verify user creation and duplicate Slack identity rejection.

## 4. Define projects and memberships
Goal: Represent active projects, their leads, and participating users.
Description: Given the custom user model, add Django models and migrations for projects and project memberships, including project name, UUID, lead, Slack channel, creation time, and an active flag used by reminder queries. Enforce unique project/user membership and verify that duplicate memberships are rejected.

## 5. Define feedback cycles
Goal: Represent each project's time-bounded feedback window.
Description: Given project records, create a feedback cycle model with UUID, project reference, timezone-aware start and end times, and OPEN/CLOSED status. Reject invalid time ranges and duplicate windows for the same project, and verify that cycle records persist correctly in PostgreSQL.

## 6. Define feedback submissions
Goal: Store one valid weekly response per user and cycle.
Description: Given users and feedback cycles, add the submission model with UUID, three integer ratings from 1 to 5, highlights, blocker text, explicit has_blocker flag, and submission timestamp. Add database constraints for rating bounds and unique cycle/user pairs, and verify that invalid ratings and duplicate submissions are rejected.

## 7. Define blocker lifecycle records
Goal: Persist blocker acknowledgment and resolution separately from feedback text.
Description: Given feedback submissions, add a blocker record linked uniquely to a submission, with OPEN/ACKNOWLEDGED/RESOLVED status and nullable actor and timestamp fields for acknowledgment and resolution. Create the migration and verify that a new blocker starts open and that lifecycle metadata can be stored without changing the original feedback.

## 8. Add Django administration screens
Goal: Let authorized administrators manage the application's core records.
Description: Given the user, project, membership, cycle, submission, and blocker models, register them in Django Admin with useful list columns, search, and filters. Limit access to application administrators with Django staff access and make submitted feedback and lifecycle audit fields read-only; verify administrative access and denial for ordinary users.

## 9. Implement project-level authorization
Goal: Centralize which users can access project feedback and management actions.
Description: Given users, projects, and memberships, implement reusable policies under the initial rule that administrators can access all projects, assigned project leads can inspect their projects' feedback, and members can submit only to their own projects. Apply equivalent checks to queryset filtering and single-record access, and verify that a LEAD role alone does not grant access to unrelated projects.

## 10. Configure the Slack webhook integration
Goal: Receive authenticated Slack requests through Django.
Description: Given the Django project, mount the Slack Bolt for Python adapter at POST /api/slack/events and load the signing secret and bot token from environment variables. Document the initial workspace's app configuration, required permissions, and request URLs, and verify signed request handling and invalid signature rejection with local fixtures rather than real messages.

## 11. Create a Slack message delivery adapter
Goal: Provide one reusable interface for sending channel messages and direct messages.
Description: Given Slack Bolt configuration, wrap Slack API calls for opening direct conversations and posting messages so callers receive the destination and message timestamp. Surface rate limits and transient failures to callers without logging credentials or feedback text, and verify behavior with mocked Slack responses.

## 12. Implement the feedback submission service
Goal: Validate and persist feedback independently of the chat interface.
Description: Given submissions, blockers, cycles, and project authorization, create a transactional service accepting a mapped user, cycle ID, three ratings, highlights, blocker text, and an explicit blocker flag. Enforce membership and the open time window, create a blocker when flagged, and treat repeated submissions as already submitted; verify successful, unauthorized, closed-window, and duplicate cases.

## 13. Build the Slack feedback entry point and modal
Goal: Let eligible members open a short feedback form for a specific project cycle.
Description: Given the Slack webhook and project authorization, handle a Submit Feedback button carrying a cycle reference, map the Slack user to an application user, and open a modal with progress, workload, morale, highlights, blocker text, and an explicit blocker flag. Explain all rating scales and show useful responses for unmapped users, ineligible members, closed cycles, or completed submissions; verify the generated modal and access checks with mocked Slack calls.

## 14. Handle Slack modal submissions
Goal: Turn a submitted Slack form into validated stored feedback.
Description: Given the Slack modal and feedback submission service, parse view submissions, verify user and cycle context on the server, and return field errors or a success acknowledgment promptly. Invoke the service without sending downstream notifications inline, and verify valid forms, invalid values, tampered context, and repeated requests using webhook fixtures.

## 15. Configure Django Q2 workers and scheduling
Goal: Run background jobs using PostgreSQL without Redis.
Description: Given the Django project and PostgreSQL configuration, configure Django Q2 with its ORM broker, migrations, scheduler, and a separately started worker process. Document worker startup and ensure a harmless queued job and a scheduled job complete in the local environment with visible failure reporting.

## 16. Add durable notification delivery records
Goal: Track pending chat notifications and prevent ordinary duplicate enqueueing.
Description: Given Django Q2 and the Slack delivery adapter, create notification records with a unique event/recipient key, payload reference, delivery state, attempt count, next attempt time, and returned Slack message identifiers. Add a delivery job and pending-record dispatcher that retry transient failures and honor rate limits; verify retry and duplicate-enqueue behavior, and document that a crash after Slack accepts a message can still cause a duplicate.

## 17. Configure weekly project schedules
Goal: Store when each project opens, reminds, and closes its weekly check-in.
Description: Given project models and Django Admin, add a project timezone and configurable weekly opening, reminder, and cutoff settings with sensible documented defaults. Expose these fields in administration and validate their chronological order, including a schedule that crosses a week boundary.

## 18. Generate and close weekly feedback cycles
Goal: Maintain project feedback windows automatically.
Description: Given project schedules, feedback cycles, and Django Q2, implement a scheduled job that creates the current weekly window for each active project and closes expired cycles using timezone-aware timestamps. Ensure repeated runs do not create duplicate cycles or reopen completed ones, and verify boundary times and daylight-saving behavior using a controlled clock.

## 19. Send feedback window opening messages
Goal: Notify project members when their weekly feedback window opens.
Description: Given feedback cycles and durable notification delivery, create one opening notification per project cycle for its configured Slack channel, containing the Submit Feedback button and a readable deadline. Dispatch openings for currently open cycles even after a worker restart, and verify repeated scans do not create duplicate notification records.

## 20. Send targeted pending-member reminders
Goal: Remind only members who have not submitted before cutoff.
Description: Given project schedules, memberships, submissions, and durable notification delivery, schedule direct-message nudges for eligible members of active projects at the configured reminder time. Recheck missing-submission status and cycle eligibility before delivery, and verify that submitted users, closed cycles, and repeated scheduler runs do not produce unnecessary reminders.

## 21. Dispatch immediate blocker alerts
Goal: Notify the assigned project lead when feedback flags a blocker.
Description: Given the submission service, blocker records, and durable notification delivery, create a pending alert record in the submission transaction and trigger delivery after commit, with the dispatcher recovering pending alerts if enqueueing fails. Send a direct message to the assigned lead containing project context, blocker text, and Acknowledge/Mark Resolved buttons, and verify that unflagged feedback produces no alert and duplicate submissions produce no extra alert record.

## 22. Handle blocker acknowledgment and resolution
Goal: Let authorized leads update blocker status from Slack.
Description: Given blocker records, project authorization, and the Slack webhook, implement button handlers that map the acting Slack user and atomically record valid acknowledgment or resolution transitions with actor and timestamp. Acknowledge requests promptly and queue an update to the originating alert, verifying unauthorized actions, repeated clicks, and that resolved blockers cannot be reopened by a late acknowledgment.

## 23. Add dashboard session authentication and layout
Goal: Provide a protected, usable entry point for the web dashboard.
Description: Given Django authentication and project authorization, create login/logout views and a shared Django template layout with navigation, HTMX, and Chart.js assets. Protect dashboard routes with session authentication and CSRF handling for forms, and verify login, logout, and unauthenticated redirects; company SSO is deferred until a provider is selected.

## 24. Build the project list page
Goal: Show leads and administrators the projects they can review.
Description: Given the dashboard layout and project authorization, implement GET /projects/ with active project names, member counts, current cycle state, and links to each project dashboard. Filter records server-side and provide an empty state, verifying that unrelated projects never appear for a lead.

## 25. Build the project dashboard summary
Goal: Show the selected project's current feedback participation and health.
Description: Given the dashboard layout, project authorization, cycles, and submissions, implement GET /projects/<uuid:project_id>/ with project details, current-cycle submission counts, and average progress, workload, and morale ratings. Display clear states for no current cycle or no responses, and verify calculations and cross-project access denial with sample data.

## 26. Implement the chart metrics endpoint
Goal: Supply authorized, date-filtered trend data to Chart.js.
Description: Given project authorization, cycles, and submissions, implement GET /projects/<uuid:project_id>/metrics/ returning chronologically ordered cycle labels, submission counts, and average progress, workload, and morale ratings. Define the date range in terms of cycle start dates, represent cycles with no responses as null ratings rather than zero, and verify filtering, averages, invalid ranges, and unauthorized access.

## 27. Add dashboard trend charts and filters
Goal: Let leads inspect how project ratings change over time.
Description: Given the project dashboard and metrics endpoint, render Chart.js trends for progress, workload, and morale with a 1–5 scale and date-range controls using HTMX where appropriate. Explain that higher workload means greater load, handle empty/error responses, and verify that changing filters updates charts without duplicating chart instances.

## 28. Build the project blocker list
Goal: Let leads review recent and unresolved blockers for their projects.
Description: Given the dashboard layout, blocker records, and project authorization, implement GET /projects/<uuid:project_id>/blockers/ as a page or HTMX partial with status filters and pagination. Show original blocker text, submitter, cycle, status, and acknowledgment/resolution metadata, and verify filtering, empty states, and access isolation.

## 29. Build submission history
Goal: Let authorized reviewers browse past weekly feedback.
Description: Given the dashboard layout, submissions, and project authorization, implement GET /submissions/ with project and cycle-date filters, pagination, ratings, highlights, and blocker text. Return full HTML or an HTMX partial as appropriate, and verify stable pagination, escaped user text, and exclusion of feedback from unauthorized projects.

## 30. Add manual blocker categories and recurrence counts
Goal: Support the plan's recurring blocker category review without automated text analysis.
Description: Given the blocker list and project authorization, add an optional category field with a small documented initial vocabulary and let authorized leads assign it from the dashboard using a CSRF-protected form. Display category counts for the selected project's date range, including Uncategorized, and verify that editing or counting categories cannot expose another project's blockers.

## 31. Verify the complete weekly feedback workflow
Goal: Demonstrate that the integrated MVP supports a full check-in cycle.
Description: Given the implemented bot, scheduler, notifications, and dashboard, add an integration scenario using PostgreSQL, a controlled clock, and mocked Slack delivery to cover cycle opening, submission, a pending-member reminder, blocker acknowledgment/resolution, and cycle closure. Verify that the stored feedback appears in the authorized dashboard and that rerunning scheduled work does not create duplicate logical notifications.

## 32. Document local operation and manual acceptance checks
Goal: Make the MVP reproducible for a new developer or reviewer.
Description: Given the completed application, document database setup, migrations, administrator creation, user-to-Slack mapping, project schedule configuration, web and worker startup, and the initial Slack app setup with a reachable webhook URL. Include a short manual walkthrough for feedback submission, reminders, blocker actions, and dashboard review, plus how to inspect failed jobs and the remaining Teams/SSO decisions, without requiring credentials in the repository.
