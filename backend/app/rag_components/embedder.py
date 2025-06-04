from sentence_transformers import SentenceTransformer
from typing import List, Tuple
from backend.app.rag_components.chunker import Chunk
from backend.app.core.config import EMBEDDING_MODEL_NAME

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model

def generate_embeddings_for_chunks(chunks: List[Chunk], model=None) -> List[Tuple[Chunk, List[float]]]:
    if model is None:
        model = get_embedding_model()
    texts = [chunk.text for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return list(zip(chunks, embeddings.tolist()))
