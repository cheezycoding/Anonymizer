# Automated Text Anonymization Tool

This project provides a web-based tool for anonymizing personally identifiable information (PII) within PDF documents. It features a Next.js frontend and a FastAPI backend.

## Project Status (Current)

*   **Version Control:** Project initialized as a Git repository in the root directory and pushed to [GitHub](https://github.com/cheezycoding/Anonymizer).
*   **Backend (FastAPI - Python):**
    *   Located in the `backend/` directory.
    *   API server setup (`backend/main.py`).
    *   Core logic for PDF processing (`backend/logic/process_pdf.py`):
        *   Extracts text using `pdfplumber`.
        *   Identifies PII using `spaCy` (`en_core_web_sm`) and Regex (for NRICs).
        *   Redacts identified items using `PyMuPDF` (`fitz`).
    *   API endpoint (`/anonymize`) accepts PDF uploads and returns the redacted file.
    *   Uses CORS middleware (`fastapi.middleware.cors`) to allow requests from the frontend origin (`http://localhost:3000`).
    *   Dependencies managed via `backend/requirements.txt`.
*   **Frontend (Next.js - TypeScript):**
    *   Located in the `frontend/anonymize/` directory.
    *   User interface built using React and Tailwind CSS (`frontend/anonymize/app/page.tsx`).
    *   Allows users to select/upload a PDF file.
    *   Handles file upload to the backend API (`/anonymize`) using `fetch` and `FormData`.
    *   Receives the processed PDF from the backend as a `Blob`.
    *   Triggers an automatic browser download for the anonymized PDF.
    *   Includes basic error handling (including CORS fix) and loading states.
*   **End-to-End Flow:** Successfully tested locally. Users can upload a PDF via the frontend, have it processed by the backend, and receive the anonymized PDF as a download.

## Project Structure

```
anonymized-pdfs/  (Repository Root: Anonymizer)
├── backend/             # FastAPI application and PDF logic
│   ├── logic/           # Core PDF processing scripts
│   │   ├── __init__.py
│   │   ├── process_pdf.py
│   │   └── sample*.pdf  # Sample PDFs for testing
│   ├── temp/            # Temporary file storage (gitignored)
│   ├── __init__.py
│   ├── main.py          # FastAPI app definition and endpoints
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js application root
│   └── anonymize/       # The actual Next.js project
│       ├── app/           # App Router pages and layouts
│       │   ├── globals.css
│       │   ├── layout.tsx
│       │   └── page.tsx   # Main page UI component
│       ├── components/    # UI components (if any added later)
│       ├── public/        # Static assets
│       ├── .gitignore     # Frontend specific gitignore
│       ├── next.config.mjs
│       ├── package.json   # Node.js dependencies & scripts
│       ├── README.md      # Next.js default README
│       └── tsconfig.json
├── .gitignore           # Project root gitignore (IMPORTANT!)
├── README.md            # This file - project overview and status
└── venv/                # Python virtual environment (gitignored)
```

*(**Note:** `venv/`, `backend/temp/`, `backend/__pycache__/`, `frontend/anonymize/node_modules/`, and `frontend/anonymize/.next/` are ignored via the root `.gitignore` file.)*

## Deployment Plan

*   **Frontend:** Deploy to [Vercel](https://vercel.com/), connected to the GitHub repository.
*   **Backend:**
    1.  Containerize using Docker (`Dockerfile`).
    2.  Push Docker image to AWS ECR (Elastic Container Registry).
    3.  Deploy container on AWS ECS (Elastic Container Service) using the Fargate launch type.

## Setup & Running Locally

### Prerequisites

*   [Python](https://www.python.org/downloads/) >= 3.9
*   [Node.js](https://nodejs.org/) (which includes npm/npx) >= 18.x
*   [Git](https://git-scm.com/)
*   Ability to create Python virtual environments (`venv`).

### Backend Setup & Run

1.  Clone the repository: `git clone git@github.com:cheezycoding/Anonymizer.git`
2.  Navigate to the project root: `cd Anonymizer`
3.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
4.  Install Python dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
5.  Download the spaCy language model:
    ```bash
    python -m spacy download en_core_web_sm
    ```
6.  Run the FastAPI server (from the project root):
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
7.  The backend API is now available at `http://localhost:8000`. CORS is configured to allow requests from `http://localhost:3000`.

### Frontend Setup & Run

1.  Open a **new terminal** in the project root (`Anonymizer`).
2.  Navigate to the Next.js project directory:
    ```bash
    cd frontend/anonymize
    ```
3.  Install Node.js dependencies:
    ```bash
    npm install
    ```
4.  Run the Next.js development server:
    ```bash
    npm run dev
    ```
5.  The frontend application is now available at `http://localhost:3000`. 