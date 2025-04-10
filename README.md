# Automated Text Anonymization Tool

This project aims to provide a web-based tool for anonymizing personally identifiable information (PII) within PDF documents.

## Project Status (As of Last Interaction)

*   **Backend:**
    *   FastAPI server setup (`backend/main.py`).
    *   Core logic for PDF processing (`backend/logic/process_pdf.py`):
        *   Extracts text using `pdfplumber`.
        *   Identifies PII using `spaCy` (pre-trained model `en_core_web_sm`) for general entities (PERSON, GPE, LOC, ORG, DATE).
        *   Identifies Singapore NRIC patterns using Regular Expressions.
        *   Redacts identified items using `PyMuPDF` (`fitz`) by applying black bars.
    *   API endpoint (`/anonymize`) implemented in `main.py`:
        *   Accepts PDF file uploads.
        *   Saves uploads to a temporary directory (`backend/temp/`).
        *   Calls processing logic functions.
        *   Returns the redacted PDF file directly using `FileResponse`.
    *   Dependencies managed via `backend/requirements.txt` (including `spacy`, `python-multipart`).
    *   Project structured as Python packages (using `__init__.py` files).
    *   Tested locally using FastAPI's interactive `/docs` UI (file download successful).
*   **Frontend:**
    *   Next.js project setup using App Router (`frontend/anonymize/`).
    *   Basic UI created (`frontend/anonymize/app/page.tsx`) with:
        *   File input restricted to PDFs.
        *   Button to trigger upload (logic not yet implemented).
        *   Client-side state (`useState`) to track the selected file using `'use client';`.
    *   Frontend development server (`npm run dev`) confirmed working.

## Project Structure

```
anonymized-pdfs/
├── backend/             # FastAPI application and PDF logic
│   ├── __init__.py
│   ├── logic/           # Core PDF processing scripts
│   │   ├── __init__.py
│   │   ├── process_pdf.py
│   │   └── sample_sg.pdf  # Sample PDF for testing
│   ├── main.py          # FastAPI app definition and endpoints
│   ├── requirements.txt # Python dependencies
│   └── temp/            # Temporary file storage (gitignore recommended)
├── frontend/            # Next.js application
│   └── anonymize/       # Root of the Next.js project
│       ├── app/           # App Router pages and layouts
│       │   ├── layout.tsx
│       │   └── page.tsx   # Main page UI
│       ├── node_modules/  # (gitignore recommended)
│       ├── public/        # Static assets
│       ├── package.json   # Node.js dependencies
│       └── ... (other Next.js config files)
├── venv/                # Python virtual environment (gitignore recommended)
├── .gitignore           # Specifies intentionally untracked files
└── README.md            # This file - project overview and status
```

## Next Steps (Planned)

1.  **Implement Frontend Upload Logic:** In `frontend/anonymize/app/page.tsx`, add the JavaScript code (`fetch` or `axios`) inside the `handleUpload` function to actually send the `selectedFile` to the backend API (`http://localhost:8000/anonymize`).
2.  **Handle Frontend Download:** Implement logic to receive the `FileResponse` from the backend and trigger the browser's download mechanism for the user.

## Setup & Running Locally

### Prerequisites

*   [Python](https://www.python.org/downloads/) >= 3.9
*   [Node.js](https://nodejs.org/) (which includes npm/npx) >= 18.x
*   Ability to create Python virtual environments (`venv`).

### Backend Setup & Run

1.  Navigate to the project root (`anonymized-pdfs`).
2.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```
3.  Install Python dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  Download the spaCy language model:
    ```bash
    python -m spacy download en_core_web_sm
    ```
5.  Run the FastAPI server (from the project root):
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```
6.  The backend API is now available at `http://localhost:8000`. Test via `http://localhost:8000/docs`.

### Frontend Setup & Run

1.  Open a **new terminal**.
2.  Navigate to the Next.js project directory:
    ```bash
    cd frontend/anonymize
    ```
3.  Install Node.js dependencies (if not already done):
    ```bash
    npm install
    ```
4.  Run the Next.js development server:
    ```bash
    npm run dev
    ```
5.  The frontend application is now available at `http://localhost:3000`. 