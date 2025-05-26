# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies
# libgomp1 is required for LightGBM (provides libgomp.so.1)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/* # Clean up apt cache

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the server directory into the container at /app
COPY ./server/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire contents of the 'server' directory into the container at /app
COPY ./server/ /app/

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Environment variable for Uvicorn (Cloud Run will set PORT, which your main.py uses)
ENV PORT 8080

# Run main.py (which is now at /app/main.py) when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-keep-alive", "300"]
