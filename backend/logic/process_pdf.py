# backend/logic/process_pdf.py

# Import the pdfplumber library, which helps us work with PDFs
import pdfplumber
# Import the os library, which helps interact with the operating system
# We'll use it to make sure we correctly locate our sample PDF
import os
import fitz  # Import the PyMuPDF library (installed as PyMuPDF)
import spacy # Import spaCy
import re    # Import Regular Expressions module

# --- Configuration ---
# Define the name of the PDF file we want to process
# Make sure you have a 'sample.pdf' file in the same 'backend/logic/' directory
PDF_FILENAME = "sample.pdf"
# Define the output filename for the REDACTED PDF
REDACTED_PDF_FILENAME = "sample_redacted.pdf"
# Define the specific text we want to find and redact (case-sensitive)
TEXT_TO_REDACT = "Dummy" # Change this if your sample PDF has different sensitive text

# Define the types of entities spaCy identifies that we consider PII
# Common examples: PERSON (People's names), ORG (Organizations), GPE (Geo-political entities like cities, countries)
# LOC (Non-GPE locations), DATE (Dates) - Adjust this list based on your needs!
PII_ENTITY_TYPES = ["PERSON", "GPE", "LOC", "ORG", "DATE"]

# Regular Expression for Singapore NRIC/FIN
# Matches S, T, F, or G, followed by 7 digits, followed by an uppercase letter
NRIC_REGEX_PATTERN = r"[STFG]\d{7}[A-Z]"

# Load the spaCy English model (small version)
# This loads the trained AI model into memory. Do it once.
print("Loading spaCy model (en_core_web_sm)...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model loaded successfully.")
except OSError:
    print("spaCy model 'en_core_web_sm' not found.")
    print("Please run: python -m spacy download en_core_web_sm")
    # Exit or handle error appropriately in a real application
    exit() # Simple exit for this script

# Construct the full path to the PDF file
# os.path.dirname(__file__) gets the directory where this script (process_pdf.py) is located
# os.path.join combines the directory path and the filename safely
PDF_PATH = os.path.join(os.path.dirname(__file__), PDF_FILENAME)
# Construct the full path for the REDACTED PDF
REDACTED_PDF_PATH = os.path.join(os.path.dirname(__file__), REDACTED_PDF_FILENAME)


# --- Main Processing Function ---
def extract_text_from_pdf(pdf_file_path):
    """
    Opens a PDF file, extracts text from all pages.

    Args:
        pdf_file_path (str): The full path to the PDF file.

    Returns:
        str: The extracted text from all pages concatenated together,
             or None if the file is not found or an error occurs.
    """
    # Check if the file actually exists before trying to open it
    if not os.path.exists(pdf_file_path):
        print(f"Error: File not found at {pdf_file_path}")
        return None  # Indicate failure: file not found

    print(f"--- Reading text from: {pdf_file_path} ---")
    full_text = ""  # Initialize an empty string to hold all the text

    # Use 'with' to open the PDF file safely. pdfplumber.open() handles the opening.
    try:
        with pdfplumber.open(pdf_file_path) as pdf:
            # pdf.pages gives us a list of all pages in the PDF
            num_pages = len(pdf.pages)
            print(f"Number of pages found: {num_pages}")

            # Loop through each page in the PDF
            # enumerate gives us both the page number (index i) and the page object
            for i, page in enumerate(pdf.pages):
                page_number = i + 1  # Human-readable page number (starts from 1)
                # page.extract_text() is the core function from pdfplumber
                # It does its best to pull out the text content from the page
                # Adding x_tolerance can sometimes help with slightly misaligned text
                text = page.extract_text(x_tolerance=2)

                # Check if text was actually extracted (sometimes pages are just images)
                if text:
                    print(f"--- Extracted Text from Page {page_number} ---")
                    print(text)
                    # Add the extracted text to our full_text variable
                    full_text += text + "\n"  # Add a newline between pages
                else:
                    print(f"--- Page {page_number} has no extractable text (might be an image or empty) ---")

        print("\n--- Finished Reading PDF ---")
        return full_text  # Return the combined text

    # Add basic error handling in case pdfplumber fails to open or process the file
    except Exception as e:
        print(f"An error occurred while processing the PDF: {e}")
        return None  # Indicate failure: error during processing


