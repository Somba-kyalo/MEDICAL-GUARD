MEDIGUARD
Medical Intelligence, Screening, Referral and Follow-up Platform

MEDIGUARD is a modular healthcare support platform designed to help healthcare workers and authorized users detect health risks, assess patients, support clinical decision-making, connect patients to appropriate facilities, follow up on care, and generate useful population-level insights.

The platform combines structured patient records, clinical screening, assistive AI, antimicrobial-resistance monitoring, referrals, facility information, follow-ups, notifications, analytics, and auditing into one integrated Django system.

Important: MEDIGUARD is a clinical support system. Its AI components are intended to assist qualified healthcare professionals and must not autonomously diagnose patients, prescribe medication, or replace professional clinical judgment.

1. Project Vision

Healthcare information is often fragmented across paper records, disconnected systems, delayed referrals, limited facility information, and inconsistent follow-up.

MEDIGUARD aims to provide a connected workflow:

Detect → Assess → Protect → Connect → Follow Up → Learn

Detect

Collect relevant patient information, symptoms, observations, history, and screening responses.

Assess

Analyze structured information and identify potential risks or areas requiring attention.

Protect

Provide healthcare workers with relevant warnings, antimicrobial-resistance information, and risk information.

Connect

Help connect patients with appropriate healthcare facilities and referral services.

Follow Up

Track what happens after screening, referral, or treatment.

Learn

Provide aggregated analytics that can help authorized users understand trends and system performance.

2. Main Objectives

MEDIGUARD is designed to:

Maintain structured patient information.
Support healthcare screening workflows.
Assist clinicians with AI-supported analysis.
Provide explanations for AI-generated results.
Support antimicrobial-resistance assessment.
Manage healthcare referrals.
Maintain healthcare facility information.
Track patient follow-ups.
Send relevant notifications and reminders.
Provide healthcare analytics.
Maintain an audit trail of important system activities.
Support secure role-based access.
Provide a foundation for future offline-first functionality.
Keep healthcare data organized around the patient.
3. Technology Architecture

MEDIGUARD is being developed as a modular Django monolith.

The system is divided into independent Django applications, with each application responsible for a specific domain.

Conceptually:

                         MEDIGUARD
                             │
                             ▼
                         AccountsApp
                             │
                             ▼
                         PatientsApp
                             │
                             ▼
                        ScreeningApp
                             │
                             ▼
                           AIApp
                             │
                             ▼
                          AmrApp
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
          ReferralsApp              AnalyticsApp
                │
                ▼
          FacilitiesApp
                │
                ▼
           FollowupsApp
                │
                ▼
        NotificationsApp

                 Important system actions
                           │
                           ▼
                       AuditApp

core provides the shared foundation across the entire platform.

4. Patient-Centered Architecture

The patient is the central entity around which most healthcare workflows are organized.

The conceptual relationship is:

Patient
   │
   ├── Screening
   │      │
   │      └── AI Analysis
   │
   ├── AMR Assessment
   │
   ├── Referrals
   │      │
   │      └── Healthcare Facility
   │
   └── Follow-ups
          │
          └── Notifications

Analytics can then consume appropriately aggregated information from these workflows.

5. Application Architecture

MEDIGUARD uses the following fixed application sequence:

1. core
2. AccountsApp
3. PatientsApp
4. ScreeningApp
5. AIApp
6. AmrApp
7. ReferralsApp
8. FacilitiesApp
9. FollowupsApp
10. AnalyticsApp
11. NotificationsApp
12. AuditApp

The order reflects the dependency and workflow structure of the system.

6. Security and Access Control

Healthcare information requires strong access control.

MEDIGUARD therefore separates:

Authentication
User accounts
Roles
Permissions
Patient access
Clinical actions
Administrative actions
Audit records

Users should only access information and actions appropriate to their role.

Potential roles can include:

Patient
Clinician
Healthcare worker
Facility administrator
System administrator
Analyst
Other authorized healthcare personnel

The exact role structure will be implemented based on the actual AccountsApp architecture rather than being assumed prematurely.

