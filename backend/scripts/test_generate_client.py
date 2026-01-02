#!/usr/bin/env python
"""Test the generate endpoint with detailed error logging."""
import os
import sys
import django
import traceback

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

# Test with Django test client to catch all errors
from django.test import Client
from apps.users.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def test_generate():
    """Test the generate endpoint with full error tracing."""
    print("=" * 60)
    print("Testing Generate Endpoint")
    print("=" * 60)
    
    # Get admin user and token
    admin = User.objects.get(email='admin@isi.edu')
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    
    print(f"User: {admin.email}")
    print(f"Token: {access_token[:20]}...")
    
    # Create Django test client
    client = Client()
    
    # Make the request
    print("\nMaking POST request to /api/predictions/predictions/generate/...")
    
    try:
        response = client.post(
            '/api/predictions/predictions/generate/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.content.decode('utf-8')}")
        
        if response.status_code >= 400:
            print("\n!!! ERROR RESPONSE !!!")
            
    except Exception as e:
        print(f"\n!!! EXCEPTION !!!")
        print(f"Error: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_generate()
