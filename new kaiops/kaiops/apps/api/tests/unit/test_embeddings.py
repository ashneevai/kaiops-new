from app.platform.embeddings import chunk_text, cosine_similarity


def test_chunk_text_generates_multiple_chunks():
    text = "a" * 1500
    chunks = chunk_text(text, chunk_size=400, overlap=100)
    assert len(chunks) >= 4


def test_cosine_similarity_self_is_one():
    vector = [1.0, 0.0, -1.0]
    assert round(cosine_similarity(vector, vector), 5) == 1.0