7. AI Safety Model

The AI component is intentionally designed as assistive intelligence.

The intended workflow is:

Patient Information
        │
        ▼
Clinical Screening
        │
        ▼
Structured Data
        │
        ▼
AI Analysis
        │
        ▼
Risk / Findings / Explanation
        │
        ▼
Clinician Review
        │
        ▼
Clinical Decision

The AI should not independently:

Diagnose a patient.
Prescribe medication.
Replace a clinician.
Make irreversible clinical decisions.
Present uncertain information as established fact.

Instead, AI output should be understandable, traceable, and reviewable.

8. Antimicrobial Resistance

MEDIGUARD includes a dedicated AmrApp.

The application can support information such as:

Antibiotic exposure.
Relevant patient history.
Laboratory/resistance information.
Resistance-related risk factors.
AMR assessment.
AMR surveillance.
Structured AMR results.

The purpose is to support healthcare workers and generate useful information for monitoring antimicrobial-resistance patterns.

9. Referral Workflow

The referral system connects patients with appropriate healthcare facilities.

Conceptually:

Patient
   │
   ▼
Screening / Assessment
   │
   ▼
Referral Required
   │
   ▼
ReferralsApp
   │
   ▼
FacilitiesApp
   │
   ▼
Selected Facility
   │
   ▼
Referral Tracking
   │
   ▼
FollowupsApp

This allows the system to track the referral beyond simply creating a referral record.

10. Healthcare Facilities

FacilitiesApp provides information about healthcare facilities.

Possible information includes:

Facility name
Location
Available services
Available resources
Contact information
Facility type
Operating information
Referral suitability

The application can later support map-based facility discovery.

11. Follow-up System

A referral or clinical interaction should not necessarily end after the initial encounter.

FollowupsApp supports:

Creating follow-up records.
Scheduling follow-ups.
Tracking follow-up status.
Recording follow-up outcomes.
Monitoring missed follow-ups.
Connecting follow-up activities with notifications.

Conceptually:

Initial Encounter
       │
       ▼
Referral / Care
       │
       ▼
Follow-up
       │
       ├── Completed
       ├── Pending
       ├── Missed
       └── Rescheduled
12. Notifications

NotificationsApp handles system notifications related to important events.

Examples include:

Follow-up reminders.
Referral updates.
Important system notifications.
Workflow reminders.
Other authorized healthcare notifications.

Notifications should be connected to actual system events rather than being randomly generated.

13. Analytics

AnalyticsApp converts appropriate system data into useful aggregated information.

Potential analytics include:

Screening trends.
AMR trends.
Referral trends.
Follow-up trends.
Facility utilization.
Healthcare workflow statistics.

Analytics should respect privacy and access controls.

The analytics layer should not expose unnecessary patient-identifying information.

14. Audit and Accountability

Healthcare systems need accountability.

AuditApp records important actions such as:

Who performed an action.
What type of action occurred.
When it occurred.
What resource was involved.
Relevant request/context information where appropriate.

Conceptually:

User
  │
  ▼
System Action
  │
  ▼
AuditApp
  │
  ▼
Audit Record

This provides an accountability layer across MEDIGUARD.

15. Frontend Approach

MEDIGUARD uses a practical Django frontend architecture.

The project will favor:

Django templates where appropriate.
Bootstrap for common UI components.
JavaScript for dynamic interactions.
JSON/API-driven interactions where useful.
Minimal custom HTML.
Minimal custom CSS.
App-specific static assets.

For example:

ScreeningApp/
└── static/
    └── ScreeningApp/
        ├── ScreeningApp.js
        └── ScreeningApp.css

Rather than putting every application's JavaScript and CSS into one large global file.

16. User Interface

MEDIGUARD follows a restrained clinical interface.

Default theme

Dark mode

Supported theme

Light mode

Main visual direction
Navy blue
Blue
White
Black
Dark surfaces
Light gray
Restrained red
Restrained green

The interface should prioritize:

Readability
Accessibility
Clear information hierarchy
Simple navigation
Clinical professionalism
Responsive design

