# Django Project Setup

This project is a Django application configured with Docker. This README provides instructions on how to set up the environment and run the application.

## Environment Variables

The following environment variables are configured for the Django application. Make sure to set these variables in your environment or in your Docker setup.

### General Environment Variables

- `PYTHONDONTWRITEBYTECODE=1`: Prevents Python from writing `.pyc` files, which can help with performance and file clutter.
- `PYTHONUNBUFFERED=1`: Ensures that Python output is sent straight to the terminal without buffering, which can be useful for debugging.

### Production Environment Variables

- `DEBUG=False`: Disables debug mode in the production environment.
- `ALLOWED_HOSTS="*"`: Allows all hosts to connect to the Django application. This should be set to specific domains in a production environment for security.

### Superuser Credentials

These credentials are used to create a superuser in the Django application. 

- `DJANGO_SUPERUSER_USERNAME=admin`
- `DJANGO_SUPERUSER_EMAIL=admin@example.com`
- `DJANGO_SUPERUSER_PASSWORD=adminpass`

