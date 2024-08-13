from functools import lru_cache
import re

class Route:
	def __init__(self, pattern, controller):
		self.pattern = pattern
		self.controller = controller
		# Convert dynamic segments in the pattern to a regular expression
		self.regex = re.compile('^' + re.sub(r'{(\w+)}', r'(?P<\1>[^/]+)', pattern) + '$')

	def match(self, url):
		match = self.regex.match(url)
		if match:
			return match.groupdict()
		return None

class Router:
	def __init__(self):
		self.routes = []

	def add_route(self, pattern, controller):
		route = Route(pattern, controller)
		self.routes.append(route)

	@lru_cache(maxsize=100)
	def dispatch(self, url):
		for route in self.routes:
			params = route.match(url)
			if params is not None:
				return {
					"controller": route.controller,
					"params": params,
				}
		return None

"""
#Example Usage:

def user_profile(username):
	return f"Profile page for {username}"

def product_details(id):
	return f"Product details for ID {id}"

# Setting up the router and routes
router = Router()
router.add_route('/user/{username}', user_profile)
router.add_route('/product/{id}', product_details)

# Dispatching URLs
result = router.dispatch('/user/john')
if result:
	print(result)
	# Example of calling the controller manually with the params
	print(result['controller'](**result['params']))
else:
	print("404 Not Found")

result = router.dispatch('/product/123')
if result:
	print(result)
	print(result['controller'](**result['params']))
else:
	print("404 Not Found")

result = router.dispatch('/nonexistent')
if result:
	print(result)
else:
	print("404 Not Found")
"""
