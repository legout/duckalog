#!/bin/bash
# Development environment setup script for Environment Variables Security Example

set -e  # Exit on any error

echo "🚀 Setting up development environment..."
echo "=" * 50

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created from template"
else
    echo "📁 .env file already exists"
fi

# Load environment variables
echo "📦 Loading environment variables..."
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded from .env"
else
    echo "⚠️  No .env file found, using existing environment variables"
fi

# Verify required environment variables
echo "🔍 Verifying environment variables..."

required_vars=("ENVIRONMENT" "CATALOG_NAME" "DATA_BUCKET_PREFIX")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ Missing required environment variables: ${missing_vars[*]}"
    echo ""
    echo "💡 Set them manually:"
    for var in "${missing_vars[@]}"; do
        echo "   export $var='your-value'"
    done
    echo ""
    echo "📝 Or edit the .env file:"
    echo "   nano .env"
    exit 1
fi

echo "✅ Required environment variables are set"

# Generate test data
echo "📊 Generating test data..."
python generate-test-data.py

# Validate development configuration
echo "🔧 Validating development configuration..."
python validate-configs.py dev

# Build development catalog
echo "🏗️  Building development catalog..."
duckalog run catalog-dev.yaml

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Connect to the catalog: duckdb ${CATALOG_NAME:-dev_security_catalog}.duckdb"
echo "2. Explore the views: .tables"
echo "3. Run queries: SELECT * FROM dev_analytics_summary LIMIT 10;"
echo "4. Test production setup when ready: python validate-configs.py prod"
echo ""
echo "📚 Reference:"
echo "  - Configuration: catalog-dev.yaml"
echo "  - Environment file: .env"
echo "  - Validation script: python validate-configs.py"
echo "  - Documentation: README.md"