"""
Custom middleware for UTF-8 encoding in JSON responses.
"""
import json
from django.http import HttpResponse


class UTF8JSONResponseMiddleware:
    """
    Middleware to ensure UTF-8 encoding in JSON responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Force UTF-8 encoding for JSON responses
        content_type = response.get('Content-Type', '')
        if 'application/json' in content_type and 'charset' not in content_type:
            response['Content-Type'] = 'application/json; charset=utf-8'
        
        return response

