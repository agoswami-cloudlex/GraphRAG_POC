from typing import List
from openai import AzureOpenAI
from app.config import settings


def get_client() -> AzureOpenAI:
	return AzureOpenAI(
		api_key=settings.azure_api_key,
		api_version=settings.azure_api_version,
		azure_endpoint=settings.azure_api_base,
	)


def embed_texts(texts: List[str]) -> List[List[float]]:
	client = get_client()
	resp = client.embeddings.create(
		input=texts,
		model=settings.azure_embedding_deployment,
	)
	return [d.embedding for d in resp.data]


def chat_complete(system_prompt: str, user_prompt: str) -> str:
	client = get_client()
	resp = client.chat.completions.create(
		model=settings.azure_chat_deployment,
		messages=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],
		temperature=0.2,
	)
	return resp.choices[0].message.content or ""