The interface should avoid excessive:

Neon colors
Glowing effects
Unnecessary animations
Oversized decorative elements
Visually distracting components
17. Database Philosophy

The database should represent actual relationships between healthcare entities.

Important conceptual relationships include:

User
 │
 └── Patient/User Profile
          │
          ├── Screenings
          │      └── AI Analyses
          │
          ├── AMR Assessments
          │
          ├── Referrals
          │      └── Facility
          │
          └── Follow-ups

The exact database fields and foreign-key relationships will be implemented after inspecting the existing code for each application.

No model should be introduced merely because it sounds useful without understanding where it belongs in the existing architecture.

18. API and Service Architecture

Where appropriate, applications will separate responsibilities into:

models.py
services.py
serializers.py
validators.py
views.py
urls.py
Models

Represent persistent data.

Services

Contain business logic.

Serializers

Convert model/application data into structured API representations.

Validators

Validate incoming information and domain-specific rules.

Views

Handle HTTP/API requests.

URLs

Expose application endpoints.

This keeps complex business logic out of views wherever practical.

19. Testing Strategy

Every application should eventually have automated tests.

Testing will cover:

Models.
Validation.
Services.
Views.
API behavior.
Permissions.
Important workflows.
Application integrations.

At project level, important checks include:

python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test

Manual browser testing will also be performed for important workflows.

20. Development Workflow

MEDIGUARD will be developed incrementally.

For each application:

Understand
   ↓
Inspect existing code
   ↓
Design relationships
   ↓
Implement
   ↓
Migrations
   ↓
Automated tests
   ↓
Integration
   ↓
Manual testing
   ↓
Git commit
   ↓
Next application

An important project rule is:

Existing code is inspected before modifying it.

This prevents accidentally replacing working functionality or creating relationships that conflict with the existing architecture.

21. Git Workflow

Development will be tracked with Git.

A change should be committed after meaningful file creation or modification.

Example:

git status
git add .
git commit -m "add screening risk validation"

This gives MEDIGUARD a clear development history and makes it easier to identify or revert problematic changes.

22. Future Development Areas

After the core platform is stable, MEDIGUARD can be extended with:

Advanced AI/ML models.
Model evaluation.
Offline-first capabilities.
Progressive Web App functionality.
Synchronization.
More sophisticated analytics.
Facility mapping.
Advanced notifications.
Improved security controls.
Deployment infrastructure.
Monitoring.
Performance optimization.

These should come after the core MVP workflow works reliably.

23. Core MEDIGUARD Workflow

The complete conceptual workflow is:

                    MEDIGUARD

                       USER
                        │
                        ▼
                 AccountsApp
                        │
                        ▼
                  PatientsApp
                        │
                        ▼
                 ScreeningApp
                        │
                        ▼
                     AIApp
                        │
                        ▼
                    AmrApp
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        ReferralsApp         AnalyticsApp
              │
              ▼
        FacilitiesApp
              │
              ▼
         FollowupsApp
              │
              ▼
      NotificationsApp

       All important actions
               │
               ▼
           AuditApp

This represents the overall architecture, while individual database relationships will be determined from the actual implementation.

24. Complete App List and Functions
#	App	Main Function
1	core	Shared project foundation and common system functionality
2	AccountsApp	Users, authentication, roles and permissions
3	PatientsApp	Patient profiles and patient-centered records
4	ScreeningApp	Clinical screening and structured health assessment
5	AIApp	Assistive AI analysis, risk assessment and explanations
6	AmrApp	Antimicrobial-resistance assessment and surveillance
7	ReferralsApp	Patient referral creation and tracking
8	FacilitiesApp	Healthcare facilities, services, resources and locations
9	FollowupsApp	Follow-up scheduling, tracking and outcomes
10	AnalyticsApp	Aggregated healthcare and system analytics
11	NotificationsApp	Reminders, alerts and system notifications
12	AuditApp	Audit logging, accountability and activity tracking
1. core

Function: The foundation of MEDIGUARD.

Responsible for:

