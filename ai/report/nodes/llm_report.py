import json

from ai.core.dependencies import get_openai_client

# Backward-compatible alias for existing tests/patch paths.
get_ollama_client = get_openai_client


async def llm_report(state: dict) -> dict:
    """cluster_summaries? category_stats瑜?諛뷀깢?쇰줈 ?붽컙 ?뚭퀬 由ы룷?몃? ?앹꽦?쒕떎."""
    cluster_summaries: list[dict] = state.get("cluster_summaries") or []
    category_stats: dict = state.get("category_stats") or {}
    retry_count: int = state.get("retry_count", 0)
    quality_issues: list[str] = state.get("quality_issues", [])

    stats_json = json.dumps(category_stats, ensure_ascii=False, indent=2)
    clusters_json = json.dumps(cluster_summaries, ensure_ascii=False, indent=2)

    base_prompt = (
        "?ㅼ쓬 ?뺣낫瑜?諛뷀깢?쇰줈 ?붽컙 ?뚭퀬 由ы룷?몃? ?묒꽦?섎씪.\n\n"
        f"[移댄뀒怨좊━蹂??ъ꽦瑜?\n{stats_json}\n\n"
        f"[?ㅽ뙣 ?대윭?ㅽ꽣 ?붿빟]\n{clusters_json}\n\n"

        "?붽뎄?ы빆:\n"
        "- ?꾩껜 300???댁긽\n"
        "- bullet ??ぉ(-, ?? *, 踰덊샇 紐⑸줉) ?ы븿\n"
        "- 紐⑤뱺 遺꾩꽍??援ъ껜?곸씤 ?レ옄(%, ?잛닔 ?? ?ы븿\n"
        "- ?⑥닚 ?붿빟???꾨땶 '?먯씤 遺꾩꽍 + 媛쒖꽑 ?꾨왂' 以묒떖?쇰줈 ?묒꽦\n\n"

        "異쒕젰 援ъ“:\n"
        "1. ?듭떖 ?붿빟\n"
        "- ?대쾲 ???깃낵瑜???臾몃떒?쇰줈 ?붿빟 (?ъ꽦瑜??ы븿)\n\n"

        "2. ?ㅽ뙣 ?대윭?ㅽ꽣 遺꾩꽍\n"
        "- 媛??ㅽ뙣 ?대윭?ㅽ꽣蹂꾨줈 ?꾨옒 ??ぉ ?ы븿:\n"
        "  ??二쇱슂 ?ㅽ뙣 ?⑦꽩\n"
        "  ??諛쒖깮 鍮꾩쑉 ?먮뒗 ?잛닔\n"
        "  ??洹쇰낯 ?먯씤 (?됰룞, ?섍꼍, ?쒓컙 愿由???援ъ껜?곸쑝濡?\n\n"

        "3. 媛쒖꽑 ?꾨왂\n"
        "- 媛??ㅽ뙣 ?먯씤????묐릺??媛쒖꽑 ?≪뀡 ?쒖떆\n"
        "- 諛섎뱶??'痢≪젙 媛???섍퀬 '援ъ껜???됰룞'?쇰줈 ?묒꽦\n"
        "  (?? '?대룞 ???섍린' ????'二?3?? 30遺??대룞' 狩?\n\n"
    )

    if retry_count > 0 and quality_issues:
        issues_text = "\n".join(f"- {issue}" for issue in quality_issues)
        base_prompt += (
            f"\n?댁쟾 ?쒕룄?먯꽌 ?ㅼ쓬 臾몄젣媛 ?덉뿀?듬땲??\n{issues_text}\n"
            "??臾몄젣瑜?諛섎뱶???섏젙?섏뿬 ?ㅼ떆 ?묒꽦?섏꽭??\n"
        )

    base_prompt += "\n由ы룷??"

    client = get_openai_client()
    retrospective_report = await client.generate(base_prompt) or ""

    return {
        "retrospective_report": retrospective_report,
        "retry_count": retry_count + 1,
    }
