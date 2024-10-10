# Use the official Python image as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Set production environment variables
ENV DEBUG=False
ENV ALLOWED_HOSTS=["*"]

# Set the working directory to 'src'
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Make migrations and migrate the database
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

# Create superuser (non-interactive)
RUN python3 manage.py createsuperuser --noinput \
    --email $DJANGO_SUPERUSER_EMAIL \
    --first_name $DJANGO_SUPERUSER_FIRST_NAME \
    --last_name $DJANGO_SUPERUSER_LAST_NAME || true


# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
