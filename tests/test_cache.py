import time
from brain.context.cache import ContextCache
from brain.context.assembler import ContextPackage

def test_context_cache_flow():
    ContextCache.clear()

    pkg = ContextPackage(project="CacheProj", goal="Build Cache", current_task="Setup Cache")

    # 1. Check misses
    cached = ContextCache.get("CacheProj", "Build Cache", "Setup Cache")
    assert cached is None

    # 2. Set cache
    ContextCache.set("CacheProj", "Build Cache", "Setup Cache", pkg)

    # 3. Check hits
    hit = ContextCache.get("CacheProj", "Build Cache", "Setup Cache")
    assert hit is not None
    assert hit.project == "CacheProj"

    # 4. Check TTL expiration
    hit_expired = ContextCache.get("CacheProj", "Build Cache", "Setup Cache", ttl_seconds=-1)
    assert hit_expired is None
