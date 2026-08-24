FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends binutils libgdal-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.in .
RUN pip install --no-cache-dir -r requirements.in
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

