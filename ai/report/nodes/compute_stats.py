def compute_stats(state: dict) -> dict:
    """monthly_logs에서 카테고리별 달성률을 집계한다."""
    monthly_logs: list[dict] = state["monthly_logs"]

    stats: dict[str, dict] = {}
    for task in monthly_logs:
        cat = task.get("category", "기타")
        if cat not in stats:
            stats[cat] = {"total": 0, "completed": 0}
        stats[cat]["total"] += 1
        if task.get("completed", False):
            stats[cat]["completed"] += 1

    category_stats = {
        cat: {
            "total": v["total"],
            "completed": v["completed"],
            "rate": round(v["completed"] / v["total"] * 100, 1),
        }
        for cat, v in stats.items()
    }

    return {"category_stats": category_stats}
