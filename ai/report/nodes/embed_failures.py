from ai.core.dependencies import get_embedding_model


def embed_failures(state: dict) -> dict:
    """failed_tasks의 텍스트를 임베딩하여 failure_embeddings(list)로 저장."""
    failed_tasks: list[dict] = state["failed_tasks"]

    if not failed_tasks:
        return {"failure_embeddings": []}

    model = get_embedding_model()
    embeddings = [
        model.encode_passage(task["text"]).tolist()
        for task in failed_tasks
    ]

    return {"failure_embeddings": embeddings}
