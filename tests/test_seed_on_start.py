import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch


def _load_seed_module():
    path = Path(__file__).parent.parent / "scripts" / "seed_on_start.py"
    spec = importlib.util.spec_from_file_location("seed_on_start", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_forwards_api_key(monkeypatch):
    module = _load_seed_module()
    monkeypatch.setenv("API_KEY", "seed-key")
    response = Mock(status_code=200)
    response.json.return_value = {"indexed": 1, "chunks_created": 1}

    with patch.object(module, "wait_for_api", return_value=True), patch.object(
        module.requests, "post", return_value=response
    ) as post:
        assert module.seed_database() == 0

    assert post.call_args.kwargs["headers"] == {"X-API-Key": "seed-key"}


def test_seed_requires_api_key(monkeypatch):
    module = _load_seed_module()
    monkeypatch.delenv("API_KEY", raising=False)

    with patch.object(module, "wait_for_api", return_value=True), patch.object(module.requests, "post") as post:
        assert module.seed_database() == 1

    post.assert_not_called()
