# The Knowledge Vessel: An Autonomous AI Knowledge Worker

**The Knowledge Vessel is a full-stack web application designed to act as an automated research assistant. It fetches, processes, and summarizes information from the web, providing users with actionable insights on a professional, interactive dashboard.**

![Dashboard Screenshot](https://ibb.co/ZRbjb2hf) 
*Note: This is a placeholder URL. You will need to replace it with a real screenshot of your application.*

---
## 🚀 About The Project

This project was built as a one-month internship assignment for Cothon Solutions. The goal was to develop a production-grade, autonomous AI system that can handle data ingestion, AI processing, and deliver insights with minimal human input.

The application features a robust backend that connects to external data sources, processes text with AI models, and stores results in both relational and vector databases. The frontend is a modern, responsive dashboard for interacting with the AI.

### Key Features
* **Multi-Source Data Ingestion**: Gathers data from live news APIs (NewsAPI, Alpha Vantage) and allows for manual document uploads.
* **AI-Powered Processing**: Automatically generates concise summaries and extracts key topics from articles using a combination of the Hugging Face API and local NLU libraries.
* **Autonomous Operation**: Includes a background scheduler to perform research tasks automatically on a daily basis.
* **Intelligent Memory & Search**:
    * Stores all tasks and results in a PostgreSQL database for historical recall.
    * Implements semantic search over past results using a Qdrant vector database.
* **Professional Dashboard**: A stakeholder-friendly, dark-mode interface built with Next.js and Shadcn/ui, featuring an interactive task history and an analytics page.

---
## 🛠️ Tech Stack

### Frontend
* **Framework**: Next.js (React)
* **Styling**: Tailwind CSS
* **Component Library**: Shadcn/ui

### Backend
* **Framework**: FastAPI (Python)
* **Database (ORM)**: SQLAlchemy
* **Task Scheduling**: APScheduler

### Databases
* **Structured Data**: PostgreSQL
* **Vector Search**: Qdrant

### AI & Services
* **Summarization**: Hugging Face Inference API
* **Topic Extraction (NLU)**: TextBlob
* **Data Sources**: NewsAPI, Alpha Vantage

---
## ⚙️ Setup and Installation

To run this project locally, you will need Git, Python, Node.js, PostgreSQL, and Docker Desktop installed.

**1. Clone the Repository:**
```bash
git clone [https://github.com/akasuman/autonomous-ai-worker.git](https://github.com/akasuman/autonomous-ai-worker.git)
cd autonomous-ai-worker