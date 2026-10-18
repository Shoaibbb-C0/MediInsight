import pytest
from app.core import auth

@pytest.fixture(autouse=True)
def isolated_state(monkeypatch,tmp_path,request):
    monkeypatch.setenv('APP_DATA_DIR',str(tmp_path))
    if request.node.get_closest_marker('real_identity') is None:
        async def test_identity(request): return 'local_default_patient'
        monkeypatch.setattr(auth,'resolve_identity',test_identity)
