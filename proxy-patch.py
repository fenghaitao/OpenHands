"""Monkey patch httpx to use longer timeouts for corporate proxies."""
import httpx

# Store original classes and functions
_original_async_client = httpx.AsyncClient
_original_client = httpx.Client
_original_get = httpx.get
_original_post = httpx.post
_original_request = httpx.request

# Create patched AsyncClient with longer timeout
class PatchedAsyncClient(_original_async_client):
    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = httpx.Timeout(60.0)
        super().__init__(*args, **kwargs)

# Create patched Client with longer timeout
class PatchedClient(_original_client):
    def __init__(self, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = httpx.Timeout(60.0)
        super().__init__(*args, **kwargs)

# Patch convenience functions to use longer timeout
def patched_get(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 60.0
    return _original_get(*args, **kwargs)

def patched_post(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 60.0
    return _original_post(*args, **kwargs)

def patched_request(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 60.0
    return _original_request(*args, **kwargs)

# Replace httpx classes and functions with patched versions
httpx.AsyncClient = PatchedAsyncClient
httpx.Client = PatchedClient
httpx.get = patched_get
httpx.post = patched_post
httpx.request = patched_request
