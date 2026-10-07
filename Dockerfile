FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd --system appuser \
    && useradd --system --gid appuser --home-dir /nonexistent \
       --shell /usr/sbin/nologin appuser

COPY requirements.txt ./
RUN python -m pip install \
    --no-cache-dir \
    --disable-pip-version-check \
    -r requirements.txt

COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser static ./static
COPY --chown=appuser:appuser templates ./templates

USER appuser

EXPOSE 5000

# The healthcheck only verifies that Flask/Gunicorn can serve the home page.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=3)"

# gthread workers + long timeout so SSE streaming is not killed.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "8", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
