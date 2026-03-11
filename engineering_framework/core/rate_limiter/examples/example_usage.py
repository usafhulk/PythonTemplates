"""Rate Limiter Example."""
from engineering_framework.core.rate_limiter.core import TokenBucketRateLimiter

limiter = TokenBucketRateLimiter(rate=10.0, capacity=100.0)
for i in range(5):
    if limiter.acquire():
        print(f"Request {i+1}: allowed")
    else:
        print(f"Request {i+1}: rate limited")
