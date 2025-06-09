from sentence_transformers import SentenceTransformer
from typing import List, Tuple
from .chunker import Chunk
from ..core.config import settings

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model

def generate_embeddings_for_chunks(chunks: List[Chunk], model=None) -> List[Tuple[Chunk, List[float]]]:
    if model is None:
        model = get_embedding_model()
    texts = [chunk.text for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    # Convert to list properly
    if hasattr(embeddings, 'tolist'):
        embeddings_list = embeddings.tolist()
    elif isinstance(embeddings, list):
        embeddings_list = embeddings
    else:
        embeddings_list = list(embeddings)
    return list(zip(chunks, embeddings_list))

class EmbeddingGenerator:
    """Wrapper class for embedding generation functionality"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self.model = None
    
    def get_model(self):
        """Get or initialize the embedding model"""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        model = self.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        if hasattr(embeddings, 'tolist'):
            return embeddings.tolist()
        return embeddings
    
    def generate_embeddings_for_chunks(self, chunks: List[Chunk]) -> List[Tuple[Chunk, List[float]]]:
        """Generate embeddings for chunks"""
        return generate_embeddings_for_chunks(chunks, self.get_model())
