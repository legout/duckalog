## 1. Spec updates
- [ ] 1.1 Update `specs/config/spec.md` to describe the config package structure and responsibilities
- [ ] 1.2 Ensure `refactor-consolidate-config-layer` and this change are consistent in intent and do not conflict

## 2. Package scaffolding
- [ ] 2.1 Create `src/duckalog/config/` with initial `__init__.py`
- [ ] 2.2 Move Pydantic models from `config.py` into `models.py`
- [ ] 2.3 Move `load_config` and related helpers into `loader.py`
- [ ] 2.4 Move env interpolation helpers into `interpolation.py`
- [ ] 2.5 Move complex validators into `validators.py`
- [ ] 2.6 Move SQL file loading glue into `sql_integration.py`

## 3. Public API compatibility
- [ ] 3.1 Ensure `duckalog.config` continues to export all previously documented symbols
- [ ] 3.2 Add tests to assert key imports still work (for example, `from duckalog.config import Config, load_config`)

## 4. Internal import updates
- [ ] 4.1 Update engine, CLI, remote-config, and tests to import from the new package layout where appropriate
- [ ] 4.2 Run full test suite to verify behavior and imports

