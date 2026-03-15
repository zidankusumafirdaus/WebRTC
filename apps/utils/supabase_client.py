from typing import Optional
from supabase import create_client
from config import Config

_client: Optional[object] = None

def get_supabase_client():
    global _client
    if _client is None:
        url = getattr(Config, 'SUPABASE_URL', None)
        key = getattr(Config, 'SUPABASE_KEY', None)
        if not url or not key:
            raise RuntimeError('SUPABASE_URL or SUPABASE_KEY not set in Config')
        _client = create_client(url, key)
    return _client
