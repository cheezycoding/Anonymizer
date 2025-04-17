# 1. Base Image: Start with an official Python image.
# We choose a specific version for consistency and slim-buster for smaller size.

FROM python:3.11-slim-buster

# 2. Set Working Directory: Define the working directory inside the container.
WORKDIR /app

# 3. Copy Requirements: Copy the requirements file first.
# This leverages Docker's layer caching. If requirements.txt doesn't change,
# Docker can reuse the layer where dependencies are installed, speeding up builds.
COPY requirements.txt .

# 4. Install Dependencies: Install Python packages specified in requirements.txt.
# --no-cache-dir reduces image size slightly.
RUN pip install --no-cache-dir -r requirements.txt

# 5. Download spaCy Model: Download the required language model.
RUN python -m spacy download en_core_web_sm

# 6. Copy Application Code: Copy the rest of the backend application code into the container.
# This includes main.py, the logic/ directory, __init__.py etc.
COPY . .

# 7. Expose Port: Inform Docker that the container will listen on port 8000 at runtime.
# This doesn't actually publish the port, just documents it.
EXPOSE 8000

# 8. Command: Specify the command to run when the container starts.
# We use uvicorn to run the FastAPI application.
# --host 0.0.0.0 makes it accessible from outside the container.
# --port 8000 matches the exposed port.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 