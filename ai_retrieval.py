from pathlib import Path
from typing import List

DOC_PATH = Path(__file__).resolve().parent / "pet_care_docs.md"


def load_documentation() -> List[str]:
    """Load pet care documentation snippets from the local knowledge file."""
    if not DOC_PATH.exists():
        return []

    text = DOC_PATH.read_text(encoding="utf-8")
    lines = [line.rstrip() for line in text.splitlines()]
    snippets: List[str] = []
    current_heading: str = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("#"):
            current_heading = stripped.lstrip("#").strip()
            continue

        if stripped.startswith("- "):
            content = stripped[2:].strip()
            if not content:
                continue
            snippet = f"{current_heading}: {content}" if current_heading else content
            snippets.append(snippet)
            continue

        snippet = f"{current_heading}: {stripped}" if current_heading else stripped
        snippets.append(snippet)

    return snippets


def score_snippet(query: str, snippet: str) -> int:
    """Score how well a documentation snippet matches the query by shared normalized terms."""
    query_terms = {term for term in query.lower().replace("-", " ").split() if len(term) > 2}
    snippet_terms = {term for term in snippet.lower().replace("-", " ").replace(":", " ").split() if len(term) > 2}
    score = len(query_terms & snippet_terms)

    section_label = snippet.split(":", 1)[0].lower()
    section_terms = {term for term in section_label.split() if len(term) > 2}
    score += len(query_terms & section_terms)

    return score


def retrieve_relevant_docs(query: str, top_k: int = 3) -> List[str]:
    """Return the most relevant documentation snippets for a query."""
    docs = load_documentation()
    if not docs:
        return []

    ranked = sorted(docs, key=lambda snippet: score_snippet(query, snippet), reverse=True)
    top_docs = [snippet for snippet in ranked if score_snippet(query, snippet) > 0]
    return top_docs[:top_k] if top_docs else docs[:top_k]
