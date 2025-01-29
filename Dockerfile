# Use the official Python 3.10 image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the backend files into the container
COPY . .

# Expose the port (change if necessary)
EXPOSE 8000

# Start the Flask API using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "api_app:app"]
