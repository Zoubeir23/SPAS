"""
Custom exception handler for DRF.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import logging
import traceback

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response data
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'status_code': response.status_code,
            }
        }

        # Add detail if available
        if hasattr(response, 'data'):
            if isinstance(response.data, dict):
                custom_response_data['error']['details'] = response.data
            else:
                custom_response_data['error']['details'] = {'detail': response.data}

        response.data = custom_response_data

        # Log the error
        logger.error(
            f"API Error: {exc} - Status: {response.status_code}",
            exc_info=True,
            extra={'context': context}
        )
    else:
        # Handle unexpected errors
        logger.error(
            f"Unhandled Exception: {exc}",
            exc_info=True,
            extra={'context': context}
        )

        error_data = {
            'success': False,
            'error': {
                'message': 'An unexpected error occurred.',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            }
        }
        
        # In DEBUG mode, show full error details
        if settings.DEBUG:
            error_data['error']['message'] = str(exc)
            error_data['error']['traceback'] = traceback.format_exc()
        
        response = Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
