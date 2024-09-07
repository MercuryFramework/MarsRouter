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
		self.is_static = not re.search(r'{(\w+)(?::(\w+))?}', pattern)
		self.regex, self.param_types = self._parse_pattern(pattern)

	def _parse_pattern(self, pattern):
		param_types = {}
		def replace(match):
			param_name = match.group(1)
			param_type = match.group(2) if match.group(2) else 'str'
			param_types[param_name] = self.type_map.get(param_type, str)
			return f'(?P<{param_name}>[^/]+)'

		if self.is_static:
			return None, param_types  # No regex needed for static routes

		regex_pattern = re.sub(r'{(\w+)(?::(\w+))?}', replace, pattern)
		regex = re.compile(f'^{regex_pattern}$')
		return regex, param_types

	def match_url(self, url):
		""" Match the URL, returning params if dynamic or a boolean for static routes """
		if self.is_static:
			return {} if url == self.pattern else None	# Return empty params if it's a static route match
		else:
			match = self.regex.match(url)
			if match:
				params = match.groupdict()
				try:
					for key, value in params.items():
						# Attempt type conversion
						params[key] = self.param_types[key](value)
				except (ValueError, TypeError):
					# Return a special error for type mismatches
					return "type_error"
				return params
			return None

	def match_method(self, method):
		""" Check if the method is valid for this route """
		return method in self.methods


class Router:
	def __init__(self):
		self.routes = []
		self.error_handlers = {}

	def add_route(self, pattern, controller, methods=None):
		route = Route(pattern, controller, methods)
		self.routes.append(route)

	def add_error_handler(self, error_tag, handler):
		self.error_handlers[error_tag] = handler

	def _handle_error(self, error_tag, default_message, status_code):
		handler = self.error_handlers.get(error_tag)
		message = handler() if handler else default_message
		return {
			"controller": None,
			"error": message,
			"status_code": status_code
		}

	@lru_cache(maxsize=100)
	def match(self, url, method):
		matching_route = None
		method_mismatch = False

		# First, try to find a matching route based on URL
		for route in self.routes:
			params = route.match_url(url)
			if params == "type_error":
				return self._handle_error("type_mismatch", f"Type mismatch in route {route.pattern}", 400)
			elif params is not None:  # Match found for static or dynamic routes
				matching_route = route
				# If the method matches, return the controller and params
				if route.match_method(method):
					return {
						"controller": route.controller,
						"params": params,
						"status_code": 200
					}
				# If the URL matches but the method doesn't, set method_mismatch
				method_mismatch = True

		# If a matching route was found but the method was wrong, return 405
		if matching_route and method_mismatch:
			return self._handle_error("invalid_method", "Invalid method", 405)

		# Otherwise, return no matching route found
		return self._handle_error("no_route", "No matching route found", 404)

"""
# Example controller functions
def post_details(id=None):
	return f"Post details for ID {id}" if id else "Static page"

# Example of custom error handler
def my_invalid_method_handler():
	return "Custom invalid method error message"

# Example of custom type mismatch handler
def my_type_mismatch_handler():
	return "Custom type mismatch error message"

# Setting up the router and routes
router = Router()
router.add_route('/posts/id/{id:int}', post_details, methods=['GET'])
router.add_route('/posts/id/{id:int}', post_details, methods=['POST'])
router.add_route('/user/{username}', post_details, methods=['GET'])
router.add_route('/register', post_details, methods=['GET'])  # Static route

# Adding custom error handlers
router.add_error_handler("invalid_method", my_invalid_method_handler)
router.add_error_handler("type_mismatch", my_type_mismatch_handler)

# Matching URLs with methods
result = router.match('/posts/id/123', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/posts/id/123', 'POST')
print(result)  # Should match the POST route and return controller and params

result = router.match('/user/johndoe', 'GET')
print(result)  # Should match the GET route and return controller and params

result = router.match('/register', 'GET')
print(result)  # Should return the static page result

result = router.match('/posts/id/not-a-number', 'GET')
print(result)  # Should return custom type mismatch error message
"""
