# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# Remove rumps from requirements for Linux/Docker environment as it's macOS specific
RUN grep -v "rumps" requirements.txt > requirements_docker.txt && \
    pip install --no-cache-dir -r requirements_docker.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Define environment variable
ENV FLASK_APP=src/web_server.py
ENV PYTHONUNBUFFERED=1

# Run web_server.py when the container launches
CMD ["python", "src/web_server.py"]
