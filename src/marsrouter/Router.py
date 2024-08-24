from functools import lru_cache
import re

class Route:
    type_map = {
        'int': int,
        'str': str,
        'float': float,
    }

    def __init__(self, pattern, controller, methods=None):
        self.pattern = pattern
        self.controller = controller
        self.methods = methods or ['GET']
        self.regex, self.param_types = self._parse_pattern(pattern)

    def _parse_pattern(self, pattern):
        param_types = {}
        def replace(match):
            param_name = match.group(1)
            param_type = match.group(2) if match.group(2) else 'str'
            param_types[param_name] = self.type_map.get(param_type, str)
            return f'(?P<{param_name}>[^/]+)'

        regex_pattern = re.sub(r'{(\w+)(?::(\w+))?}', replace, pattern)
        regex = re.compile(f'^{regex_pattern}$')
        return regex, param_types

    def match(self, url, method):
        if method not in self.methods:
            return None
        match = self.regex.match(url)
        if match:
            params = match.groupdict()
            try:
                for key, value in params.items():
                    params[key] = self.param_types[key](value)
            except (ValueError, TypeError):
                return None
            return params
        return None

class Router:
    def __init__(self):
        self.routes = []
        self.error_handlers = {}

    def add_route(self, pattern, controller, methods=None):
        route = Route(pattern, controller, methods)
        self.routes.append(route)

    def add_error_handler(self, error_tag, handler):
        self.error_handlers[error_tag] = handler

    @lru_cache(maxsize=100)
    def _match_url(self, url, method):
        for route in self.routes:
            params = route.match(url, method)
            if params is not None:
                return {
                    "controller": route.controller,
                    "params": params,
                    "status_code": 200
                }

        return self._handle_error("no_route", "No matching route found", 404)

    def match(self, url, method):
        match_result = self._match_url(url, method)
        if match_result.get("params") is None:
            return match_result

        for route in self.routes:
            if route.match(url, method) is None:
                return self._handle_error("invalid_method", "Invalid method", 405)

        return match_result

    def _handle_error(self, error_tag, default_message, status_code):
        handler = self.error_handlers.get(error_tag)
        message = handler() if handler else default_message
        return {
            "controller": None,
            "error": message,
            "status_code": status_code
        }

"""
# Example controller functions
def post_details(id):
    return f"Post details for ID {id}"

def create_post():
    return "Post created"

def user_profile(username):
    return f"Profile page for {username}"

# Example of custom error handler
def my_invalid_method_handler():
    return "Custom invalid method error message"

# Setting up the router and routes
router = Router()
router.add_route('/posts/id/{id:int}', post_details, methods=['GET'])
router.add_route('/posts/id/{id:int}', create_post, methods=['POST'])
router.add_route('/user/{username}', user_profile, methods=['GET'])

# Adding custom error handler
router.add_error_handler("invalid_method", my_invalid_method_handler)

# Matching URLs with methods
result = router.match('/posts/id/123', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/posts/id/123', 'POST')
print(result)  # Should match the POST route and return controller and params

result = router.match('/user/johndoe', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/user/johndoe', 'POST')
print(result)  # Should return custom invalid method error message

result = router.match('/posts/id/not-a-number', 'GET')
print(result)  # Should return a type mismatch error

"""
