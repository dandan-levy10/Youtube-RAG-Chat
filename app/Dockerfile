# User an official Python runtime as a parent image
FROM python:3.12-slim

# Set a neutral working directory, so that 'app' is not the root directory
WORKDIR /code

# [Optimisation] Install uv itself first.
# This step will be cached and run only once
RUN pip install uv

# Copy the requirements file into the container at /app
COPY app/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN uv pip install --no-cache --system -r requirements.txt

# Copy the rest of the application's code from the host to the image filesystem
COPY ./app /code/app
COPY ./db /code/db

# Tell python to add the '/app' directory to its path.
# This ensures that imports like 'from app.database import ...' will work correctly.
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# The host 0.0.0.0 allows the container to be accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]