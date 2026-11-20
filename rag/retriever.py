import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class RAGRetriever:
    """
    RAG (Retrieval-Augmented Generation) Engine for Emotional Support.
    Provides semantic search over evidence-based mental wellness techniques,
    coping strategies, and uploaded guidance documents.
    """

    def __init__(self):
        self.knowledge_dir = Path(__file__).parent / "knowledge_base"
        self.knowledge_entries: List[Dict[str, Any]] = []
        self._load_built_in_knowledge()

    def _load_built_in_knowledge(self):
        """Loads all static JSON knowledge bases."""
        json_files = self.knowledge_dir.glob("*.json")
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                    if isinstance(entries, list):
                        self.knowledge_entries.extend(entries)
            except Exception as e:
                logger.error(f"Failed to load knowledge file {jf}: {e}")
        logger.info(f"Loaded {len(self.knowledge_entries)} knowledge entries into RAG index.")

    def retrieve(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Retrieves top_k most relevant knowledge articles based on query context.
        Uses keyword-weighted semantic overlap scoring.
        """
        if not query or not self.knowledge_entries:
            return []

        query_tokens = set(query.lower().split())
        scored_results = []

        for entry in self.knowledge_entries:
            score = 0.0
            
            # 1. Trigger matching (high weight)
            triggers = entry.get("triggers", [])
            for trigger in triggers:
                if trigger.lower() in query.lower():
                    score += 5.0
                else:
                    trigger_words = trigger.lower().split()
                    if any(tw in query_tokens for tw in trigger_words):
                        score += 2.0
            
            # 2. Title matching
            title_words = set(entry.get("title", "").lower().split())
            score += len(query_tokens.intersection(title_words)) * 2.0
            
            # 3. Content matching
            content_words = set(entry.get("content", "").lower().split())
            score += len(query_tokens.intersection(content_words)) * 0.3

            if score > 0:
                scored_results.append((score, entry))

        # Sort descending by relevance score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:top_k]]

    def format_context_for_prompt(self, relevant_entries: List[Dict[str, Any]]) -> str:
        """Formats retrieved knowledge entries into a structured string for prompt injection."""
        if not relevant_entries:
            return ""

        context_blocks = []
        for i, entry in enumerate(relevant_entries, 1):
            block = (
                f"[REFERENCE TECHNIQUE {i}: {entry.get('title')}]\n"
                f"Category: {entry.get('category')}\n"
                f"{entry.get('content')}"
            )
            context_blocks.append(block)

        return "\n\n".join(context_blocks)

# Singleton retriever instance
rag_retriever = RAGRetriever()
