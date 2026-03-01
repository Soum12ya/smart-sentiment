# --------- Builder Stage ---------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# --------- Production Stage ---------
FROM python:3.11-slim

WORKDIR /app

# Copy installed site-packages from builder
COPY --from=builder /usr/local /usr/local

# Copy app code
COPY . .

RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]