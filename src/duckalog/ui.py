"""Dashboard UI server for Duckalog."""

from __future__ import annotations

import uvicorn
from starlette.applications import Starlette

from .dashboard.app import create_app
from .dashboard.state import DashboardContext


class UIServer:
    """Main UI server class for the Duckalog dashboard."""

    def __init__(
        self,
        config_path: str,
        host: str = "127.0.0.1",
        port: int = 8000,
        row_limit: int = 1000,
    ):
        """Initialize the UI server.

        Args:
            config_path: Path to the catalog configuration file
            host: Host to bind the server to
            port: Port to bind the server to
            row_limit: Maximum number of rows to return in queries
        """
        self.config_path = config_path
        self.host = host
        self.port = port
        self.row_limit = row_limit

        # Initialize dashboard context
        self._context = DashboardContext.from_path(config_path, row_limit=row_limit)

        # Create Starlette application
        self._app = create_app(self._context, host=self.host)

    @property
    def app(self) -> Starlette:
        """Get the Starlette application instance."""
        return self._app

    def run(self) -> None:
        """Run the UI server using uvicorn."""
        print(f"Starting Duckalog dashboard on http://{self.host}:{self.port}")
        print(f"Config file: {self.config_path}")

        # Add security warning if binding to non-loopback
        if self.host not in ("127.0.0.1", "localhost", "::1"):
            print("WARNING: Binding to non-loopback address. Ensure proper firewall rules.")

        uvicorn.run(self._app, host=self.host, port=self.port, log_level="info")


__all__ = ["UIServer"]