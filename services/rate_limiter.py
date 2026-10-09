import time
from collections import defaultdict
from functools import wraps
from flask import request, jsonify, abort

class InMemoryRateLimiter:
    """
    Lightweight, thread-safe in-memory sliding window rate limiter.
    Protects compute-intensive AI endpoints without external Redis dependencies.
    """
    def __init__(self):
        self.requests = defaultdict(list)
        
    def is_allowed(self, key, limit=15, window_seconds=60):
        now = time.time()
        window_start = now - window_seconds
        
        # Clean older entries
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        if len(self.requests[key]) >= limit:
            return False
            
        self.requests[key].append(now)
        return True

limiter = InMemoryRateLimiter()

def rate_limit(limit=15, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            key = f"{client_ip}:{request.endpoint}"
            
            if not limiter.is_allowed(key, limit, window_seconds):
                if request.is_json:
                    return jsonify({
                        "status": "rate_limited",
                        "error": f"Rate limit exceeded: Maximum {limit} requests per {window_seconds}s. Please wait before submitting another query."
                    }), 429
                else:
                    return "Rate limit exceeded. Please wait a minute before making another request.", 429
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator
