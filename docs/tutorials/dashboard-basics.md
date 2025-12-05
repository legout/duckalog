# Dashboard Basics Tutorial

Master the Duckalog web dashboard for interactive data exploration and catalog management. This hands-on tutorial teaches you to effectively use the web interface for all your data workflows.

## Learning Objectives

After completing this tutorial, you will be able to:

- **Launch and configure** the Duckalog web dashboard
- **Navigate the interface** - Home, Views, Query, and Semantic Layer sections
- **Inspect and manage** catalog views and semantic models
- **Execute ad-hoc queries** with proper security controls
- **Export data** in multiple formats (CSV, Excel, Parquet)
- **Update configurations** through the web interface
- **Apply security best practices** for dashboard deployment

## Prerequisites

- **Completed Getting Started tutorial** OR basic Duckalog configuration knowledge
- **Duckalog[ui] package** installed:
  ```bash
  pip install duckalog[ui]
  ```
- **Working Duckalog catalog** (we'll use the getting-started example)
- **Web browser** and basic web concepts
- **No web development experience** required

## Step 1: Setting Up the Dashboard

### 1.1 Prepare Your Catalog

If you completed the Getting Started tutorial, you should have a working catalog. If not, let's create a simple one:

```yaml
# dashboard-tutorial-catalog.yaml
catalog:
  database: "tutorial.duckdb"
  
views:
  - name: sample_users
    sql: |
      SELECT 
        'Alice' as name,
        25 as age,
        'Engineering' as department
      UNION ALL
      SELECT 
        'Bob' as name,
        30 as age,
        'Marketing' as department
```

### 1.2 Launch the Dashboard

You can launch the dashboard in two ways:

**Method 1: Python API (Recommended for Development)**
```python
from duckalog.dashboard import run_dashboard

run_dashboard(
    "dashboard-tutorial-catalog.yaml", 
    host="127.0.0.1", 
    port=8787, 
    row_limit=500
)
```

**Method 2: CLI Command**
```bash
duckalog ui dashboard-tutorial-catalog.yaml --host 127.0.0.1 --port 8787 --row-limit 500
```

### 1.3 Access the Dashboard

Open your web browser and navigate to: `http://127.0.0.1:8787`

You should see the Duckalog dashboard home page with your catalog information.

**✓ Success Check:** The dashboard loads and shows your catalog details (database path, view count, and build status).

---

## Step 2: Understanding the Dashboard Interface

### 2.1 Home Page Overview

The home page provides a snapshot of your catalog:

- **Configuration Path**: Shows your catalog file location
- **Database Location**: DuckDB database file path
- **Catalog Statistics**: Number of views, attachments, and semantic models
- **Build Status**: Last build timestamp and success/failure status
- **Rebuild Button**: Trigger catalog rebuild without restarting

**Try it:** Click the "Rebuild Catalog" button and watch the status update.

### 2.2 Navigation Menu

The dashboard has four main sections:

1. **Views** - Browse and inspect catalog views
2. **Query** - Run ad-hoc SQL queries
3. **Semantic Layer** - Explore business-friendly models
4. **Home** - Catalog overview and management

**Try it:** Click through each navigation item to familiarize yourself with the layout.

---

## Step 3: Working with Views

### 3.1 Browse Views

Navigate to the **Views** section. You should see:

- **View List**: All views from your catalog
- **Search Bar**: Filter views by name
- **View Details**: Source type and location information

**Try it:** Search for views and observe how the list filters dynamically.

### 3.2 Inspect View Details

Click on the `sample_users` view to see:

- **SQL Definition**: The exact SQL used to create the view
- **Source Information**: Where the view comes from (SQL in this case)
- **Semantic Layer**: Any associated dimensions/measures (if applicable)

**Understanding:** The interface shows you exactly how each view is constructed, which is valuable for debugging and understanding your data transformations.

---

## Step 4: Query Execution and Data Export

### 4.1 Running Queries

Navigate to the **Query** section. This is your interactive SQL playground.

**Basic Query:**
```sql
SELECT * FROM sample_users WHERE age > 25
```

**Try it:** Enter this query and click "Execute". You should see Bob's record returned.

### 4.2 Query Security Features

The dashboard enforces important security controls:

- **Read-Only**: Only SELECT queries are allowed (no INSERT, UPDATE, DELETE)
- **Row Limits**: Queries automatically limited to prevent resource exhaustion
- **Error Handling**: Clear error messages for SQL syntax issues

**Test Security:** Try this query to see security in action:
```sql
DROP TABLE sample_users  -- This will be blocked
```

### 4.3 Data Export

After running a successful query, you'll see export options:

1. **CSV**: Comma-separated values for spreadsheet applications
2. **Excel**: Native Excel format with formatting
3. **Parquet**: Columnar format for analytics workflows

**Try it:** Run the query `SELECT * FROM sample_users` and export results as CSV.

---

## Step 5: Semantic Layer Exploration

### 5.1 Understanding Semantic Models

The semantic layer adds business context to your data. For this tutorial, let's add semantic models to our catalog:

```yaml
# Adding to dashboard-tutorial-catalog.yaml
semantic_layer:
  models:
    - name: user_demographics
      description: "User demographic information"
      dimensions:
        - name: name
          description: "User full name"
          sql: "name"
        - name: department
          description: "Department name"
          sql: "department"
      measures:
        - name: average_age
          description: "Average age by department"
          sql: "AVG(age)"
          aggregation: "avg"
```

### 5.2 Exploring Semantic Models

After adding the semantic layer and rebuilding:

1. Navigate to **Semantic Layer** section
2. Browse the `user_demographics` model
3. Review dimensions (descriptive attributes) and measures (calculations)

**The Value:** Semantic models make your data accessible to business users without requiring SQL knowledge.

---

## Step 6: Configuration Management

### 6.1 In-Memory Updates

The dashboard allows safe configuration updates:

1. Navigate to views that reference file sources
2. Modify connection parameters through the interface
3. Changes apply immediately without file corruption

### 6.2 Format Preservation

The dashboard maintains your original formatting:
- **YAML formatting** preserved exactly
- **Comments and structure** maintained
- **Atomic writes** prevent corruption

**⚠️ Important:** Configuration updates through the dashboard write directly to your catalog file. Always have backups.

---

## Step 7: Security and Production Deployment

### 7.1 Development vs Production

**Development Settings (Default):**
```bash
duckalog ui catalog.yaml --host 127.0.0.1 --port 8787
```

**Production Settings:**
```bash
# Set admin token for protecting mutating operations
export DUCKALOG_ADMIN_TOKEN="your-secure-random-token"

duckalog ui catalog.yaml --host 0.0.0.0 --port 8000
```

### 7.2 Security Best Practices

1. **Use Admin Tokens** in production for configuration changes
2. **Localhost Binding** by default prevents external access
3. **No External Dependencies** - everything served locally
4. **Row Limit Enforcement** prevents resource exhaustion

**Never:** Expose dashboards without authentication in production environments.

---

## Step 8: Advanced Dashboard Features

### 8.1 Schema Inspection

Use the Query section to inspect table schemas:

```sql
-- View all tables and their columns
PRAGMA table_info('sample_users');
```

### 8.2 Performance Monitoring

Monitor your catalog through:
- **Home page build status** - Track successful/failed builds
- **Query execution time** - Monitor query performance
- **Database size** - Track catalog growth

### 8.3 Troubleshooting Common Issues

**Common Problems and Solutions:**

1. **Dashboard won't start**
   - Check if port is in use: `lsof -i :8787`
   - Install UI bundle: `pip install duckalog[ui]`

2. **Queries fail with security errors**
   - Ensure using SELECT statements only
   - Check row limit settings

3. **Changes not appearing**
   - Click "Rebuild Catalog" on home page
   - Verify catalog file syntax

---

## Check Your Understanding

Test your knowledge with these exercises:

### Exercise 1: Data Exploration
1. Create a new view with multiple departments
2. Run queries to analyze the data
3. Export results in different formats

### Exercise 2: Semantic Layer
1. Add a semantic model to your catalog
2. Create dimensions and measures
3. Explore the semantic layer interface

### Exercise 3: Configuration Updates
1. Add a new view through the dashboard interface
2. Verify changes are saved correctly
3. Test the format preservation feature

### Exercise 4: Security Testing
1. Test the read-only SQL enforcement
2. Verify row limits work correctly
3. Check CORS behavior with different origins

---

## Next Steps

After completing this tutorial, you should be comfortable with:

- **Dashboard workflow** from launch to advanced features
- **Interactive data exploration** and analysis
- **Secure deployment practices** for production use

### Continue Your Learning

1. **How-to Guides**:
   - [Environment Management](../how-to/environment-management.md) - Production deployment patterns
   - [Performance Tuning](../how-to/performance-tuning.md) - Optimize dashboard performance

2. **Reference Documentation**:
   - [CLI Reference](../reference/cli.md) - All dashboard command options
   - [API Reference](../reference/api.md) - Programmatic dashboard control

3. **Examples**:
   - [Multi-Source Analytics](../../examples/multi-source-analytics.md) - Advanced dashboard scenarios
   - [Security Examples](../../examples/duckdb-secrets.md) - Secure configuration patterns

---

## Getting Help

If you encounter issues with the dashboard:

1. **Check the troubleshooting section** above
2. **Verify your catalog configuration** with `duckalog validate`
3. **Check browser console** for JavaScript errors
4. **Review dashboard logs** for startup issues
5. **Ask for help** in GitHub discussions with specific details

### When Reporting Issues:

- **Dashboard version** and installation method
- **Catalog configuration** (sanitized)
- **Browser and OS** information
- **Error messages** and screenshots
- **Steps to reproduce** the issue

---

## Summary

You've successfully mastered the Duckalog web dashboard! You can now:

✅ **Launch and configure** dashboards for development and production
✅ **Navigate all interface sections** confidently
✅ **Execute queries safely** with proper security controls
✅ **Export data** in multiple formats for different workflows
✅ **Leverage the semantic layer** for business-friendly data access
✅ **Apply security best practices** for safe deployment

The dashboard is now a powerful tool in your data analytics workflow, enabling rapid exploration and management of your Duckalog catalogs.

Ready for the next challenge? Explore our [how-to guides](../how-to/index.md) for specific problem-solving techniques!