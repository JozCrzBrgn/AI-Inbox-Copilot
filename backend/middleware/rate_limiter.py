from slowapi import Limiter

limiter = Limiter(key_func=lambda request: getattr(request.state, "user", request.client.host))