from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import traceback

from .logic.process_pdf import (
    extract_text_from_pdf,
    find_pii_entities,
    find_nric_matches,
    redact_sensitive_text
)

app = FastAPI()

# --- CORS Configuration ---
# Define the list of origins that are allowed to make requests to this backend.
# For development, we'll allow our frontend's origin.
origins = [
    "http://localhost:3000",  # The origin of your Next.js frontend app
    # You could add other origins here if needed (e.g., a deployed frontend URL)
]

# Add the CORS middleware to the FastAPI application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins allowed
    allow_credentials=True, # Allows cookies to be included in requests (optional)
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all HTTP headers
)
# --- End CORS Configuration ---

# Define TEMP_DIR relative to main.py's location
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
# Create the temp directory if it doesn't exist
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def read_root():
    """ Basic endpoint to check if the server is running. """
    return {"message": "Hello from the Anonymizer Backend!"}

@app.post("/anonymize")
async def anonymize_pdf_endpoint(file: UploadFile = File(...)):
    """
    Receives a PDF file upload, processes it to redact PII,
    and returns the redacted PDF file for download.
    """
    temp_input_path = None
    temp_output_path = None
    unique_id = uuid.uuid4()

    try:
        print(f"Received file: {file.filename}")
        print(f"Content type: {file.content_type}")

        # Construct temporary paths
        temp_input_path = os.path.join(TEMP_DIR, f"{unique_id}_input.pdf")
        temp_output_path = os.path.join(TEMP_DIR, f"{unique_id}_output_redacted.pdf")
        print(f"Temporary input file path: {temp_input_path}")
        print(f"Temporary output file path: {temp_output_path}")

        # Step 1: Save the uploaded file temporarily
        try:
            with open(temp_input_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            print(f"Uploaded file saved temporarily to: {temp_input_path}")
        except Exception as e:
            print(f"Error saving uploaded file: {e}")
            return {"error": f"Could not save uploaded file: {e}"}
        finally:
            await file.close()
            print("Closed uploaded file handle.")

        # Step 2: Extract text (required for finding PII)
        extracted_text = extract_text_from_pdf(temp_input_path)
        if not extracted_text:
            if not os.path.exists(temp_input_path): # Should exist unless save failed
                 print("Error: Temporary input file missing before text extraction.")
                 return {"error": "Temporary file vanished before processing."}
            print("Warning: No text extracted from PDF. May be image-based or empty.")
            all_pii_to_redact = []
        else:
             # Step 2b: Find PII entities if text was extracted
            spacy_pii = find_pii_entities(extracted_text)
            nric_pii = find_nric_matches(extracted_text)
            combined_set = set(spacy_pii) | set(nric_pii)
            all_pii_to_redact = list(combined_set)
            print(f"Found {len(all_pii_to_redact)} unique PII items to search for redaction.")

        # Step 3: Perform Redaction
        redaction_successful = redact_sensitive_text(
            temp_input_path,
            temp_output_path,
            all_pii_to_redact # This list might be empty if no text/PII found
        )

        # Step 4: Prepare Response
        if redaction_successful:
            # Check if the output file actually exists before sending
            if os.path.exists(temp_output_path):
                print(f"Redaction successful. Preparing file response for: {temp_output_path}")
                # Return the actual redacted file as a download
                return FileResponse(
                    path=temp_output_path,
                    media_type='application/pdf',
                    filename=f"redacted_{file.filename}" # Suggest a download filename
                )
            else:
                 print(f"Warning/Error: Redaction function reported success, but output file '{temp_output_path}' not found. Sending original?")
                 return {"error": "Processing completed, but no redacted output file was generated (perhaps no PII found?)."}
        else:
            # Handle cases where redaction function reported failure
            print("Redaction process failed during execution.")
            return {"error": "Failed to process and redact the PDF file."}

    # Catch-all for unexpected errors during the whole process
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
        traceback.print_exc()
        return {"error": f"An internal server error occurred."}

    # Cleanup happens *after* FileResponse is prepared if successful,
    # or after error response if failed.
    finally:
        # Always try to delete the temporary *input* file
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.remove(temp_input_path)
                print(f"Deleted temporary input file: {temp_input_path}")
            except Exception as e:
                print(f"Error deleting temporary input file {temp_input_path}: {e}")

        # --- CRITICAL: We DO NOT delete temp_output_path here ---
        # FileResponse needs the file to exist when the response is sent.
        # Proper cleanup of output files requires a different approach
        # (e.g., a background task, scheduled cleanup, or deleting after download confirmation if possible).
        # For local testing, files will remain in backend/temp/.