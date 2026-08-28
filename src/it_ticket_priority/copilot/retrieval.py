"""Small, inspectable TF-IDF retriever for grounded service-desk runbooks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from it_ticket_priority.config import PROJECT_ROOT

from .models import RetrievedEvidence


@dataclass(frozen=True, slots=True)
class _KnowledgeChunk:
    evidence_id: str
    document_id: str
    title: str
    section: str
    source_path: str
    text: str


class RunbookRetriever:
    """Retrieve transparent evidence without a vector database or paid service."""

    def __init__(self, runbook_dir: str | Path | None = None) -> None:
        self.runbook_dir = Path(runbook_dir or PROJECT_ROOT / "knowledge_base" / "runbooks")
        self._chunks = self._load_chunks()
        if not self._chunks:
            raise ValueError(f"No Markdown runbooks found in {self.runbook_dir}")

        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            strip_accents="unicode",
            sublinear_tf=True,
        )
        self._matrix = self._vectorizer.fit_transform(chunk.text for chunk in self._chunks)

    def _load_chunks(self) -> list[_KnowledgeChunk]:
        chunks: list[_KnowledgeChunk] = []
        for path in sorted(self.runbook_dir.glob("*.md")):
            chunks.extend(self._split_markdown(path))
        return chunks

    def _split_markdown(self, path: Path) -> list[_KnowledgeChunk]:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = next(
            (line.removeprefix("# ").strip() for line in lines if line.startswith("# ")),
            path.stem.replace("_", " ").title(),
        )
        sections: list[tuple[str, list[str]]] = []
        current_heading = "Overview"
        current_lines: list[str] = []

        for line in lines:
            if line.startswith("## "):
                if current_lines:
                    sections.append((current_heading, current_lines))
                current_heading = line.removeprefix("## ").strip()
                current_lines = []
            elif not line.startswith("# "):
                current_lines.append(line)
        if current_lines:
            sections.append((current_heading, current_lines))

        document_id = path.stem
        try:
            relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            relative_path = path.as_posix()
        output: list[_KnowledgeChunk] = []
        for section, body_lines in sections:
            body = "\n".join(body_lines).strip()
            if not body:
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-") or "section"
            evidence_id = f"{document_id}#{slug}"
            output.append(
                _KnowledgeChunk(
                    evidence_id=evidence_id,
                    document_id=document_id,
                    title=title,
                    section=section,
                    source_path=relative_path,
                    text=f"{title}\n{section}\n{body}",
                )
            )
        return output

    def search(
        self,
        query: str,
        *,
        top_k: int = 3,
        min_score: float = 0.04,
    ) -> list[RetrievedEvidence]:
        """Return the highest-scoring runbook fragments above a transparent threshold."""

        if not query.strip():
            return []
        query_vector = self._vectorizer.transform([query])
        scores = (self._matrix @ query_vector.T).toarray().ravel()
        ranked_indices = np.argsort(scores)[::-1]

        results: list[RetrievedEvidence] = []
        for index in ranked_indices:
            score = float(scores[index])
            if score < min_score or len(results) >= top_k:
                break
            chunk = self._chunks[int(index)]
            excerpt = chunk.text[:900].strip()
            results.append(
                RetrievedEvidence(
                    evidence_id=chunk.evidence_id,
                    document_id=chunk.document_id,
                    title=chunk.title,
                    section=chunk.section,
                    source_path=chunk.source_path,
                    score=round(score, 4),
                    excerpt=excerpt,
                )
            )
        return results

    def list_documents(self) -> list[str]:
        return sorted({chunk.document_id for chunk in self._chunks})
