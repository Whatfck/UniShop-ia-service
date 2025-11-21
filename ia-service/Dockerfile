# Multi-stage build for lighter image
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements_light.txt .
RUN pip install --no-cache-dir --user -r requirements_light.txt

# Runtime stage
FROM python:3.11-alpine

# Install runtime dependencies (curl for health check)
RUN apk add --no-cache curl

# Create non-root user
RUN adduser -D app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/app/.local
ENV PATH=/home/app/.local/bin:$PATH

# Copy source code to root level
COPY src/ ./

# Change ownership
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]