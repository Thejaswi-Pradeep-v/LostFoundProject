# 🔍 LLM-Powered Lost & Found Management System

An AI-powered Lost & Found platform that helps users report, search, and recover lost items efficiently using Large Language Models (LLMs), image analysis, and intelligent matching algorithms.

 📌 Problem Statement

Traditional lost-and-found systems rely heavily on manual processes, making it difficult to search, match, and recover items effectively. This project enhances the process by leveraging AI to automate item reporting, improve search accuracy, and assist users through a conversational interface.

🚀 Features

🤖 AI-Powered Chatbot

* Integrated Google Gemini AI
* Provides conversational assistance
* Helps users report and search for items
* Answers user queries in natural language

📸 Image-Based Auto-Fill

* Upload an image of a lost item
* AI extracts:

  * Item name
  * Category
  * Color
  * Distinguishing features
* Automatically populates report forms

🔎 Intelligent Item Search

* Natural language search
* Search using descriptions instead of exact keywords
* Semantic understanding of user queries

🎯 Smart Matching System

* Suggests potential matches between lost and found items
* Similarity-based recommendation engine
* Reduces manual verification effort

🔐 Secure Authentication

* User Registration
* Login & Logout
* Session Management

📊 Dashboard

* View reported items
* Track recovery status
* Monitor matches and activity

🏗️ System Architecture

```text
User
 │
 ▼
Frontend (HTML, CSS, JavaScript)
 │
 ▼
Flask Backend APIs
 │
 ├── Authentication Module
 ├── Item Management Module
 ├── AI Chatbot Module
 ├── Matching Engine
 │
 ▼
Database (MySQL/PostgreSQL)

AI Services
(Google Gemini API)
```

🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap

### Backend

* Python
* Flask

### Database

* MySQL / PostgreSQL

### AI & Machine Learning

* Google Gemini AI
* Prompt Engineering

### Tools

* Git
* GitHub
* VS Code

---

📂 Project Workflow

1. User logs into the system.
2. Reports a lost or found item.
3. Uploads an image (optional).
4. AI extracts item details.
5. Data is stored in the database.
6. Matching engine searches for similar records.
7. Potential matches are recommended.
8. Recovery status is updated when the item is returned.

🌟 Key AI Innovations

### Prompt Engineering

Custom prompts are designed to:

* Improve response quality
* Reduce hallucinations
* Generate structured outputs
* Maintain contextual awareness

### Conversational Assistance

* Intelligent user guidance
* Real-time support
* Better user experience

### AI-Assisted Data Extraction

* Automated item identification
* Reduced manual data entry
* Faster report creation

---

## 📈 Future Enhancements

* Mobile Application
* QR Code-Based Item Tracking
* Multi-Language Support
* Email & SMS Notifications
* Voice-Based Reporting
* Vector Database Search
* RAG-Based Knowledge Assistant
* Real-Time Location Tracking

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/your-username/LostFoundProject.git
```

### Navigate to Project

```bash
cd LostFoundProject
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

---

## 🎓 Learning Outcomes

This project demonstrates:

* Full Stack Development
* REST API Development
* Database Design
* LLM Integration
* Prompt Engineering
* AI-Powered Automation
* User-Centric Product Development
## 👨‍💻 Author

**Thejaswi Pradeep**

B.Tech Computer Science and Engineering
SCMS School of Engineering and Technology

⭐ If you found this project useful, consider giving it a star.
