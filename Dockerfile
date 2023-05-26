# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Expose port 8000 for the API
EXPOSE 8000

# Run the API with uvicorn when the container launches
CMD ["uvicorn", "hook:app", "--host", "0.0.0.0", "--port", "8000"]