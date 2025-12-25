import time
from fastapi import Request, HTTPException
from collections import defaultdict

class RateLimiter:
    """
    Simple in-memory Token Bucket Rate Limiter.
    """
    def __init__(self, requests_per_minute: int = 10):
        self.rate = requests_per_minute
        self.window = 60  # seconds
        self.clients = defaultdict(list)

    def check(self, ip: str):
        now = time.time()
        # Clean up old timestamps
        self.clients[ip] = [t for t in self.clients[ip] if now - t < self.window]
        
        if len(self.clients[ip]) >= self.rate:
            raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
        
        self.clients[ip].append(now)

rate_limiter = RateLimiter(requests_per_minute=10)
