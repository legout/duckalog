import warnings
import pytest
import importlib
from duckalog.config import load_config


def test_no_warning_on_modern_import(tmp_path):
    config_file = tmp_path / "catalog.yaml"
    config_file.write_text("version: 1\nduckdb:\n  database: ':memory:'\nviews: []")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Direct import from duckalog.config should be fine
        from duckalog.config import Config, load_config

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


def test_warning_on_loader_import():
    import duckalog.config.loader

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(duckalog.config.loader)

        # We want this to trigger a warning
        assert (
            len(
                [
                    warning
                    for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
            )
            > 0
        )


def test_warning_on_interpolation_import():
    import duckalog.config.interpolation

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(duckalog.config.interpolation)

        # We want this to trigger a warning
        assert any(
            "duckalog.config.interpolation" in str(warning.message) for warning in w
        )


def test_warning_on_internal_function_call(tmp_path):
    from duckalog.config import _load_config_from_local_file

    config_file = tmp_path / "catalog.yaml"
    config_file.write_text("views: []")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            _load_config_from_local_file(str(config_file))
        except Exception:
            # We only care about the warning
            pass

        # We want this to trigger a warning
        assert any(
            "_load_config_from_local_file is internal and deprecated"
            in str(warning.message)
            for warning in w
        )
