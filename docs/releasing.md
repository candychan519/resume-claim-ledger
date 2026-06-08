# Release Process

## Versioning

Use SemVer tags in the form `vMAJOR.MINOR.PATCH`. A current release is an
artifact-only release. Release only after the full local gate passes:

```bash
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## Artifact-Only Flow

The release workflow builds the source distribution and wheel, then stores them
as a GitHub artifact named `dist`. It does not upload to TestPyPI or production
PyPI.

Use `workflow_dispatch` or a SemVer tag to run the workflow, then download the
GitHub artifact from the run summary if you need to inspect or install the built
package locally.

## Publishing Deferred

TestPyPI and PyPI publishing are intentionally disabled until the project is
ready for public package-index expectations. When publishing becomes useful,
restore Trusted Publishing jobs and configure a TestPyPI Trusted Publisher for:

- project name: `resume-claim-ledger`
- owner: `candychan519`
- repository: `resume-claim-ledger`
- workflow filename: `release.yml`
- environment: `testpypi`

For the first upload, create it as a pending publisher in TestPyPI. The first successful workflow run will create the TestPyPI project.

## production PyPI

Production PyPI publishing should stay disabled until TestPyPI is green and the
package is ready for external users. When enabling it, use Trusted Publishing
through GitHub Actions OIDC and the `pypi` GitHub environment. Configure the
PyPI Trusted Publisher with:

- project name: `resume-claim-ledger`
- owner: `candychan519`
- repository: `resume-claim-ledger`
- workflow filename: `release.yml`
- environment: `pypi`

The `pypi` environment should require manual approval.

## Rollback

Use this rollback policy after a bad release: GitHub release assets may be deleted or a release may be marked as pre-release if no users consumed it. PyPI files cannot be replaced after upload. A bad PyPI version must be yanked, followed by a patch release.

## Hotfix

Create a minimal hotfix branch, add a regression test, release the next patch version, and mention the yanked version in the changelog.
