# Release Process

## Versioning

Use SemVer tags in the form `vMAJOR.MINOR.PATCH`. Release only after the full local gate passes:

```bash
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## TestPyPI First

Publish to TestPyPI before production PyPI. Configure a TestPyPI Trusted Publisher for:

- owner: `candychan519`
- repository: `resume-claim-ledger`
- workflow filename: `release.yml`
- environment: `testpypi`

## production PyPI

Production PyPI publishing uses Trusted Publishing through GitHub Actions OIDC and the `pypi` GitHub environment. Configure the PyPI Trusted Publisher with:

- owner: `candychan519`
- repository: `resume-claim-ledger`
- workflow filename: `release.yml`
- environment: `pypi`

The `pypi` environment should require manual approval.

## Rollback

Use this rollback policy after a bad release: GitHub release assets may be deleted or a release may be marked as pre-release if no users consumed it. PyPI files cannot be replaced after upload. A bad PyPI version must be yanked, followed by a patch release.

## Hotfix

Create a minimal hotfix branch, add a regression test, release the next patch version, and mention the yanked version in the changelog.
