# AI-Assisted Online Pharmacy System (Bot Pharmacist)

## 📌 Project Overview
[cite_start]The AI-Assisted Online Pharmacy System is a web-based platform that acts as an accessible digital triage and safety mechanism[cite: 71]. [cite_start]The system allows users to receive over-the-counter (OTC) medication recommendations based on their symptoms, check for dangerous interactions with current medications, and browse or order medication from a simulated digital storefront[cite: 26]. 

[cite_start]This project aims to alleviate the burden on public healthcare systems and promote safe self-medication by automating routine pharmacological safety checks using rule-based AI[cite: 73, 86].

## ✨ Key Features
- [cite_start]**Bot Pharmacist (AI Symptom Checker):** A rule-based recommendation engine that suggests OTC medication based on user symptoms, providing a confidence score and risk indicator[cite: 31, 74, 80].
- [cite_start]**Drug Interaction Warning System:** Prompts users to enter current medications before checkout to cross-reference and detect harmful drug-drug interactions, explaining the risk in plain language[cite: 82, 83, 85].
- [cite_start]**E-Commerce Functionality:** Browse medication, manage shopping carts, and a simulated checkout process[cite: 26].
- [cite_start]**User Management:** Secure user registration, authentication, and profile management[cite: 26].
- [cite_start]**Admin Dashboard:** Medication inventory management, user activity tracking, and AI recommendation log reviews[cite: 170].

## 🛠️ Technology Stack
[cite_start]The project follows a Client-Server architecture utilizing the Model-View-Controller (MVC) design pattern[cite: 156, 157].
- [cite_start]**Frontend:** React.js [cite: 159]
- [cite_start]**Backend:** Python 3, Django, and Django Rest Framework (DRF) [cite: 162, 312]
- [cite_start]**Database:** MySQL (Relational Database) [cite: 168, 175]
- [cite_start]**CI/CD & Version Control:** Git, GitHub Actions (Automated testing and security scans) [cite: 135, 136, 200]
- [cite_start]**AI Engine:** Custom Python-based deterministic rule engine using structured JSON/YAML mappings[cite: 324, 325].

## 👥 Meet the Team
[cite_start]This system is developed for the SFG117V/ISE117V module at Tshwane University of Technology[cite: 1, 3, 4].

| Name | Role | Key Responsibilities |
| :--- | :--- | :--- |
| **A Tsaku** | Full stack developer, AI developer | [cite_start]AI medication recommendation [cite: 13] |
| **A Mmboyi** | Full stack developer | [cite_start]User management [cite: 13] |
| **S Lubongo** | Full stack developer | [cite_start]Medication catalogue management [cite: 13] |
| **K Alfredo** | Full stack developer, AI developer | [cite_start]Order management, Drug interaction warning [cite: 13] |
| **N Bashizi** | Full stack developer | [cite_start]Admin management, Medication management [cite: 13] |

## 🚀 Getting Started

### Prerequisites
- Node.js (v16+)
- Python (3.9+)
- MySQL Server

### Backend Setup (Django)
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: 
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure your MySQL database settings in `core_api/settings.py`.
6. Apply migrations: `python manage.py migrate`
7. Start the server: `python manage.py runserver`

### Frontend Setup (React)
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

## ⚖️ Legal & Ethical Compliance
This project strictly adheres to South African data protection and medical guidelines:
- [cite_start]**POPIA Compliant:** Medical history and symptom data (Special Personal Information) require explicit opt-in consent and are encrypted at rest and in transit[cite: 332, 335, 338].
- **Scope Restriction:** The AI strictly recommends unscheduled or low-schedule OTC medication. [cite_start]It will not recommend Schedule 3+ prescription medication[cite: 344, 345].
- **Clinical Disclaimer:** The AI is a clinical decision support tool, not a human replacement. [cite_start]Persistent disclaimers advise users to consult healthcare professionals[cite: 354, 357].
