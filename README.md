# MarsRouter

MarsRouter is a lightweight and flexible dynamic routing system for Python.
It allows you to define URL patterns with dynamic segments and map them
to controller functions. The routing system matches incoming URLs to
the defined patterns, extracts dynamic parameters, and provides a simple
interface to handle requests based on these parameters.

# Features
- Dynamic URL pattern matching
- Simple function-based controllers
- Flexible parameter extraction
- Easy integration into existing Python projects

# Usage
```python3
router = Router()
router.add_route('/user/{username}', user_profile)
result = router.dispatch('/user/john')
# {'controller': user_profile, 'params': {'username': 'john'}}
```
