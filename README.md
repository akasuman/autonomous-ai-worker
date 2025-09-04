# The Knowledge Vessel: An Autonomous AI Knowledge Worker

**The Knowledge Vessel is a full-stack web application designed to act as an automated research assistant. It fetches, processes, and summarizes information from the web, providing users with actionable insights on a professional, interactive dashboard.**

![Dashboard Screenshot](https://ibb.co/ZRbjb2hf) 
*Note: You will need to take a screenshot of your running application, upload it to a service like Imgur, and replace the URL above.*

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
git clone <https://github.com/akasuman/autonomous-ai-worker.git>
cd <cd ai-knowledge-worker>
## ▶️ Usage

To run the application, you must have three separate terminals open and running concurrently. Make sure to start them in the following order.

**1. Start the Qdrant Database (in Terminal 1):**
* From the project root (`Cothon_Project_Final`), start the Docker container:
    ```bash
    docker run -p 6333:6333 -p 6334:6334 -v ${PWD}/qdrant_data:/qdrant/storage qdrant/qdrant
    ```

**2. Start the Backend Server (in Terminal 2):**
* From the project root, activate the virtual environment and start the Uvicorn server:
    ```bash
    .\backend\venv\Scripts\activate
    uvicorn backend.main:app --reload
    ```

**3. Start the Frontend Server (in Terminal 3):**
* From the `frontend` directory, start the Next.js dev server:
    ```bash
    cd frontend
    npm run dev
    ```
* Open your browser and navigate to `http://localhost:3000`.

---