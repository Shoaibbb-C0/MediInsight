# Tests must never read operator credentials or reach a configured cloud project.
import os
os.environ["SIMPLIFIER_LOAD_DOTENV"] = "0"
os.environ["ENVIRONMENT"] = "test"
for name in ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_PUBLISHABLE_KEY", "AUTH_MODE", "CORS_ORIGINS"]:
    os.environ.pop(name, None)
import pytest
from app.core import auth

@pytest.fixture(autouse=True)
def isolated_state(monkeypatch,tmp_path,request):
    monkeypatch.setenv('APP_DATA_DIR',str(tmp_path))
    monkeypatch.setenv("ENVIRONMENT", "development")
    if request.node.get_closest_marker('real_identity') is None:
        async def test_identity(request): return 'local_default_patient'
        monkeypatch.setattr(auth,'resolve_identity',test_identity)