# --- Function to Save Text to File (Optional but good practice) ---
def save_text_to_file(text_content, output_file_path):
    """
    Saves the given text content to a specified file path.

    Args:
        text_content (str): The text to save.
        output_file_path (str): The full path where the text file should be saved.
    """
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(text_content)
        print(f"--- Extracted text saved successfully to: {output_file_path} ---")
    except Exception as e:
        print(f"Error saving text to file {output_file_path}: {e}")


# --- PII Detection Function (using spaCy) ---
def find_pii_entities(text):
    """
    Processes text using spaCy to find potential PII entities.

    Args:
        text (str): The text content to analyze.

    Returns:
        list: A list of unique text strings identified as PII.
    """
    if not text:
        return []

    print("\n--- [PII Detect - spaCy] Analyzing text for standard PII ---")
    # Process the text with the loaded spaCy model
    doc = nlp(text)

    pii_list = []
    # Iterate through the entities found by spaCy
    # doc.ents contains the named entities (like PERSON, ORG, DATE)
    for entity in doc.ents:
        # Check if the entity's label (e.g., "PERSON") is in our list of PII types
        if entity.label_ in PII_ENTITY_TYPES:
            print(f"  Found spaCy PII: '{entity.text}' (Type: {entity.label_})")
            # Add the text of the entity to our list
            pii_list.append(entity.text)

    # Return a list of unique PII strings found
    # Using set() removes duplicates, then convert back to list
    unique_pii = list(set(pii_list))
    print(f"--- [PII Detect - spaCy] Found {len(unique_pii)} unique standard PII entities ---")
    return unique_pii


# --- NRIC Detection Function (using Regex) ---
def find_nric_matches(text):
    """
    Finds potential Singapore NRIC/FIN numbers in text using regex.

    Args:
        text (str): The text content to analyze.

    Returns:
        list: A list of unique strings matching the NRIC pattern.
    """
    if not text:
        return []
    print("\n--- [PII Detect - Regex] Searching for NRIC patterns ---")
    # re.findall finds all non-overlapping matches of the pattern in the string
    nric_matches = re.findall(NRIC_REGEX_PATTERN, text)

    if nric_matches:
        print(f"  Found Regex NRIC Matches: {nric_matches}")
    else:
        print("  No NRIC patterns found via regex.")

    # Return unique matches
    unique_nrics = list(set(nric_matches))
    print(f"--- [PII Detect - Regex] Found {len(unique_nrics)} unique potential NRICs ---")
    return unique_nrics


