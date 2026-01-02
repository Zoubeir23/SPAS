#!/usr/bin/env python
"""Test the generate endpoint via Django test client."""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.test import RequestFactory
from rest_framework.test import force_authenticate
from apps.predictions.views import PredictionViewSet
from apps.users.models import User
import traceback


def test_generate_via_viewset():
    print("Testing generate via Django ViewSet directly...")
    
    # Get admin user
    admin = User.objects.filter(role='admin').first()
    print(f"User: {admin.email}")
    
    # Create request
    factory = RequestFactory()
    request = factory.post('/api/predictions/predictions/generate/', {}, content_type='application/json')
    force_authenticate(request, user=admin)
    
    # Create ViewSet and call generate
    viewset = PredictionViewSet.as_view({'post': 'generate'})
    
    try:
        response = viewset(request)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.data}")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()


if __name__ == '__main__':
    test_generate_via_viewset()
