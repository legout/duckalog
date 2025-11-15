## 1. SQL generation utilities and functions

- [x] 1.1 Implement `quote_ident` and `render_options` utilities consistent with the `sql-generation` spec.
- [x] 1.2 Implement `generate_view_sql(view: ViewConfig) -> str` supporting all configured `source` variants and raw SQL views.
- [x] 1.3 Implement `generate_all_views_sql(config: Config) -> str` that prepends header comments and concatenates per-view SQL.
- [x] 1.4 Add SQL snapshot tests for representative views (parquet, delta, iceberg by `uri` and `catalog`+`table`, attached DBs, and raw SQL).