Shared project functionality.
Home page.
Common dashboard functionality.
Error handling.
Shared utilities.
Global/common configuration where appropriate.
Theme foundation.
Common system-level components.

Does NOT own: patient-specific clinical logic.

2. AccountsApp

Function: Determines who is using MEDIGUARD.

Responsible for:

User registration.
Login.
Logout.
Authentication.
Password management.
Password reset.
User profiles.
Roles.
Permissions.
Access control.
User-related security.
3. PatientsApp

Function: Determines who the patient is and what patient information belongs to them.

Responsible for:

Patient profiles.
Patient demographic information.
Patient records.
Patient details.
Patient history/timeline.
Patient record editing.
Patient record listing.
Patient-centered relationships.
4. ScreeningApp

Function: Determines what health information is being collected and assessed.

Responsible for:

Screening forms.
Symptoms.
Clinical observations.
Patient responses.
Relevant history.
Screening validation.
Screening results.
Screening history.
Clinical review workflow.
Preparing structured information for AI analysis.
5. AIApp

Function: Provides assistive intelligence.

Responsible for:

Screening analysis.
Risk assessment.
AI-generated explanations.
AI recommendations/support.
AI prompts.
AI validation.
AI services.
AI engine integration.
Clinician-review workflow.

The AI layer remains assistive, not autonomous.

6. AmrApp

Function: Handles antimicrobial-resistance information.

Responsible for:

AMR assessment.
Antibiotic-related information.
Resistance-related risk factors.
AMR rules.
AMR services.
AMR results.
AMR surveillance.
AMR-related reporting.
7. ReferralsApp

Function: Handles connecting patients to additional healthcare services.

Responsible for:

Creating referrals.
Referral details.
Referral status.
Referral tracking.
Referral history.
Referral updates.
Connecting referrals to facilities.
Referral workflow.
8. FacilitiesApp

Function: Determines where a patient can receive appropriate healthcare services.

Responsible for:

Healthcare facilities.
Facility profiles.
Facility locations.
Facility services.
Facility resources.
Facility details.
Facility search/listing.
Facility maps.
Referral destination information.
9. FollowupsApp

Function: Determines what happens after the initial healthcare interaction.

Responsible for:

Follow-up creation.
Follow-up scheduling.
Follow-up details.
Follow-up status.
Follow-up outcomes.
Missed follow-ups.
Follow-up tracking.
Post-referral monitoring.
10. AnalyticsApp

Function: Determines what the collected system information tells us at an aggregated level.

Responsible for:

Screening analytics.
AMR analytics.
Referral analytics.
Follow-up analytics.
Facility analytics.
Dashboards.
Aggregated statistics.
Trend analysis.
System-level reporting.

It should protect patient privacy and avoid unnecessary exposure of identifiable information.

11. NotificationsApp

Function: Keeps users informed about relevant system events.

Responsible for:

Notifications.
Follow-up reminders.
Referral notifications.
Status updates.
System alerts.
Scheduled notification tasks.
Notification history.
12. AuditApp

Function: Provides accountability and traceability.

Responsible for:

Audit logs.
User activity tracking.
Important system actions.
Record access tracking where appropriate.
Change tracking.
Timestamping.
Accountability.
Security investigation support.
Final MEDIGUARD Structure

The entire platform can therefore be remembered as:

CORE
 │
 ▼
ACCOUNTS
 │
 ▼
PATIENTS
 │
 ▼
SCREENING
 │
 ▼
AI
 │
 ▼
AMR
 │
 ├──────────────► REFERRALS ─────────► FACILITIES
 │                                      │
 │                                      ▼
 │                                  FOLLOWUPS
 │                                      │
 │                                      ▼
 │                                NOTIFICATIONS
 │
 └──────────────► ANALYTICS

ALL IMPORTANT ACTIONS
          │
          ▼
        AUDIT

And the 12 apps we are working on are fixed as:

core → AccountsApp → PatientsApp → ScreeningApp → AIApp → AmrApp → ReferralsApp → FacilitiesApp → FollowupsApp → AnalyticsApp → NotificationsApp → AuditApp.