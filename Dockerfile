# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file into the container first
COPY ./requirements.txt /code/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy your application code and models into the container
# This includes server.py, stt.py, llm.py, and the 'models' directory
COPY . /code

# Expose port 8000 to allow traffic to the server
EXPOSE 8000

# The command to run your FastAPI server when the container starts
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]