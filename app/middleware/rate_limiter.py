# app/middleware/rate_limiter.py
from fastapi import Request, HTTPException
import time
from collections import defaultdict
import asyncio

class RateLimiter:
    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self.requests = defaultdict(list)
        
    async def __call__(self, request: Request):
        client_ip = request.client.host
        now = time.time()
        
        # Clean up old requests
        self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] if now - req_time < self.seconds]
        
        # Check if rate limit is exceeded
        if len(self.requests[client_ip]) >= self.times:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        
        # Add current request timestamp
        self.requests[client_ip].append(now)
        
        # Periodically clean up expired entries
        if len(self.requests) > 1000:  # Arbitrary number to avoid memory bloat
            asyncio.create_task(self._cleanup_old_ips())
    
    async def _cleanup_old_ips(self):
        now = time.time()
        for ip in list(self.requests.keys()):
            # Remove IPs that haven't made requests in twice the rate limit window
            if all(now - req_time > 2 * self.seconds for req_time in self.requests[ip]):
                del self.requests[ip]

# Add to main.py
from app.middleware.rate_limiter import RateLimiter

rate_limiter = RateLimiter(times=100, seconds=60)  # 100 requests per minute

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    await rate_limiter(request)
    return await call_next(request)