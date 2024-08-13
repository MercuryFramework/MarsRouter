import re
from functools import lru_cache

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
            param_types[param_name] = Route.type_map.get(param_type, str)
            return f'(?P<{param_name}>[^/]+)'

        regex_pattern = re.sub(r'{(\w+)(?::(\w+))?}', replace, pattern)
        regex = re.compile(f'^{regex_pattern}$')
        return regex, param_types

    def match(self, url):
        match = self.regex.match(url)
        if match:
            params = match.groupdict()
            try:
                for key, value in params.items():
                    params[key] = self.param_types[key](value)
            except (ValueError, TypeError):
                return None, {"controller": None, "error": f"Invalid type, '{self.pattern}'", "status_code": 400}
            return params, None
        return None, None

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, pattern, controller, methods=None):
        route = Route(pattern, controller, methods)
        self.routes.append(route)

    @lru_cache(maxsize=100)
    def _match_url(self, url, method):
        route_found = False
        for route in self.routes:
            params, error = route.match(url)
            if params is not None:
                if method in route.methods:
                    return {
                        "controller": route.controller,
                        "params": params,
                        "status_code": 200
                    }
                else:
                    route_found = True  # URL pattern matched but method did not
            if error:
                return error

        if route_found:
            return {"controller": None, "error": "Invalid method", "status_code": 405}
        return {"controller": None, "error": "Route not found", "status_code": 404}

    def match(self, url, method):
        return self._match_url(url, method)

#Testing
"""
# Example controller functions
def post_details(id):
    return f"Post details for ID {id}"

def create_post():
    return "Post created"

def user_profile(username):
    return f"Profile page for {username}"

# Setting up the router and routes
router = Router()
router.add_route('/posts/id/{id:int}', post_details, methods=['GET'])
router.add_route('/posts/id/{id:int}', create_post, methods=['POST'])
router.add_route('/user/{username}', user_profile, methods=['GET'])

# Matching URLs with methods
result = router.match('/posts/id/123', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/posts/id/123', 'POST')
print(result)  # Should match the POST route and return controller and params

result = router.match('/user/johndoe', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/user/johndoe', 'POST')
print(result)  # Should return error message since no POST method is defined for this route

result = router.match('/posts/id/not-a-number', 'GET')
print(result)  # Should return an error due to type mismatch

result = router.match('/nonexistent/path', 'GET')
print(result)  # Should return "Route not found"
"""
