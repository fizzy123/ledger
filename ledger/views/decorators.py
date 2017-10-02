from functools import wraps
from flask import request, abort

from ledger import r_client

# Decorator to require an APIKEY in the header before allowing access to the route
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if r_client.get(request.headers.get('X-APIKEY')):
            return f(*args, **kwargs)
        abort(403)
    return decorated_function
