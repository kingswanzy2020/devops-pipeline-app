# Stage 1: Install Python dependencies
FROM python:3.11-slim AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Lightweight runtime image
FROM python:3.11-slim
WORKDIR /app
RUN useradd --system --no-create-home appuser
COPY --from=builder /install /usr/local
COPY app/ .
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]