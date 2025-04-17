# Automated Text Anonymization Tool

This project provides a web-based tool for anonymizing personally identifiable information (PII) within PDF documents. It features a Next.js frontend and a FastAPI backend.

## Project Status (Current)

*   **Version Control:** Project initialized as a Git repository in the root directory and pushed to [GitHub](https://github.com/cheezycoding/Anonymizer).
*   **Frontend (Next.js - TypeScript):**
    *   Located in `frontend/anonymize/`.
    *   User interface built using React and Tailwind CSS.
    *   Handles PDF file upload and triggers download of the processed file.
    *   Deployed successfully to **Vercel**: [https://anonymizer-two.vercel.app/](https://anonymizer-two.vercel.app/)
    *   Vercel environment variable `NEXT_PUBLIC_API_URL` updated to point to the deployed backend URL. ✅
*   **Backend (FastAPI - Python):**
    *   Located in `backend/`.
    *   Core logic uses `pdfplumber`, `spaCy`, `PyMuPDF` for PII detection and redaction.
    *   API endpoint `/anonymize` processes uploaded PDFs.
    *   CORS initially configured for `localhost:3000` and the Vercel URL.
    *   **Dockerization:**
        *   `backend/Dockerfile` created to containerize the application. ✅
        *   Docker image `anonymizer-backend:latest` built successfully locally. ✅
        *   Container runs successfully locally, exposing the API on port 8000. ✅
    *   **Google Cloud Deployment:**
        *   Google Cloud project `anonymizer-pdf` created. ✅
        *   Artifact Registry API enabled. ✅
        *   Artifact Registry repository created (`asia-southeast1`). ✅
        *   Docker image pushed successfully to Artifact Registry. ✅
        *   Backend deployed to **Google Cloud Run** in `asia-southeast1` region using the container image: [https://anonymizer-backend-115653311564.asia-southeast1.run.app/](https://anonymizer-backend-115653311564.asia-southeast1.run.app/) ✅
        *   Cloud Run service configured with 1GiB RAM, 1 vCPU, min instances = 0, max instances = 1. ✅
*   **End-to-End Flow:**
    *   Working correctly when frontend (local or Vercel) communicates with the **local** backend. (MAYBE)
    *   Working correctly when backend tested directly via Cloud Run URL (`/` and `/docs`). ✅
    *   **Currently FAILING** when Vercel frontend attempts to call the deployed Cloud Run backend (`/anonymize` endpoint). ⚠️

## Current Issues

*   **CORS Preflight Failure:** When the deployed frontend on Vercel tries to upload a file to the deployed backend on Cloud Run, the request gets stuck in "Processing...". Browser developer tools indicate a CORS preflight (`OPTIONS`) request failure. Backend logs on Cloud Run do not show the `OPTIONS` or `POST` request arriving from the Vercel frontend during these failed attempts.
    *   **Attempted Fix:** Temporarily set `allow_origins=["*"]` in `backend/main.py` CORS middleware. This did not resolve the issue (likely due to incompatibility with `allow_credentials=True`).
    *   **Current Action:** Reverted `allow_origins` back to the specific list (`["http://localhost:3000", "https://anonymizer-two.vercel.app"]`). Currently rebuilding/redeploying the backend container image with this corrected configuration.

## Project Structure

```
anonymized-pdfs/  (Repository Root: Anonymizer)
├── backend/
│   ├── logic/
│   ├── temp/            # (gitignored)
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile       # Docker instructions for backend
├── frontend/
│   └── anonymize/       # Next.js project
│       ├── app/
│       ├── components/
│       ├── public/
│       ├── .gitignore
│       ├── next.config.mjs
│       ├── package.json
│       ├── README.md
│       └── tsconfig.json
├── .gitignore           # Project root gitignore
├── README.md            # This file
└── venv/                # (gitignored)
```

## Deployment Plan (Updated)

1.  **Frontend:** Deployed to [Vercel](https://vercel.com/). ✅
2.  **Backend:**
    1.  Containerize using Docker (`Dockerfile`). ✅
    2.  Push Docker image to **Google Artifact Registry**. ✅
    3.  Deploy container on **Google Cloud Run** (Fargate-like serverless). ✅
    4.  Update Vercel frontend environment variable (`NEXT_PUBLIC_API_URL`) to point to the deployed backend HTTPS URL. ✅
    5.  **Resolve CORS issue** between Vercel frontend and Cloud Run backend. (In Progress ⏳)

## Setup & Running Locally

### Prerequisites

*   [Python](https://www.python.org/downloads/) >= 3.9
*   [Node.js](https://nodejs.org/) >= 18.x
*   [Git](https://git-scm.com/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
*   Ability to create Python virtual environments (`venv`).

### Option 1: Run Backend Directly

1.  Clone repo: `git clone git@github.com:cheezycoding/Anonymizer.git && cd Anonymizer`
2.  Setup venv: `python -m venv venv && source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
3.  Install deps: `pip install -r backend/requirements.txt`
4.  Download model: `python -m spacy download en_core_web_sm`
5.  Run server: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

### Option 2: Run Backend via Docker (Recommended for Consistency)

1.  Clone repo: `git clone git@github.com:cheezycoding/Anonymizer.git && cd Anonymizer`
2.  Build image: `docker build -t anonymizer-backend ./backend`
3.  Run container: `docker run --rm -p 8000:8000 anonymizer-backend`

### Frontend Setup & Run (Connects to Backend on Port 8000)

1.  Open a **new terminal** in the project root (`Anonymizer`).
2.  Navigate to frontend: `cd frontend/anonymize`
3.  Install deps: `npm install`
4.  Run dev server: `npm run dev` (Frontend available at `http://localhost:3000`) 