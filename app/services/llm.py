from typing import List
from app.models.schemas import RetrievedChunk, GraphPath
from app.services.azure_openai import chat_complete


SYSTEM_PROMPT = (
	"You are a helpful assistant that answers strictly using the provided context. "
	"Cite evidence via short references in parentheses when possible. If unsure, say you don't know."
)


def build_user_prompt(question: str, chunks: List[RetrievedChunk], paths: List[GraphPath]) -> str:
	lines: List[str] = []
	lines.append("Question: " + question)
	lines.append("")
	lines.append("Context:")
	for i, c in enumerate(chunks[:8]):
		ref = c.metadata.get("filename") or c.metadata.get("document_id") or c.metadata.get("chunk_id")
		lines.append(f"- Chunk {i+1} [{ref}]: {c.text}")
	for i, p in enumerate(paths[:8]):
		lines.append(f"- Graph Path {i+1}: {' -> '.join(p.nodes)}")
	lines.append("")
	lines.append("Answer succinctly and factually based on the context above.")
	return "\n".join(lines)


def answer_question(question: str, chunks: List[RetrievedChunk], paths: List[GraphPath]) -> str:
	user_prompt = build_user_prompt(question, chunks, paths)
	return chat_complete(SYSTEM_PROMPT, user_prompt)
