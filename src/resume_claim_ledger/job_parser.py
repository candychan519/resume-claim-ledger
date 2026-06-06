import re
from typing import Final

from .models import JobRequirement

TOKEN_PATTERN: Final = re.compile(r"[A-Za-z][A-Za-z0-9.+#-]*|[가-힣]{2,}")
REQUIRED_HEADINGS: Final[tuple[str, ...]] = ("required", "requirements", "must", "필수", "자격")
PREFERRED_HEADINGS: Final[tuple[str, ...]] = ("preferred", "nice", "우대", "선호")


def extract_job_requirements(text: str) -> list[JobRequirement]:
    requirements: list[JobRequirement] = []
    current_required = True

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        heading_requiredness = _heading_requiredness(stripped)
        if heading_requiredness is not None:
            current_required = heading_requiredness
            continue

        bullet = _bullet_text(stripped)
        if bullet == "":
            continue

        requirement_number = len(requirements) + 1
        requirements.append(
            JobRequirement(
                requirement_id=f"REQ-{requirement_number:03}",
                text=bullet,
                keywords=_extract_keywords(bullet),
                required=current_required,
            ),
        )

    return requirements


def _heading_requiredness(line: str) -> bool | None:
    if not line.startswith("#"):
        return None

    heading = line.lstrip("#").strip().casefold()
    if any(term in heading for term in PREFERRED_HEADINGS):
        return False
    if any(term in heading for term in REQUIRED_HEADINGS):
        return True
    return None


def _bullet_text(line: str) -> str:
    if not line.startswith(("- ", "* ")):
        return ""
    return line[2:].strip()


def _extract_keywords(text: str) -> tuple[str, ...]:
    keywords: list[str] = []
    seen: set[str] = set()
    for match in TOKEN_PATTERN.finditer(text):
        keyword = match.group(0)
        normalized = keyword.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        keywords.append(keyword)
    return tuple(keywords)
