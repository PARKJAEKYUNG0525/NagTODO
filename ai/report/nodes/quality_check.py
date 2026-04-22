import re


# bullet 패턴: 들여쓰기 허용, 번호 목록 공백 선택적
_BULLET_PATTERN = re.compile(r"^\s*[-•*]\s|^\s*\d+\.\s*\S", re.MULTILINE)
# 통계 숫자: 날짜(YYYY-MM, YYYY/MM) 맥락의 숫자는 제외
_STAT_PATTERN = re.compile(r"(?<!\d[-/])\b\d+\b(?![-/]\d)")


def quality_check(state: dict) -> dict:
    """리포트 품질을 3가지 규칙으로 검증한다."""
    report: str = state.get("retrospective_report") or ""

    issues: list[str] = []

    if len(report) < 100:
        issues.append(f"리포트가 너무 짧습니다 ({len(report)}자)")

    if not _BULLET_PATTERN.search(report):
        issues.append("개선 방향 bullet 항목이 없습니다")

    if not _STAT_PATTERN.search(report):
        issues.append("통계 숫자가 인용되지 않았습니다")

    return {
        "quality_passed": len(issues) == 0,
        "quality_issues": issues,
    }
