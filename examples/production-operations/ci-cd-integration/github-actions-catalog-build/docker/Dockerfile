# Duckalog CI/CD Build Environment
# Multi-stage build for efficient containerized builds

# Base stage with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    jq \
    unzip \
    # DuckDB dependencies
    libgcc-s1 \
    libstdc++6 \
    libblas3 \
    liblapack3 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Dependencies stage
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r requirements-dev.txt

# Build stage
FROM dependencies as build

ARG CONFIG_HASH
ARG ENVIRONMENT
ARG FORCE_REBUILD=false

# Copy application code
COPY . .

# Set build metadata
ENV BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    BUILD_VERSION="$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    CONFIG_HASH="${CONFIG_HASH}" \
    ENVIRONMENT="${ENVIRONMENT}" \
    FORCE_REBUILD="${FORCE_REBUILD}"

# Validate build metadata
RUN echo "Build metadata:" && \
    echo "  Date: ${BUILD_DATE}" && \
    echo "  Version: ${BUILD_VERSION}" && \
    echo "  Config Hash: ${CONFIG_HASH}" && \
    echo "  Environment: ${ENVIRONMENT}" && \
    echo "  Force Rebuild: ${FORCE_REBUILD}"

# Run validation
RUN python scripts/validate-configs.py --environment ${ENVIRONMENT} --strict

# Runtime stage
FROM base as runtime

# Install only runtime dependencies
RUN pip install --upgrade pip && \
    pip install duckalog pyyaml polars pyarrow

# Create non-root user
RUN groupadd -r duckalog && useradd -r -g duckalog duckalog

# Set working directory
WORKDIR /app

# Copy built application from build stage
COPY --from=build --chown=duckalog:duckalog /app ./

# Create necessary directories
RUN mkdir -p deployments/backups data logs && \
    chown -R duckalog:duckalog deployments data logs

# Switch to non-root user
USER duckalog

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import duckdb; conn = duckdb.connect(':memory:'); conn.execute('SELECT 1').fetchone() or exit(1)" || exit 1

# Default command
CMD ["python", "-m", "duckalog", "--config", "configs/catalog-${ENVIRONMENT:-dev}.yaml"]

# Labels for metadata
LABEL maintainer="Duckalog Team" \
    version="${BUILD_VERSION}" \
    description="Duckalog catalog build environment" \
    org.opencontainers.image.title="Duckalog Build" \
    org.opencontainers.image.description="Duckalog catalog build environment" \
    org.opencontainers.image.version="${BUILD_VERSION}" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.source="https://github.com/your-org/duckalog" \
    org.opencontainers.image.revision="${BUILD_VERSION}"
