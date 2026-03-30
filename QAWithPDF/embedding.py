from pathlib import Path

from llama_index.core import Settings, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.embeddings.gemini import GeminiEmbedding

from QAWithPDF.config import settings
from QAWithPDF.model_api import load_model

import sys
from QAWithPDF.exception import customexception
from logger import logging


def _configure_settings() -> None:
    Settings.llm = load_model()
    Settings.embed_model = GeminiEmbedding(model_name=settings.gemini_embedding_model_name)
    Settings.chunk_size = settings.chunk_size
    Settings.chunk_overlap = settings.chunk_overlap


def build_and_persist_index(documents, index_dir: str | Path):
    try:
        _configure_settings()
        index_path = Path(index_dir)
        index_path.mkdir(parents=True, exist_ok=True)

        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(str(index_path))
        logging.info("Index persisted at %s", index_path)
        return index
    except Exception as e:
        raise customexception(e, sys)


def load_query_engine(index_dir: str | Path, top_k: int | None = None):
    try:
        _configure_settings()
        index_path = Path(index_dir)
        if not index_path.exists():
            raise FileNotFoundError(f"Index directory does not exist: {index_path}")

        storage_context = StorageContext.from_defaults(persist_dir=str(index_path))
        index = load_index_from_storage(storage_context)
        similarity_top_k = top_k if isinstance(top_k, int) and top_k > 0 else settings.top_k
        return index.as_query_engine(similarity_top_k=similarity_top_k)
    except Exception as e:
        raise customexception(e, sys)


def download_gemini_embedding(model, document):
    Settings.llm = model
    Settings.embed_model = GeminiEmbedding(model_name=settings.gemini_embedding_model_name)
    Settings.chunk_size = settings.chunk_size
    Settings.chunk_overlap = settings.chunk_overlap
    index = VectorStoreIndex.from_documents(document)
    return index.as_query_engine(similarity_top_k=settings.top_k)