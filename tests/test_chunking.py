import pytest
from langchain.schema import Document

from app.services.chunking import chunk_documents


@pytest.fixture
def one_long_doc():
    # Create a dummy langchain Document Object
    text = "ABCDE" * 200
    return [Document(page_content=text, metadata = {"title":"my_doc"})]

@pytest.mark.parametrize(
    ("size","overlap","expected_min_chunks"),
    [
        (500, 50, 3),
        (800, 100, 2)
    ]
)


def test_chunking_splits_cleanly(one_long_doc, size, overlap, expected_min_chunks):
    chunks = chunk_documents(one_long_doc, chunk_size=size, chunk_overlap= overlap)
    # test number of chunks
    assert len(chunks) >= expected_min_chunks

    # test chunk overlap consistent
    if overlap > 0:
        for c1, c2 in zip(chunks, chunks[1:]):
            assert c1.page_content[-overlap:] == c2.page_content[:overlap]

    # test metadata preservation
    for c in chunks:
        assert c.metadata['title'] == "my_doc"

    

    