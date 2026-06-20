"""RAG 파이프라인 (코어) — 정책 문서 Chroma 검색.

search_policy 가 4번째 툴이자, 그래프에서 **노드로 강제** 호출된다(설계 결정 1).
LLM 재량이 아니라 항상 검색 → "환불은 항상 정책 근거"를 보장.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
import requests

import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

_ROOT = Path(__file__).resolve().parents[3]
_POLICY_DIR = _ROOT / "data" / "policies"
_CHROMA_DIR = os.environ.get("CHROMA_DIR", str(_ROOT / "chroma_db"))
_COLLECTION = "payment_policies"


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Gemini HTTP API를 직접 호출하는 초경량 의존성 커스텀 임베딩 함수."""
    def __init__(self, api_key: str, model_name: str = "text-embedding-004"):
        self.api_key = api_key
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        for text in input:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:embedContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "content": {
                    "parts": [{"text": text}]
                }
            }
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            res.raise_for_status()
            embeddings.append(res.json()["embedding"]["values"])
        return embeddings


def get_embedding_function() -> EmbeddingFunction:
    """EMBEDDING_PROVIDER 환경변수에 기반하여 임베딩 함수 인스턴스를 동적으로 획득합니다."""
    provider = os.environ.get("EMBEDDING_PROVIDER", "local").lower()

    if provider == "openai":
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required when EMBEDDING_PROVIDER is 'openai'")
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        )
    elif provider in ("google", "gemini"):
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY is required when EMBEDDING_PROVIDER is 'google' or 'gemini'")
        model_name = os.environ.get("GOOGLE_EMBEDDING_MODEL", "text-embedding-004")
        return GeminiEmbeddingFunction(api_key=api_key, model_name=model_name)
    else:
        # Default local SentenceTransformer
        return embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )


def _chunk_markdown(text: str, source: str) -> list[dict[str, Any]]:
    """섹션 헤더 단위로 청크 분할. 각 청크에 source·section 메타 부여."""
    chunks: list[dict[str, Any]] = []
    # 첫 '## ' 이전(문서 제목)은 버리고 섹션 단위로 자른다.
    parts = re.split(r"\n(?=## )", text)
    for part in parts:
        part = part.strip()
        if not part.startswith("## "):
            continue
        section = part.splitlines()[0].lstrip("# ").strip()
        chunks.append({"text": part, "source": source, "section": section})
    return chunks


def _get_client() -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=_CHROMA_DIR)


def build_index() -> int:
    """정책 문서를 청크로 잘라 Chroma에 (재)인덱싱. 청크 개수 반환."""
    client = _get_client()
    embed_fn = get_embedding_function()

    # idempotent: 기존 컬렉션 삭제 후 재생성
    try:
        client.delete_collection(_COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(_COLLECTION, embedding_function=embed_fn)

    docs, metas, ids = [], [], []
    for md_path in sorted(_POLICY_DIR.glob("*.md")):
        chunks = _chunk_markdown(md_path.read_text(encoding="utf-8"), md_path.name)
        for i, ch in enumerate(chunks):
            docs.append(ch["text"])
            metas.append({"source": ch["source"], "section": ch["section"]})
            ids.append(f"{md_path.stem}-{i}")

    if docs:
        collection.add(documents=docs, metadatas=metas, ids=ids)
    return len(docs)


def search_policy(query: str, k: int = 3) -> dict[str, Any]:
    """[safe / 노드 강제] 정책 문서에서 query 관련 청크 k개 검색.

    반환: {ok, query, results:[{text, source, section, distance}]}
    results 가 faithfulness·context-precision 평가의 채점 대상이 된다.
    """
    client = _get_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(_COLLECTION, embedding_function=embed_fn)
    except Exception:
        return {"ok": False, "reason": "index not built — run build_index()", "query": query, "results": []}

    res = collection.query(query_texts=[query], n_results=k)
    results = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        results.append({"text": doc, "source": meta["source"], "section": meta["section"], "distance": dist})
    return {"ok": True, "query": query, "results": results}


if __name__ == "__main__":
    n = build_index()
    print(f"indexed {n} chunks into '{_COLLECTION}' at {_CHROMA_DIR}")
    demo = search_policy("100만원 넘는 환불은 어떻게 처리해?", k=2)
    for r in demo["results"]:
        print(f"  [{r['source']} · {r['section']}] dist={r['distance']:.3f}")
