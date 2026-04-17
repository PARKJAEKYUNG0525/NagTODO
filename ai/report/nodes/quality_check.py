import re


# bullet 패턴: -, •, *, 또는 숫자 목록(1. 2. 등)
_BULLET_PATTERN = re.compile(r"(^[-•*]|\d+\.)\s", re.MULTILINE)
_NUMBER_PATTERN = re.compile(r"\d+")


def quality_check(state: dict) -> dict:
    """리포트 품질을 3가지 규칙으로 검증한다."""
    report: str = state.get("retrospective_report", "")

    issues: list[str] = []

    if len(report) < 100:
        issues.append(f"리포트 길이 부족 ({len(report)}자 < 100자)")

    if not _BULLET_PATTERN.search(report):
        issues.append("bullet 항목(-, •, *, 번호 목록) 없음")

    if not _NUMBER_PATTERN.search(report):
        issues.append("숫자 수치 없음")

    return {
        "quality_passed": len(issues) == 0,
        "quality_issues": issues,
    }
