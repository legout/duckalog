import json
from pathlib import Path

from litestar.testing import TestClient

from duckalog.dashboard.app import create_app
from duckalog.dashboard.state import DashboardContext


def _write_config(tmp_path: Path) -> Path:
    db_path = tmp_path / "catalog.duckdb"
    config_path = tmp_path / "catalog.yaml"
    config_path.write_text(
        """
version: 1
duckdb:
  database: "{db}"
views:
  - name: foo
    sql: "select 1 as x"
""".format(
            db=db_path
        )
    )
    return config_path


def test_dashboard_routes_work(tmp_path: Path):
    config_path = _write_config(tmp_path)
    ctx = DashboardContext.from_path(str(config_path))
    app = create_app(ctx)
    client = TestClient(app)

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Duckalog Dashboard" in resp.text

    resp = client.get("/views")
    assert resp.status_code == 200
    assert "foo" in resp.text

    resp = client.get("/views/foo")
    assert resp.status_code == 200
    assert "foo" in resp.text

    resp = client.post("/query", data={"sql": "select 1 as x"})
    assert resp.status_code in [200, 201]  # Accept both 200 and 201
    assert "1" in resp.text

    resp = client.post("/build", follow_redirects=False)
    assert resp.status_code == 303
    # After build, home should still respond
    resp = client.get("/")
    assert resp.status_code == 200


def test_dashboard_sse_endpoints(tmp_path: Path):
    """Test the new Server-Sent Events endpoints."""
    config_path = _write_config(tmp_path)
    ctx = DashboardContext.from_path(str(config_path))
    app = create_app(ctx)
    client = TestClient(app)

    # Test query streaming endpoint
    resp = client.post("/query/stream", data={"sql": "select 1 as test_col"})
    assert resp.status_code in [200, 201]  # Accept both success codes
    assert "text/event-stream" in resp.headers["content-type"]

    # Check that SSE events are returned
    content = resp.content.decode()
    assert "event: datastar-patch-signals" in content
    assert '"query_running": true' in content
    assert '"query_complete": true' in content

    # Test build streaming endpoint
    resp = client.post("/build/stream")
    assert resp.status_code in [200, 201]  # Accept both success codes
    assert "text/event-stream" in resp.headers["content-type"]

    # Check that build SSE events are returned
    content = resp.content.decode()
    assert "event: datastar-patch-signals" in content
    assert '"build_running": true' in content
    assert '"build_complete": true' in content


def test_dashboard_query_error_handling(tmp_path: Path):
    """Test error handling in query streaming."""
    config_path = _write_config(tmp_path)
    ctx = DashboardContext.from_path(str(config_path))
    app = create_app(ctx)
    client = TestClient(app)

    # Test SQL syntax error
    resp = client.post("/query/stream", data={"sql": "select invalid syntax"})
    assert resp.status_code in [200, 201]  # Accept both success codes

    content = resp.content.decode()
    assert "event: datastar-patch-signals" in content
    assert '"query_error"' in content
    assert '"query_running": false' in content


def test_dashboard_read_only_enforcement(tmp_path: Path):
    """Test read-only query enforcement."""
    config_path = _write_config(tmp_path)
    ctx = DashboardContext.from_path(str(config_path))
    app = create_app(ctx)
    client = TestClient(app)

    # Test dangerous SQL is blocked
    dangerous_queries = [
        "DROP TABLE test",
        "DELETE FROM test",
        "UPDATE test SET x = 1",
        "INSERT INTO test VALUES (1)",
        "CREATE TABLE test (x INT)",
        "ALTER TABLE test ADD COLUMN y INT"
    ]

    for dangerous_sql in dangerous_queries:
        resp = client.post("/query", data={"sql": dangerous_sql})
        assert resp.status_code in [200, 201]

        # Check that error message is returned
        assert "Dashboard only allows SELECT queries" in resp.text or "cannot contain" in resp.text

    # Test valid SELECT queries work
    valid_queries = [
        "SELECT 1 as test",
        "SELECT * FROM (SELECT 1 as x) as subquery",
        "WITH test AS (SELECT 1 as x) SELECT * FROM test"
    ]

    for valid_sql in valid_queries:
        resp = client.post("/query", data={"sql": valid_sql})
        assert resp.status_code in [200, 201]
        assert "1" in resp.text or "test" in resp.text


def test_dashboard_cli_integration(tmp_path: Path):
    """Test CLI integration."""
    config_path = _write_config(tmp_path)

    # Test that CLI can create dashboard context
    ctx = DashboardContext.from_path(str(config_path))
    assert ctx.config_path == str(config_path)
    assert len(ctx.config.views) == 1
    assert ctx.config.views[0].name == "foo"

    # Test that app can be created from context (CLI integration test)
    app = create_app(ctx)
    assert app is not None

    # Test basic routes work
    from litestar.testing import TestClient
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
