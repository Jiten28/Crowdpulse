"""
Minimal in-memory rate limiter, keyed by client IP. Deliberately simple:
a dict of recent request timestamps per key, pruned on each check. Good
enough for a single-instance demo deployment and avoids pulling in an
extra dependency (slowapi) for something this small — see Rules.md §1.
"""
import time
from collections import defaultdict
from typing import Dict, List

_requests: Dict[str, List[float]] = defaultdict(list)


def is_allowed(key: str, max_per_minute: int) -> bool:
    """Returns True and records the request if the key is under its per-minute limit, else False."""
    now = time.time()
    window_start = now - 60
    _requests[key] = [t for t in _requests[key] if t > window_start]
    if len(_requests[key]) >= max_per_minute:
        return False
    _requests[key].append(now)
    return True
