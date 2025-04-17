# Automated PDF Anonymization Tool

This project offers a user-friendly web application for automatically identifying and redacting Personally Identifiable Information (PII) within uploaded PDF documents. It leverages Natural Language Processing (NLP) via spaCy to detect entities like names and locations and finetuned  specific patterns (e.g., Singapore NRIC numbers), before generating a downloadable, anonymized version of the PDF with the sensitive information blacked out.

## Live Application

You can access the deployed application here:
[https://anonymizer-two.vercel.app/](https://anonymizer-two.vercel.app/)

## Technology Stack

*   **Frontend:** [Next.js](https://nextjs.org/) (React, TypeScript, Tailwind CSS) Deployed on Vercel
*   **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python) Deployed on Google Cloud. Uses **spaCy** for NLP (Named Entity Recognition) and **PyMuPDF** for PDF manipulation.
*   **Containerization:** [Docker](https://www.docker.com/)

## Project Structure

```
anonymized-pdfs/
├── backend/
│   ├── logic/
│   ├── temp/            # (gitignored)
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── anonymize/       # Next.js project
│       ├── app/
│       ├── components/
│       ├── public/
│       ├── .gitignore
│       ├── next.config.ts # Note: Previous README listed .mjs, ensure correct extension
│       ├── package.json
│       ├── README.md
│       └── tsconfig.json
├── .gitignore           # Project root gitignore
├── README.md            # This file
└── venv/                # (gitignored)
```

## Running Locally

### Prerequisites

*   [Python](https://www.python.org/downloads/) >= 3.9
*   [Node.js](https://nodejs.org/) >= 18.x
*   [Git](https://git-scm.com/)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine

### Backend (Docker - Recommended)

1.  Clone repo: `git clone https://github.com/cheezycoding/Anonymizer.git && cd Anonymizer`
2.  Build image: `docker build -t anonymizer-backend ./backend`
3.  Run container: `docker run --rm -p 8000:8000 anonymizer-backend`
    *The backend API will be available at `http://localhost:8000`.*

### Backend (Directly - Alternative)

1.  Clone repo and `cd Anonymizer`
2.  Setup venv: `python -m venv venv && source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
3.  Install deps: `pip install -r backend/requirements.txt`
4.  Download model: `python -m spacy download en_core_web_sm`
5.  Run server: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

### Frontend

1.  Open a **new terminal** in the project root (`Anonymizer`).
2.  Navigate to frontend: `cd frontend/anonymize`
3.  Install deps: `npm install`
4.  **(Important)** Create a `.env.local` file in the `frontend/anonymize` directory and add the backend URL:
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```
5.  Run dev server: `npm run dev`
    *The frontend will be available at `http://localhost:3000`.* 