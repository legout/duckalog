# Spec: Docker Setup for External Services

## Summary
Define docker-compose configurations and Makefile standards for examples requiring external services (PostgreSQL, S3/MinIO).

## ADDED Requirements

### Requirement: PostgreSQL Example
A PostgreSQL integration example **SHALL** exist at `04-external-services/postgres/`.

#### Scenario: Docker Compose**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: duckalog
      POSTGRES_PASSWORD: duckalog
      POSTGRES_DB: demo
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U duckalog"]
      interval: 5s
      timeout: 5s
      retries: 5
volumes:
  postgres_data:
```

#### Scenario: Init Script**
An `init.sql` file seeds sample data:
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO customers (name, email) VALUES
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com');
```

#### Scenario: Catalog Configuration**
```yaml
attachments:
  postgres:
    - alias: production
      host: localhost
      port: 5432
      database: demo
      user: duckalog
      password: duckalog
```

---

### Requirement: S3/MinIO Example
An S3-compatible storage example **SHALL** exist at `04-external-services/s3-minio/`.

#### Scenario: Docker Compose with MinIO**
```yaml
services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  createbucket:
    image: minio/mc
    depends_on:
      - minio
    entrypoint: >
      /bin/sh -c "
      /usr/bin/mc alias set local http://minio:9000 minioadmin minioadmin &&
      /usr/bin/mc mb local/sample-bucket &&
      /usr/bin/mc policy set public local/sample-bucket &&
      exit 0
      "

volumes:
  minio_data:
```

#### Scenario: Catalog Configuration**
```yaml
views:
  - name: s3_data
    source: parquet
    uri: "s3://sample-bucket/data/*.parquet"
    properties:
      AWS_ENDPOINT: "http://localhost:9000"
      AWS_ACCESS_KEY_ID: "minioadmin"
      AWS_SECRET_ACCESS_KEY: "minioadmin"
      AWS_REGION: "us-east-1"
```

#### Scenario: Upload Script**
```python
import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# Upload sample data
s3.upload_file('data/sample.parquet', 'sample-bucket', 'data/sample.parquet')
```

---

### Requirement: Multi-Source Example
A combined example **SHALL** exist at `04-external-services/multi-source-full/`.

#### Scenario: Docker Compose**
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: duckalog
      POSTGRES_PASSWORD: duckalog
      POSTGRES_DB: demo
    ports:
      - "5432:5432"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"

  duckalog:
    image: duckalog:latest
    depends_on:
      - postgres
      - minio
    volumes:
      - .:/workspace
    working_dir: /workspace
    command: build catalog.yaml
```

---

### Requirement: Makefile Standard
All docker-based examples **SHALL** include a Makefile with standard targets.

#### Scenario: Makefile Targets**
```makefile
.PHONY: up down build setup clean test

up:
    docker-compose up -d
    @echo "Services started. Waiting for readiness..."
    @sleep 5

build:
    duckalog build catalog.yaml

setup:
    python setup.py

test:
    duckalog validate catalog.yaml
    python validate.py

clean:
    docker-compose down -v
    rm -rf data/*.parquet data/*.duckdb data/*.csv

down:
    docker-compose down
```

---

### Requirement: README Documentation
Each docker example **SHALL** document the Makefile workflow.

#### Scenario: README Sections**
- What it demonstrates
- Prerequisites (Docker, docker-compose)
- Quick start using Makefile
- Service URLs (PostgreSQL: localhost:5432, MinIO Console: localhost:9001)
- Troubleshooting section

#### Scenario: Quick Start Example**
```bash
cd 04-external-services/postgres
make up          # Start PostgreSQL
make setup       # Seed database
make build       # Build catalog
make test        # Validate
make clean       # Cleanup
```

---

### Requirement: Health Checks
Docker services **SHALL** include health checks.

#### Scenario: PostgreSQL Health**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U duckalog"]
  interval: 5s
  timeout: 5s
  retries: 5
```

#### Scenario: Wait for Ready**
Makefile should wait for services to be healthy:
```makefile
wait-postgres:
    @echo "Waiting for PostgreSQL..."
    @until docker-compose exec -T postgres pg_isready -U duckalog; do sleep 1; done
    @echo "PostgreSQL is ready"
```

---

## MODIFIED Requirements

### Requirement: Catalog Configuration
Existing catalog configurations **SHALL** be updated for updates for docker environments.

#### Scenario: Environment Variables**
```yaml
attachments:
  postgres:
    - alias: production
      host: "${env:POSTGRES_HOST}"
      port: "${env:POSTGRES_PORT}"
      database: "${env:POSTGRES_DB}"
      user: "${env:POSTGRES_USER}"
      password: "${env:POSTGRES_PASSWORD}"
```

---

## Validation

**Check: PostgreSQL Example**
```bash
cd 04-external-services/postgres
make up
make setup
make build
duckalog query "SELECT COUNT(*) FROM pg_customers"
# Expected: Count of seeded customers
make clean
```

**Check: MinIO Example**
```bash
cd 04-external-services/s3-minio
make up
make setup
make build
# Access MinIO console at http://localhost:9001
make clean
```

**Check: Multi-Source Example**
```bash
cd 04-external-services/multi-source-full
make up
make setup
make build
# Should successfully query across PostgreSQL and S3
make clean
```
