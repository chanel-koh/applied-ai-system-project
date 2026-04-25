from pathlib import Path
from typing import List

DOC_PATH = Path(__file__).resolve().parent / "pet_care_docs.md"


def load_documentation() -> List[str]:
    """Load pet care documentation snippets from the local knowledge file."""
    if not DOC_PATH.exists():
        return []

    text = DOC_PATH.read_text(encoding="utf-8")
    snippets = [line.strip() for line in text.splitlines() if line.strip()]
    return snippets


def score_snippet(query: str, snippet: str) -> int:
    """Score how well a documentation snippet matches the query by shared normalized terms."""
    query_terms = {term for term in query.lower().split() if len(term) > 2}
    snippet_terms = {term for term in snippet.lower().replace("-", " ").split() if len(term) > 2}
    return len(query_terms & snippet_terms)


def retrieve_relevant_docs(query: str, top_k: int = 3) -> List[str]:
    """Return the most relevant documentation snippets for a query."""
    docs = load_documentation()
    if not docs:
        return []

    ranked = sorted(docs, key=lambda snippet: score_snippet(query, snippet), reverse=True)
    top_docs = [snippet for snippet in ranked if score_snippet(query, snippet) > 0]
    return top_docs[:top_k] if top_docs else docs[:top_k]
