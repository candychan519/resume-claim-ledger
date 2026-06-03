# Maintenance

## Routine Checks

Run the local gate before merging:

```bash
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## Dependencies

Dependabot tracks GitHub Actions and uv/Python dependencies. Review dependency updates with the same local gate.

## Release Safety

Use GitHub environments for TestPyPI and PyPI. Keep production publishing behind manual approval.
