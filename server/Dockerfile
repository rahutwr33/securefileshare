# Step 1: Use official python image as the base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy requirements.txt and install dependencies
COPY ./server/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the backend application code to the container
COPY ./server /app

# Step 5: Copy the SSL certificates to the container (use a better location)
COPY ./server/cert.pem /etc/ssl/certs/cert.pem
COPY ./server/key.pem /etc/ssl/private/key.pem

# Step 6: Expose port 8000 for FastAPI
EXPOSE 8000

# Step 7: Start the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/etc/ssl/private/key.pem", "--ssl-certfile", "/etc/ssl/certs/cert.pem"]
