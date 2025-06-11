# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /frontend

# [Optimisation] Install uv itself first.
# This step will be cached and run only once
RUN pip install uv

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN uv pip install --no-cache --system -r requirements.txt

# Copy the rest of your application's code
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the streamlit app
CMD ["streamlit", "run", "frontend.py"]