"""Utility functions for test cases."""

class MockRequest404Response():
    """A mock of requests 404 response."""
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.status_code = 404

class MockRequest200Response():
    """A mock of request 200 response with custom text."""
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.status_code = 200
