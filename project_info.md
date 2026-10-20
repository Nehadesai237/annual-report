# Synopsis

- **Project Title :-** EduReport an annual report portal
- **Guide :-** Prof.A.S.Phalle
- **Area / Domain of Project :-** Web development and Machine learning

(1) **Introduction** :- Educational institutes generate a large volume of data annually across various
departments—academic, research, finance, infrastructure, and extracurricular activities. Preparing
a comprehensive and accurate annual report from this data is often time-consuming, inconsistent,
and manual.

(2) **Motivation :-** Preparing annual reports in educational institutes is often a manual, repetitive, and
error-prone process. Each department works in silos, leading to delays, data inconsistency, and
lack of standardization. There is a growing need for a unified, efficient, and automated solution
that simplifies data collection, enhances collaboration, and presents insights in a structured format.
This motivated the development of EduReport — a smart portal that streamlines annual report
creation and supports informed decision-making through accurate and well-organized data.

(3) **Existing System** :- In most educational institutes, the annual report preparation process is manual
and decentralized. Each department typically collects its own data using spreadsheets, word
documents, or emails. These reports are then individually submitted to a central authority for
compilation. This approach lacks standardization, consumes significant time, and increases the
chances of data duplication, inconsistency, and human error.

(4) **Drawbacks/limitations/challenges in Existing System** :-

- Manual Process: Time-consuming and prone to errors and duplication.
- Lack of Standardization: Inconsistent data formats across departments.
- No Collaboration Tools: Limited scope for real-time editing or feedback.
- Poor Data Visualization: Absence of graphs or dashboards for insights.
- Version Control Issues: Difficult to manage and track document updates.
- Security Risks: Unsecured sharing of sensitive institutional data.

(5) **Problem Statement :-**
Develop a portal to streamline data collection and generate accurate, consistent annual reports for
educational institutions.


```
(6) Feasibility Study :-
The feasibility study evaluates the technical, operational, and economic aspects of EduReport.
Technically, the project is feasible as the required technologies (React, Python/Django/Flask,
MongoDB, ML frameworks) are readily available. Operational feasibility is ensured since institutes
already collect such data and users are familiar with web portals. Economically, the system reduces
manual workload and long-term costs, making it cost-effective.
```
```
(7) Project Scope :-
```
1. Data collection and integration
2. Data analysis and visualization
3. Report generation
4. Collaboration and feedback
5. User authentication and role management

```
(8) Requirement Engineering :-
Requirement engineering involves the systematic process of eliciting, analyzing, documenting, and
validating requirements. For EduReport, this includes functional requirements (user management,
activity submission, ML verification, reporting) and non-functional requirements (usability,
performance, security, scalability). Stakeholder discussions and iterative feedback will guide the
refinement of requirements.
```
```
(9) Software Requirement Specification (SRS) :-
```
- **Functional Requirements**
1. User Authentication & Roles – Secure login, role-based access.
2. Data Collection & Integration – Import from databases/spreadsheets, system integration, manual
entry.
3. Analysis & Visualization – KPIs dashboards, charts, graphs.
4. Report Generation – Automated PDF/HTML reports, customizable templates, multimedia support.
5. Collaboration & Feedback – Editing, reviews, feedback, version control.
6. User Experience – Intuitive UI, responsive design, multilingual support.


- **Non-Functional Requirements**
1. Performance – Fast, responsive, handles large data.
2. Security – Compliance (GDPR/FERPA), strong protection.
3. Scalability – Works for different institutes, supports growth.
- **System Architecture**
1. Frontend – HTML, CSS, JS (Bootstrap/Materialize).
2. Backend – Python/Java with MySQL/MongoDB.
3. Integration – APIs, import/export (CSV, Excel).
- **Data Management**
1. Storage – Structured DB, backup & recovery.
2. Security – Encryption, access control, audits.
- **Testing**
1. Unit Testing – Individual modules.
2. Integration Testing – External systems/data.
3. User Acceptance – End-user validation.
- **Deployment & Maintenance**
1. Deployment – Phased rollout.
2. Maintenance – Updates, bug fixes, support.

```
(10) Project Overview :-
EduReport is a smart web-based system designed to automate the annual report preparation process
in educational institutions. It integrates data collection, ML-based content validation, secure storage,
and structured report generation. By reducing manual effort and improving accuracy, the system
ensures consistency, transparency, and efficiency across departments. The project contributes to
digital transformation in academic administration and enhances decision-making through insightful
reports.
```

```
(11) Proposed Work :-
(1) Block Diagram :
```
```
notify
```
```
Check
manually
```
User
(Student)

```
Authentication
(registration,login)
```
```
Activity selection
(social gathering,sports,academic)
```
```
Acitivity details
(text, images)
```
```
Database
(store data)
```
```
Checking the images
By using ML algorithm
(normal or abnormal)
```
```
If normal images
accepted
```
```
If abnormal images
rejected
```
```
Admin
(check
images)
```
```
If accept
```
```
Report
```
```
Individual Group^
```
```
View report
(pdf)
```
```
If reject
```
```
discard
```
```
Individual Group
```
```
Start
```
```
End
```
```
End
```

