# app/core/limiter.py
from slowapi import Limiter
from slowapi.util import get_remote_address


def _rate_limit_key(request) -> str:
    """اگر کاربر لاگین است از user_id، وگرنه از IP."""
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    return get_remote_address(request)


limiter = Limiter(key_func=_rate_limit_key)