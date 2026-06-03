from pathlib import Path


def test_dependabot_covers_actions_and_python_dependencies() -> None:
    # Given: dependabot configuration.
    content = Path(".github/dependabot.yml").read_text(encoding="utf-8")

    # When: ecosystems are inspected.
    # Then: GitHub Actions and uv/Python dependencies are covered.
    assert 'package-ecosystem: "github-actions"' in content
    assert 'package-ecosystem: "uv"' in content
    assert 'directory: "/"' in content
