# Builder stage
FROM python:3.9-slim as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=fitness_project.settings

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Modified collectstatic command
RUN python -c "from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "fitness_project.wsgi:application"]