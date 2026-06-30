FROM python:3.12-slim AS builder
WORKDIR /build
COPY pyproject.toml .
COPY quantforge/ quantforge/
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY quantforge/ quantforge/
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "quantforge.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
