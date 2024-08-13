import re
from functools import lru_cache

class Route:
    type_map = {
        'int': int,
        'str': str,
        'float': float,
    }

    def __init__(self, pattern, controller):
        self.pattern = pattern
        self.controller = controller
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

    def match(self, url):
        match = self.regex.match(url)
        if match:
            params = match.groupdict()
            try:
                for key, value in params.items():
                    # Attempt to convert the parameters based on the type hint
                    params[key] = self.param_types[key](value)
            except (ValueError, TypeError):
                # If conversion fails, return None to indicate no match
                return None
            return params
        return None

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, pattern, controller):
        route = Route(pattern, controller)
        self.routes.append(route)

    @lru_cache(maxsize=100)
    def _match_url(self, url):
        for route in self.routes:
            params = route.match(url)
            if params is not None:
                return {
                    "controller": route.controller,
                    "params": params,
                }
        return None

    def match(self, url):
        return self._match_url(url)
