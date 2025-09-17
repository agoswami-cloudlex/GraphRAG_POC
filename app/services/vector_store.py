from typing import List, Dict, Any, Optional
import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.services.azure_openai import embed_texts


class VectorStore:
	def delete_document_chunks(self, user_id: str, document_id: str):
		collection = self.get_or_create_collection(user_id)
		print(f"Deleting all chunks for document_id={document_id} in user {user_id}")
		collection.delete(where={"document_id": document_id})
	def debug_print_all_chunks(self, user_id: str):
		collection = self.get_or_create_collection(user_id)
		print(f"--- ChromaDB contents for user {user_id} ---")
		res = collection.get()
		ids = res.get("ids", [])
		docs = res.get("documents", [])
		metas = res.get("metadatas", [])
		for i in range(len(ids)):
			print(f"Chunk {i+1}: id={ids[i]}, text={docs[i][:60]}..., metadata={metas[i]}")
	def __init__(self) -> None:
		persist_dir = settings.chroma_persist_dir
		os.makedirs(persist_dir, exist_ok=True)
		self.client = chromadb.Client(ChromaSettings(persist_directory=persist_dir))

	def _collection_name(self, user_id: str) -> str:
		return f"user_{user_id}"

	def get_or_create_collection(self, user_id: str):
		return self.client.get_or_create_collection(self._collection_name(user_id))

	def add_texts(self, user_id: str, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
		embeddings = embed_texts(texts)
		collection = self.get_or_create_collection(user_id)
		collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)

	def similarity_search(self, user_id: str, query: str, k: int = 5, case_id: Optional[str] = None, document_ids: Optional[list] = None):
		collection = self.get_or_create_collection(user_id)
		query_emb = embed_texts([query])
		where = None
		if document_ids and len(document_ids) > 0:
			where = {"document_id": {"$in": document_ids}}
		elif case_id:
			where = {"case_id": case_id}
		res = collection.query(query_embeddings=query_emb, n_results=k, where=where)
		results: List[Dict[str, Any]] = []
		for i in range(len(res.get("ids", [[]])[0])):
			results.append({
				"id": res["ids"][0][i],
				"text": res["documents"][0][i],
				"score": res["distances"][0][i] if "distances" in res else 0.0,
				"metadata": res["metadatas"][0][i],
			})
		return results


vector_store = VectorStore()
