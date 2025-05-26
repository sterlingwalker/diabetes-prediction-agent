# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the server directory into the container at /app
COPY ./server/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of the 'server' directory into the container at /app
# This will include main.py, model files, and FAISS index folders from your server folder.
COPY ./server/ /app/

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Environment variable for Uvicorn (Cloud Run will set PORT, which your main.py uses)
ENV PORT 8080

# Run main.py (which is now at /app/main.py) when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300"]
