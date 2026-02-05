# 🤖 Hybrid RAG Chatbot (Gemini Powered)

> **Your Intelligent Document Assistant.**
> Chat with your own documents (TXT, MD) with zero hallucinations, powered by advanced AI.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red?style=flat&logo=streamlit)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=flat&logo=docker)
![LangChain](https://img.shields.io/badge/AI-LangChain-green?style=flat)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=flat&logo=google)

## 📋 Description

This project implements a **Retrieval-Augmented Generation (RAG)** architecture that allows users to upload documents and ask natural language questions about them. The system retrieves relevant information and generates accurate answers citing the context.

**Core Engine:**
By default, the system uses **Google Gemini 3 Flash** (via API) for fast, high-quality, and cost-effective inference. It is also architected to support local models (Ollama) if needed.

## ✨ Key Features

- **Zero Hallucinations:** Answers are strictly grounded in the provided documents.
- **Multi-format Support:** Compatible with `.txt` and `.md` files.
- **Vector Memory:** Uses **ChromaDB** for efficient storage and retrieval of knowledge chunks.
- **Microservices Architecture:** Fully containerized with **Docker**, isolating the application logic.
- **Automated Installer:** Includes a `install.sh` script for one-click deployment.
- **User-Friendly Interface:** Built with Streamlit for a clean, responsive chat experience.

---

## 🚀 Installation & Usage

You have three ways to run this project:

### Option A: Docker Deployment (Recommended)

The easiest way to get everything running in isolation.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/my-rag-chatbot.git](https://github.com/your-username/my-rag-chatbot.git)
    cd my-rag-chatbot
    ```

2.  **Configure Environment:**
    Create a `.env` file in the root directory and add your Google API Key:
    ```bash
    GOOGLE_API_KEY=your_api_key_here
    ```

3.  **Start Services:**
    ```bash
    docker-compose up --build
    ```

4.  **Access:** Open your browser at [http://localhost:8501](http://localhost:8501).

---

### Option B: Client / Offline Mode (.tar Installer)

If you received the deployment package (without source code), follow these steps:

1.  **Unzip** the project folder.
2.  **Open a terminal** inside the folder.
3.  **Run the master script** (Recommended):
    ```bash
    chmod +x install.sh  # (Linux/Mac only) Grant permissions
    ./install.sh
    ```
    *The script will automatically load the Docker images, prompt for your API Key (if missing), and launch the application.*

#### ⚠️ Manual Configuration (Important)
If you are **not** using the `install.sh` script and want to run `docker-compose up` manually, you must ensure your `docker-compose.yml` is pointing to the pre-loaded image, not trying to build the code.

**Ensure your `docker-compose.yml` looks like this:**

```yaml
services:
  chatbot:
    # build: .                <-- COMMENT OUT or REMOVE this line
    image: chatbot_image:v1   # <-- USE the name of the image from the .tar file
    container_name: mi-chatbot-rag
    # ... rest of configuration
```
---

### Option C: Local Development (Python)

If you wish to modify the code locally without Docker:

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set API Key:**
    Create a `.env` file or export the variable in your terminal:
    ```bash
    export GOOGLE_API_KEY="your_key"
    ```

4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## ⚙️ Configuration

The chatbot's behavior can be tweaked in `config.py`.

| Variable | Description | Default Value |
| :--- | :--- | :--- |
| `MODEL_NAME` | LLM Model Name (e.g., `gemini-3-flash-preview`) | `"gemini-3-flash-preview"` |
| `CHUNK_SIZE` | Size of text chunks to read | `600` |
| `CHUNK_OVERLAP` | Overlap between chunks for context | `100` |
| `RETRIEVAL_K` | Number of chunks to retrieve per query | `5` |

### Switching to Local AI (Ollama)

Although configured for Gemini, you can switch to local models (Privacy Mode):
1.  Change `backend.py` to use `ChatOllama` instead of `ChatGoogleGenerativeAI`.
2.  Update `config.py` with the local model name (e.g., `llama3.2`).
3.  Ensure the Ollama service is running in `docker-compose.yml`.

---

## 📂 Project Structure

```text
.
├── app.py                 # Frontend (Streamlit UI)
├── backend.py             # RAG Logic, Embeddings & LLM connection
├── config.py              # Central Configuration
├── docker-compose.yml     # Service Orchestrator
├── Dockerfile             # App Image Build Instructions
├── install.sh             # Automatic Deployment Script
├── requirements.txt       # Python Dependencies
├── .dockerignore          # Files excluded from Docker image
└── .gitignore             # Files excluded from Git
