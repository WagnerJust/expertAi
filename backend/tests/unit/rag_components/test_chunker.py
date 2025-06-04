import pytest
from backend.app.rag_components.chunker import chunk_text, Chunk

@pytest.fixture
def sample_text():
    return "This is a test document. " * 100  # 600 words

@pytest.fixture
def page_info():
    return {0: [1], 1: [2]}

def test_chunk_text_basic(sample_text, page_info):
    chunks = chunk_text(
        text_content=sample_text,
        article_title="Test Article",
        pdf_filename="test.pdf",
        collection_id="col1",
        pdf_db_id=1,
        page_info=page_info,
        chunk_size=100,
        chunk_overlap=20
    )
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.id == f"test.pdf_chunk_{i}"
        assert chunk.article_title == "Test Article"
        assert chunk.source_pdf_filename == "test.pdf"
        assert chunk.collection_id == "col1"
        assert chunk.pdf_db_id == 1
        assert isinstance(chunk.page_numbers, list)
        assert isinstance(chunk.text, str)
        assert chunk.chunk_sequence_id == i

def test_chunk_text_overlap(sample_text, page_info):
    chunks = chunk_text(
        text_content=sample_text,
        article_title="Overlap Test",
        pdf_filename="overlap.pdf",
        collection_id="col2",
        pdf_db_id=2,
        page_info=page_info,
        chunk_size=50,
        chunk_overlap=25
    )
    assert len(chunks) > 1
    # Check overlap: the last 25 words of chunk 0 should be the first 25 of chunk 1
    first_chunk_words = chunks[0].text.split()
    second_chunk_words = chunks[1].text.split()
    assert first_chunk_words[-25:] == second_chunk_words[:25]
