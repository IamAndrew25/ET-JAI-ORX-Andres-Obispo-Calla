from pathlib import Path

from app.services.ingestion.indexer import _document_id, index_documents_to_chroma


class FakeCollection:
    def __init__(self):
        self.records = {}

    def get(self, where, include):
        document_id = where["document_id"]
        return {
            "ids": [
                chunk_id
                for chunk_id, metadata in self.records.items()
                if metadata["document_id"] == document_id
            ]
        }

    def delete(self, ids):
        for chunk_id in ids:
            del self.records[chunk_id]


class FakeVectorStore:
    def __init__(self):
        self._collection = FakeCollection()
        self.added_ids = []
        self.added_documents = []

    def add_documents(self, documents, ids):
        self.added_documents.append(documents)
        self.added_ids.append(ids)
        for document, chunk_id in zip(documents, ids):
            self._collection.records[chunk_id] = document.metadata


def test_reindexing_replaces_document_with_stable_chunk_ids(tmp_path):
    file_path = Path(tmp_path / "document.md")
    file_path.write_text("# Title\n\nA stable document.", encoding="utf-8")
    vectorstore = FakeVectorStore()

    first = index_documents_to_chroma([file_path], vectorstore)
    second = index_documents_to_chroma([file_path], vectorstore)

    assert first == (1, 1, [])
    assert second == (1, 1, [])
    assert vectorstore.added_ids[0] == vectorstore.added_ids[1]
    assert len(vectorstore._collection.records) == 1


def test_seed_documents_have_distinct_stable_ids(tmp_path):
    first = Path(tmp_path / "first.md")
    second = Path(tmp_path / "second.md")

    assert _document_id(first) != _document_id(second)
