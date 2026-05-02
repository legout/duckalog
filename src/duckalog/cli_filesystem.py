"""CLI filesystem helpers for Duckalog.

Extracted from cli.py to keep the command definitions separate from
filesystem option normalization and fsspec protocol construction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

# Import fsspec at module level for easier testing
try:
    import fsspec
except ImportError:
    fsspec = None  # Will be handled in the function


def _create_filesystem_from_options(
    protocol: Optional[str] = None,
    key: Optional[str] = None,
    secret: Optional[str] = None,
    token: Optional[str] = None,
    anon: bool = False,
    timeout: Optional[int] = 30,
    aws_profile: Optional[str] = None,
    gcs_credentials_file: Optional[str] = None,
    azure_connection_string: Optional[str] = None,
    sftp_host: Optional[str] = None,
    sftp_port: int = 22,
    sftp_key_file: Optional[str] = None,
):
    """Create a fsspec filesystem from CLI options.

    Returns None if no filesystem options are provided.

    Args:
        protocol: Filesystem protocol (s3, gcs, abfs, sftp, github)
        key: API key or access key
        secret: Secret key or password
        token: Authentication token
        anon: Use anonymous access
        timeout: Connection timeout
        aws_profile: AWS profile name
        gcs_credentials_file: Path to GCS credentials file
        azure_connection_string: Azure connection string
        sftp_host: SFTP server hostname
        sftp_port: SFTP server port
        sftp_key_file: Path to SFTP private key file

    Returns:
        fsspec filesystem object or None

    Raises:
        typer.Exit: If filesystem creation fails
    """
    # If no filesystem options provided, return None
    if not any(
        [
            protocol,
            key,
            secret,
            token,
            anon,
            aws_profile,
            gcs_credentials_file,
            azure_connection_string,
            sftp_host,
            sftp_key_file,
        ]
    ):
        return None

    # Check if fsspec is available
    if fsspec is None:
        typer.echo(
            "fsspec is required for filesystem options. Install with: pip install duckalog[remote]",
            err=True,
        )
        raise typer.Exit(4)

    # Validate protocol if provided or try to infer from other options
    if not protocol:
        # Try to infer protocol from provided options
        if aws_profile or (key and secret):
            protocol = "s3"
        elif gcs_credentials_file:
            protocol = "gcs"
        elif azure_connection_string or (key and secret):
            protocol = "abfs"
        elif sftp_host or sftp_key_file:
            protocol = "sftp"
        elif token:
            protocol = "github"
        else:
            typer.echo(
                "Protocol must be specified or inferable from provided options.",
                err=True,
            )
            raise typer.Exit(4)

    # Validate required options for specific protocols
    if protocol in ["s3"] and not any([aws_profile, key, secret, anon]):
        typer.echo(
            "For S3 protocol, provide either --aws-profile, --fs-key/--fs-secret, or use --fs-anon",
            err=True,
        )
        raise typer.Exit(4)

    if protocol in ["abfs", "adl", "az"] and not any(
        [azure_connection_string, key, secret]
    ):
        typer.echo(
            "For Azure protocol, provide either --azure-connection-string or --fs-key/--fs-secret",
            err=True,
        )
        raise typer.Exit(4)

    if protocol == "sftp" and not sftp_host:
        typer.echo(
            "SFTP protocol requires --sftp-host to be specified",
            err=True,
        )
        raise typer.Exit(4)

    # Validate mutual exclusivity
    if aws_profile and key:
        typer.echo(
            "Cannot specify both --aws-profile and --fs-key",
            err=True,
        )
        raise typer.Exit(4)

    if azure_connection_string and key:
        typer.echo(
            "Cannot specify both --azure-connection-string and --fs-key",
            err=True,
        )
        raise typer.Exit(4)

    # Validate file paths exist if provided
    if gcs_credentials_file and not Path(gcs_credentials_file).exists():
        typer.echo(
            f"GCS credentials file not found: {gcs_credentials_file}",
            err=True,
        )
        raise typer.Exit(4)

    if sftp_key_file and not Path(sftp_key_file).exists():
        typer.echo(
            f"SFTP key file not found: {sftp_key_file}",
            err=True,
        )
        raise typer.Exit(4)

    # Determine protocol from URI or explicit parameter
    filesystem_options = {}

    # Add timeout if specified
    if timeout:
        filesystem_options["timeout"] = timeout

    # Handle different protocols
    if protocol == "s3" or aws_profile:
        if aws_profile:
            filesystem_options["profile"] = aws_profile
        elif key and secret:
            filesystem_options.update(
                {
                    "key": key,
                    "secret": secret,
                    "anon": anon or False,
                }
            )
            # Add region if needed
            filesystem_options["client_kwargs"] = {}
        else:
            # Use default AWS credential resolution
            pass

    elif protocol == "gcs":
        if gcs_credentials_file:
            filesystem_options["token"] = gcs_credentials_file
        # Otherwise use default ADC

    elif protocol in ["abfs", "adl", "az"]:
        if azure_connection_string:
            filesystem_options["connection_string"] = azure_connection_string
        elif key and secret:
            # Handle Azure account key auth
            filesystem_options.update(
                {
                    "account_name": key,
                    "account_key": secret,
                }
            )

    elif protocol == "sftp":
        filesystem_options.update(
            {
                "host": sftp_host,
                "port": sftp_port,
            }
        )
        if sftp_key_file:
            filesystem_options["key_filename"] = sftp_key_file
        elif secret:  # Use password if key file not provided
            filesystem_options["password"] = secret
        elif key:  # Use key as username
            filesystem_options["username"] = key

    elif protocol == "github":
        if token:
            filesystem_options["token"] = token
        elif key:
            filesystem_options["username"] = key
            if secret:
                filesystem_options["password"] = secret

    elif protocol == "https" or protocol == "http":
        # HTTP/HTTPS doesn't need special filesystem creation
        # Just return None to use built-in requests
        return None

    try:
        return fsspec.filesystem(protocol, **filesystem_options)
    except Exception as exc:
        typer.echo(
            f"Failed to create filesystem for protocol '{protocol}': {exc}",
            err=True,
        )
        raise typer.Exit(4)
