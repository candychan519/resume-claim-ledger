from resume_claim_ledger.job_parser import extract_job_requirements


def test_extract_job_requirements_from_markdown_required_and_preferred_sections() -> None:
    # Given: a Markdown job description with required and preferred sections.
    job_text = (
        "## 필수\n"
        "- Python, MLOps 운영\n"
        "- 장애 대응 문서화\n"
        "## 우대\n"
        "- 배포 자동화 경험"
    )

    # When: requirements are extracted.
    requirements = extract_job_requirements(job_text)

    # Then: section requiredness and keywords are preserved deterministically.
    assert [requirement.requirement_id for requirement in requirements] == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
    ]
    assert [requirement.required for requirement in requirements] == [True, True, False]
    assert requirements[0].text == "Python, MLOps 운영"
    assert requirements[0].keywords == ("Python", "MLOps", "운영")
    assert requirements[2].keywords == ("배포", "자동화", "경험")


def test_extract_job_requirements_when_input_is_empty_returns_empty_list() -> None:
    # Given: an empty job description.
    job_text = " \n\t "

    # When: requirements are extracted.
    requirements = extract_job_requirements(job_text)

    # Then: no synthetic requirements are invented.
    assert requirements == []


def test_extract_job_requirements_keeps_stable_ordered_ids() -> None:
    # Given: a job description without recognized headings.
    job_text = "- FastAPI 서비스 운영\n* PostgreSQL 쿼리 튜닝"

    # When: requirements are extracted.
    requirements = extract_job_requirements(job_text)

    # Then: bullets default to required and keep input order.
    assert [(item.requirement_id, item.required, item.text) for item in requirements] == [
        ("REQ-001", True, "FastAPI 서비스 운영"),
        ("REQ-002", True, "PostgreSQL 쿼리 튜닝"),
    ]


def test_extract_job_requirements_marks_preferred_requirements_heading_as_optional() -> None:
    # Given: a preferred heading that also contains the word requirements.
    job_text = "## Preferred Requirements\n- Kubernetes 운영"

    # When: requirements are extracted.
    requirements = extract_job_requirements(job_text)

    # Then: the preferred section remains optional.
    assert [(item.requirement_id, item.required, item.text) for item in requirements] == [
        ("REQ-001", False, "Kubernetes 운영"),
    ]
