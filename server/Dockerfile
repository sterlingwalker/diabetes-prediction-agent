# Use an official Python runtime as a parent image
# python:3.9-slim is a good balance. You can use python:3.9.9-slim if you need that specific patch.
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the server directory into the container at /app
COPY ./server/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
# Ensure system libraries for packages like faiss-cpu or lightgbm are available if needed.
# The python:slim images are Debian-based. For faiss-cpu and lightgbm,
# standard pip install should typically suffice as they often bundle or link to precompiled libs.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of the 'server' directory into the container at /app
# This will include main.py, model files, and FAISS index folders.
COPY ./server/ /app/

# Make port 8080 available to the world outside this container
# Cloud Run will map its external port to this port on the container.
EXPOSE 8080

# Define environment variable for the Uvicorn server.
# Cloud Run will set the PORT environment variable, which your main.py already uses.
# This ENV instruction in the Dockerfile is more for documentation or local runs if not overridden.
ENV PORT 8080

# Run main.py when the container launches
# Your main.py already handles os.environ.get("PORT", 8080)
# CMD ["python", "main.py"] # This would work if main.py's __main__ block directly ran uvicorn
# More robust and common for FastAPI is to directly call uvicorn:
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300"]
