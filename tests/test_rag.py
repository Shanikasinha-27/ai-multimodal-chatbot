from rag.retriever import rag_retriever

def test_rag_retrieval_grounding():
    query = "I am having a panic attack and need to feel grounded right now"
    results = rag_retriever.retrieve(query, top_k=2)
    assert len(results) > 0
    categories = [r.get("category") for r in results]
    assert "grounding" in categories
    
    formatted = rag_retriever.format_context_for_prompt(results)
    assert "5-4-3-2-1" in formatted or "Breathing" in formatted

def test_rag_retrieval_cbt():
    query = "I am catastrophizing and feel like a total failure"
    results = rag_retriever.retrieve(query, top_k=2)
    assert len(results) > 0
    assert any("cbt" in r.get("category", "") for r in results)
