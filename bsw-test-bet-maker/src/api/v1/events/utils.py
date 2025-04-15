import httpx

http_client = httpx.AsyncClient()
events_cache = {"data": None, "expiry": 0}

def get_http_client() -> httpx.AsyncClient:
    return http_client

def get_events_cache() -> dict:
    return events_cache