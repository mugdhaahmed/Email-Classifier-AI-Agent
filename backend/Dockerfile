# Use a stable, lightweight Python environment
FROM python:3.11-slim

# Set system environment variables to optimize Python inside containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system level dependencies required for compiling certain Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY . /app/

# Expose Django/Daphne's default runtime port
EXPOSE 8000

# Run database migrations and launch the Daphne ASGI server interface on container boot
CMD ["sh", "-c", "python manage.py migrate && daphne -b 0.0.0.0 -p 8000 core.asgi:application"]