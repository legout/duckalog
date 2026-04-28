import warnings


def test_no_warning_on_modern_import(tmp_path):
    config_file = tmp_path / "catalog.yaml"
    config_file.write_text("version: 1\nduckdb:\n  database: ':memory:'\nviews: []")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Direct import from duckalog.config should be fine
        from duckalog.config import load_config

        load_config(str(config_file))

        assert (
            len(
                [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
            )
            == 0
        )


