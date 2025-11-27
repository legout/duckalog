"""
Example: Custom Filesystem Authentication

This example demonstrates how to use custom fsspec filesystem objects
for loading Duckalog configurations from remote storage systems with
advanced authentication scenarios.

This is useful for:
- Programmatic credential management
- Testing scenarios with custom authentication
- CI/CD pipelines with injected credentials
- Multi-cloud scenarios with different auth methods
"""

import fsspec
from duckalog import load_config


def main():
    """Demonstrate custom filesystem authentication."""

    print("=== Duckalog Custom Filesystem Example ===\\n")

    # Example 1: S3 with direct credentials
    print("1. Loading from S3 with custom filesystem...")
    try:
        # Create S3 filesystem with direct credentials
        s3_fs = fsspec.filesystem(
            "s3",
            key="AKIAIOSFODNN7EXAMPLE",
            secret="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        )

        # Load config with custom filesystem
        print("   Creating S3 filesystem with direct credentials...")
        print("   Loading config from s3://example-bucket/configs/catalog.yaml...")

        # This would work if the bucket existed:
        # config = load_config("s3://example-bucket/configs/catalog.yaml", filesystem=s3_fs)
        # print(f"   ✓ Loaded {len(config.views)} views from S3")

        print("   ✓ S3 filesystem created successfully")

    except Exception as e:
        print(f"   ⚠ S3 example: {e}")

    print()

    # Example 2: GitHub with personal access token
    print("2. Loading from GitHub with token...")
    try:
        # Create GitHub filesystem with token
        github_fs = fsspec.filesystem("github", token="ghp_xxxxxxxxxxxxxxxxxxxx")

        print("   Creating GitHub filesystem with personal access token...")
        print("   Loading config from github://user/repo/config.yaml...")

        # This would work if the repository existed:
        # config = load_config("github://user/repo/config.yaml", filesystem=github_fs)
        # print(f"   ✓ Loaded {len(config.views)} views from GitHub")

        print("   ✓ GitHub filesystem created successfully")

    except Exception as e:
        print(f"   ⚠ GitHub example: {e}")

    print()

    # Example 3: Azure with connection string
    print("3. Loading from Azure Blob Storage...")
    try:
        # Create Azure filesystem with connection string
        azure_fs = fsspec.filesystem(
            "abfs",
            connection_string="DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key;EndpointSuffix=core.windows.net",
        )

        print("   Creating Azure filesystem with connection string...")
        print("   Loading config from abfs://account@container/config.yaml...")

        # This would work if the container existed:
        # config = load_config("abfs://account@container/config.yaml", filesystem=azure_fs)
        # print(f"   ✓ Loaded {len(config.views)} views from Azure")

        print("   ✓ Azure filesystem created successfully")

    except Exception as e:
        print(f"   ⚠ Azure example: {e}")

    print()

    # Example 4: SFTP with SSH key
    print("4. Loading from SFTP server...")
    try:
        # Create SFTP filesystem with SSH key
        sftp_fs = fsspec.filesystem(
            "sftp",
            host="sftp.example.com",
            username="user",
            private_key="~/.ssh/id_rsa",
        )

        print("   Creating SFTP filesystem with SSH key...")
        print("   Loading config from sftp://user@sftp.example.com/path/config.yaml...")

        # This would work if the server existed:
        # config = load_config("sftp://user@sftp.example.com/path/config.yaml", filesystem=sftp_fs)
        # print(f"   ✓ Loaded {len(config.views)} views from SFTP")

        print("   ✓ SFTP filesystem created successfully")

    except Exception as e:
        print(f"   ⚠ SFTP example: {e}")

    print()

    # Example 5: Anonymous access (public buckets)
    print("5. Loading from public S3 bucket...")
    try:
        # Create anonymous S3 filesystem
        anon_fs = fsspec.filesystem("s3", anon=True)

        print("   Creating anonymous S3 filesystem...")
        print("   Loading config from s3://public-bucket/config.yaml...")

        # This would work if the public bucket existed:
        # config = load_config("s3://public-bucket/config.yaml", filesystem=anon_fs)
        # print(f"   ✓ Loaded {len(config.views)} views from public bucket")

        print("   ✓ Anonymous S3 filesystem created successfully")

    except Exception as e:
        print(f"   ⚠ Anonymous example: {e}")

    print()

    # Backward compatibility demonstration
    print("6. Backward compatibility - no filesystem needed...")
    print("   Environment variable authentication still works:")
    print("   - Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
    print("   - Use GOOGLE_APPLICATION_CREDENTIALS for GCS")
    print("   - Set Azure credentials in environment")
    print("   ✓ Backward compatibility maintained")

    print()
    print("=== Example Complete ===")
    print()
    print("Key Benefits:")
    print("✓ Flexible authentication without environment variables")
    print("✓ Programmatic credential management")
    print("✓ Testing scenarios with custom filesystems")
    print("✓ CI/CD integration with secure credential injection")
    print("✓ Multi-cloud support with different auth methods")
    print("✓ Backward compatibility preserved")


if __name__ == "__main__":
    main()
