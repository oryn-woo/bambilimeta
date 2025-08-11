# Common Mistakes and Their Solutions

## 1. Django Tests Failing with 'No installed app with label "admin"'

### Error Message
```
LookupError: No installed app with label 'admin'.
```

### Cause
This error occurs when:
1. The `INSTALLED_APPS` setting is conditionally defined inside an `if not TESTING` block
2. Django can't find required apps (like 'admin') when running tests because the `INSTALLED_APPS` list is empty during test execution

### Problematic Code
```python
# settings.py
TESTING = "test" in sys.argv or "PYTEST_VERSION" in os.environ
if not TESTING:  # This is the issue!
    INSTALLED_APPS = [
        'django.contrib.admin',  # Not available during tests!
        # ... other apps
    ]
```

### Solution
1. Move `INSTALLED_APPS` outside of any conditional blocks
2. If you need to conditionally include apps for testing, create a separate list and extend `INSTALLED_APPS`

### Corrected Code
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Your apps
]

# Conditionally add test-only apps if needed
if "test" in sys.argv or "PYTEST_VERSION" in os.environ:
    INSTALLED_APPS += [
        'your_test_only_app',
    ]
```

### Prevention Tips
1. Always keep core Django apps in the main `INSTALLED_APPS` list
2. Only use conditional app loading for truly optional or test-specific apps
3. Test your test configuration by running `python manage.py test` after making changes to settings

### Debugging Steps
1. Check if `INSTALLED_APPS` is being overridden anywhere
2. Look for conditional logic that might affect app loading
3. Run tests with `-v 2` flag for more verbose output
4. Verify that all required Django apps are included in the list

### Related Issues
- Tests failing with database errors
- Missing template errors during tests
- Authentication/Authorization issues in test environment
