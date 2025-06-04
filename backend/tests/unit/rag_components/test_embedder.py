import pytest
from app.rag_components.chunker import Chunk
from app.rag_components import embedder

class DummyModel:
    def encode(self, texts, convert_to_numpy=True):
        # Return a list of fixed-length vectors (e.g., 3 floats)
        return [[float(i)]*3 for i in range(len(texts))]

def test_generate_embeddings_for_chunks():
    chunks = [
        Chunk(
            id=f"test_{i}",
            text=f"This is chunk {i}",
            article_title="Test Article",
            source_pdf_filename="test.pdf",
            page_numbers=[1],
            chunk_sequence_id=i,
            collection_id="col1",
            pdf_db_id=1
        ) for i in range(3)
    ]
    model = DummyModel()
    results = embedder.generate_embeddings_for_chunks(chunks, model=model)
    assert len(results) == 3
    for i, (chunk, emb) in enumerate(results):
        assert chunk.id == f"test_{i}"
        assert emb == [float(i)]*3
