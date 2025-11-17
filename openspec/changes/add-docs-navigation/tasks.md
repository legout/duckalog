## Tasks

1. **Update mkdocs.yml navigation configuration**
   - Add "DuckDB Secrets" entry pointing to `examples/duckdb-secrets.md`
   - Add "DuckDB Settings" entry pointing to `examples/duckdb-settings.md`
   - Insert entries in alphabetical order under Examples section
   - Verify YAML syntax and formatting

2. **Validate navigation configuration**
   - Run `mkdocs build` to check for warnings
   - Verify no pages are reported as missing from navigation
   - Test navigation structure and ordering

3. **Verify documentation accessibility**
   - Check that added pages are accessible via navigation
   - Confirm examples follow consistent formatting with other documentation
   - Ensure links work correctly

4. **Test documentation site**
   - Run `mkdocs serve` to test locally
   - Verify navigation menu displays all examples correctly
   - Confirm no broken links or missing pages