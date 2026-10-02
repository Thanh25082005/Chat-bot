FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static ./static
COPY templates ./templates

RUN useradd -m appuser
USER appuser

EXPOSE 5000

# gthread workers + long timeout so SSE streaming isn't killed
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "--threads", "8", "--timeout", "120", "app:app"]