**Description of the diagram:**

1. User (Student)
A student starts by accessing the system.
2. Authentication (Registration/Login)
The student registers if new, or logs in if already registered.
Authentication ensures only authorized users can submit activities.
    3. Activity Selection
    The student selects the type of activity: social, sports, or academic.
    4. Activity Details (Text and Images)
    The student uploads descriptions and supporting images of the activity.
    5. Image Verification using ML Algorithm
    The system automatically checks uploaded images using a machine learning algorithm
       to detect whether they are normal or abnormal (valid or invalid content).
    6. Decision Branch: Image Accepted or Rejected
    If accepted: Data is sent directly to the database.
    If rejected: The system notifies the Admin.
    7. Manual Verification by Admin
    The admin manually checks the rejected images.
    If the admin approves, the data is added to the database.
    If not approved, the image/data is discarded.
    8. Database Storage
    Approved data is stored securely in the database.
    9. Report Generation
    Students and faculty can view the report in PDF format.
    Reports can be generated for individual students or groups.

```
(2) Modules :
```
**1. User Management Module**
Registration & Login
    Handles new user sign-ups and secure logins.
    Includes email verification or OTP (optional).
    Authentication & Authorization
    Role-based access (Student vs. Admin).


**2. Activity Submission Module**
    Activity Selection
    Students choose type: Social, Sports, Academic.
    Data Upload
    Input form for text description.
    File/image upload (with size & format checks).
    Client-side Validation
    Ensures required fields are filled before submission.
    **3. Machine Learning Image Verification Module**
    Image Preprocessing
    Resize, normalize, and clean images before ML model input.
    ML Model Integration
    Model to classify uploaded images as normal or abnormal.
    Can be trained using CNN (e.g., TensorFlow/Keras or PyTorch).
    Decision Engine
    If accepted → send to DB.
    If rejected → notify admin for manual review.
    **4. Admin Review Module**
    Notification System
    Alerts admin about rejected submissions.
    Manual Verification Dashboard
    View rejected images, approve or discard.
    Audit Logging
    Keep records of all approvals/rejections for transparency.
    **5. Database Module**
    Data Storage
    User data, activity details, ML results.
    Schema Design
    Tables for Users, Activities, Images, Reports, Admin logs.
    Database Management
    MySQL / PostgreSQL / MongoDB depending on stack choice.
    **6. Report Generation Module**
    Report Type Selection
    Individual report vs. Group report.
    PDF Generation
    Using libraries like ReportLab (Python) or jsPDF (JavaScript).
    Download / View Interface
    Secure access to reports for both users and admins.

```
7.Notification & Feedback Module
```

```
Email Alerts (SMTP, SendGrid, etc.)
In-App Notifications
Status Updates for students (Accepted, Rejected, Pending).
```
```
( 3 ) Architecture Diagram:
```
```
Input Output
```
```
Devlopment Environment :-
```
```
(3) Software Requirements :
Operating System:
Windows 10 or later / Ubuntu 20.04+ / macOS Monterey or later
```
```
Frontend Development:
Code Editor: VS Code /netbeans
Framework: React.js
Browser: Chrome / Firefox (for testing)
```
```
Backend Development:
Language: Python (Flask / Django) or Node.js
```
User
(Student)

```
Authentication module
```
```
Activity submission module
```
```
ML image verification module
```
```
If normal image If abnormal image^
```
```
Report
generation
module
(pdf)
```
```
Database
module
```
```
Admin review
```

```
Package Managers: pip / npm
```
```
Database:
MongoDB (if NoSQL flexibility is required)
```
```
Machine learning:
Dataset: Kaggle
NLP: text processing
```
```
Reporting & Visualization:
Libraries: Chart.js, D3.js, Recharts
```
```
Version Control:
Git & GitHub (for code collaboration and tracking)
```
```
Other Tools:
XAMPP/WAMP (optional for local DB testing) Docker
(optional for containerization)
draw.io / Figma (for diagrams and UI design)
```
```
(4) Hardware Requirements :
Component Minimum Specification
Processor (CPU) Intel i3 / AMD Ryzen 3
RAM 4 GB 8 GB or more
Storage 256 GB HDD/SSD
Display 13" or larger Full HD Monitor
Internet Stable broadband connection
```
```
(7) References :-
i.Journal/Conference Papers:
https://www.researchgate.net/publication/388826881_ANNUAL_REPORT_PORTAL_FOR_
EDUCATI ONAL_INSTITUTES_Department_of_computer_science
```
```
ii.Web reference link:
https://www.ijaresm.com/annual-report-portal-for-educational-institutions
```
Prof. A.S.Phalle Prof. T.H.Patil Dr. R. B. Patil
**Project Guide FYP, Coordinator HoD, CSE**