from app.schemas.ask import AskCitation, AskRequest, AskResponse, AskResultOrderItem, AskSupportingResult
from app.schemas.search import SearchRequest
from app.services.llm.factory import get_llm_provider
from app.services.reranking_service import RerankingService
from app.services.search_service import SearchService


class AskService:
    @staticmethod
    def ask(db, payload: AskRequest) -> AskResponse:
        retrieval_payload = SearchRequest(
            query=payload.query,
            project_id=payload.project_id,
            top_k=payload.top_k,
            document_ids=payload.document_ids,
        )
        retrieval_response = SearchService.search(db, retrieval_payload)
        reranked_results = RerankingService.rerank(
            query=payload.query,
            candidates=retrieval_response.results,
        )

        supporting_results = [
            AskSupportingResult(
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                score=item.score,
                content=item.content,
            )
            for item in reranked_results
        ]

        citations = [
            AskCitation(
                document_id=item.document_id,
                chunk_id=item.chunk_id,
                chunk_index=item.chunk_index,
                snippet=item.content[:240],
            )
            for item in reranked_results
        ]

        prompt = AskService._build_grounded_prompt(
            query=payload.query,
            contexts=[item.content for item in reranked_results],
        )

        llm_provider = get_llm_provider()
        answer = llm_provider.generate_grounded_answer(
            query=payload.query,
            prompt=prompt,
            contexts=[item.content for item in reranked_results],
        )

        if not reranked_results:
            answer = "Insufficient evidence in retrieved context to answer this question."

        retrieved_order = [
            AskResultOrderItem(chunk_id=item.chunk_id, position=index + 1)
            for index, item in enumerate(retrieval_response.results)
        ]
        reranked_order = [
            AskResultOrderItem(chunk_id=item.chunk_id, position=index + 1)
            for index, item in enumerate(reranked_results)
        ]

        return AskResponse(
            answer=answer,
            citations=citations,
            supporting_results=supporting_results,
            retrieved_order=retrieved_order,
            reranked_order=reranked_order,
        )

    @staticmethod
    def _build_grounded_prompt(query: str, contexts: list[str]) -> str:
        instructions = (
            "You are a grounded assistant. Answer only using the provided context chunks. "
            "If evidence is missing or weak, return an explicit insufficient-evidence answer. "
            "Do not invent facts."
        )
        context_block = "\n\n".join(
            f"[CONTEXT {idx + 1}]\n{context}" for idx, context in enumerate(contexts)
        )
        return f"{instructions}\n\n[QUESTION]\n{query}\n\n[CONTEXTS]\n{context_block}"