# --- Redaction Function (using PyMuPDF/fitz) ---
def redact_sensitive_text(input_pdf_path, output_pdf_path, text_list_to_redact):
    """
    Opens a PDF, searches for specified text strings, redacts them by
    applying a black bar, and saves the result to a new file.

    Args:
        input_pdf_path (str): Path to the original PDF file.
        output_pdf_path (str): Path where the redacted PDF should be saved.
        text_list_to_redact (list): A list of strings to search for and redact.
    """
    if not os.path.exists(input_pdf_path):
        print(f"Error [Redact]: Input file not found at {input_pdf_path}")
        return False # Indicate failure

    if not text_list_to_redact:
        print("--- [Redact] No text specified for redaction. Skipping redaction. ---")
        try:
            import shutil
            shutil.copyfile(input_pdf_path, output_pdf_path)
            print(f"Copied original file to {output_pdf_path} as no redactions were needed.")
            return True
        except Exception as e:
            print(f"Error copying original file: {e}")
            return False

    print(f"\n--- [Redact] Starting redaction process for: {input_pdf_path} ---")
    print(f"--- [Redact] Text items to find and cover with black bar: {len(text_list_to_redact)} ---")
    print(f"--- [Redact] Output will be saved to: {output_pdf_path} ---")

    try:
        # Open the PDF file using fitz
        doc = fitz.open(input_pdf_path)
        redactions_made = 0

        # Iterate through each page in the document
        for page_num, page in enumerate(doc):
            page_number_human = page_num + 1 # For printing (starts from 1)
            print(f"--- [Redact] Processing Page {page_number_human} ---")

            # Search for each piece of text we want to redact on the current page
            for text in text_list_to_redact:
                if not text: continue
                search_instances = page.search_for(str(text))

                if search_instances:
                    print(f"  Applying black bar over '{text}' ({len(search_instances)} instances) on page {page_number_human}")
                    redactions_made += len(search_instances)

                    # Add a redaction annotation for each instance found
                    # Explicitly set fill color to black (0,0,0)
                    for inst in search_instances:
                        page.add_redact_annot(inst, fill=(0, 0, 0)) # Explicitly black

            # IMPORTANT: Apply the redactions for the current page.
            page.apply_redactions()

        # Save the modified document to the output path
        if redactions_made > 0:
            doc.save(output_pdf_path, garbage=4, deflate=True)
            print(f"\n--- [Redact] Successfully saved redacted PDF to: {output_pdf_path} ---")
            print(f"--- [Redact] Total black bar redactions applied: {redactions_made} ---")
            success = True
        else:
            doc.save(output_pdf_path, garbage=4, deflate=True)
            print("\n--- [Redact] No matching text found in the document for listed items. Output file saved (unmodified). ---")
            success = True

        # Close the document
        doc.close()
        return success

    except Exception as e:
        print(f"An error occurred during redaction: {e}")
        if 'doc' in locals() and doc: doc.close()
        return False # Indicate failure


# --- Script Execution Block ---
# This standard Python construct checks if the script is being run directly
# (as opposed to being imported as a module by another script)
if __name__ == "__main__":
    print("\nStarting Full PDF Anonymization Script...")

    # --- Step 1: Extract Text (Optional but good for confirmation) ---
    # extracted_text = extract_text_from_pdf(PDF_PATH)
    # if extracted_text:
    #     print("\nText extraction completed (content not shown here).")
    # else:
    #     print("\nText extraction failed or file not found.")

    # --- Step 2: Find PII entities in the extracted text
    extracted_text = extract_text_from_pdf(PDF_PATH)
    all_pii_to_redact = [] # Initialize empty list for combined results
    if extracted_text:
        # Step 3: Find PII entities in the extracted text
        spacy_pii = find_pii_entities(extracted_text)

        # Step 4: Find NRIC patterns using Regex
        nric_pii = find_nric_matches(extracted_text)

        # Step 5: Combine the results from both methods
        # Use set to automatically handle duplicates between the lists
        combined_set = set(spacy_pii) | set(nric_pii) # '|' is the union operator for sets
        all_pii_to_redact = list(combined_set)
        print(f"\n--- [Combine PII] Total unique items to search for redaction: {len(all_pii_to_redact)} ---")
        # print(all_pii_to_redact) # Optional: print the full combined list
    else:
        print("\nText extraction failed. Cannot proceed with PII detection or redaction.")
        # all_pii_to_redact remains empty

    # --- Step 6: Redact the found PII entities in the original PDF
    # Only proceed if PII was found (or if you want to save a copy anyway)
    if all_pii_to_redact: # Check if the list is not empty
        redaction_successful = redact_sensitive_text(PDF_PATH, REDACTED_PDF_PATH, all_pii_to_redact)

        if redaction_successful:
            print("\n--- Summary: Anonymization process completed. ---")
            print(f"Check the potentially redacted file: {REDACTED_PDF_PATH}")
        else:
            print("\n--- Summary: Anonymization process encountered errors during redaction or file handling. ---")
    elif extracted_text: # If text was extracted but no PII found
         print("\n--- Summary: No PII detected according to rules. No redaction performed. ---")
         # Optionally copy the original file to the output path if you want an output regardless
         # import shutil
         # try:
         #     shutil.copyfile(PDF_PATH, REDACTED_PDF_PATH)
         #     print(f"Copied original file to {REDACTED_PDF_PATH} as no PII was found.")
         # except Exception as e:
         #     print(f"Error copying original file: {e}")
    # else case (extraction failed) is handled above

    print("\nFull PDF Anonymization script finished.")