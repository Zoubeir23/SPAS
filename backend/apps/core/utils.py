"""
Utility functions for the core app.
"""


def get_client_ip(request):
    """
    Get the client's IP address from the request.

    Handles cases where the request comes through a proxy or load balancer.

    Args:
        request: Django/DRF request object

    Returns:
        str: IP address of the client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, get the first one
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_changes_dict(instance, validated_data):
    """
    Create a dictionary of changes between an instance and new data.

    Args:
        instance: The model instance being updated
        validated_data: Dictionary of new validated data

    Returns:
        dict: Dictionary with 'before' and 'after' keys showing changes
    """
    changes = {
        'before': {},
        'after': {}
    }

    for field, new_value in validated_data.items():
        old_value = getattr(instance, field, None)

        # Convert to string for comparison if needed
        if old_value != new_value:
            # Handle different types
            if hasattr(old_value, 'pk'):
                old_value = old_value.pk
            if hasattr(new_value, 'pk'):
                new_value = new_value.pk

            changes['before'][field] = old_value
            changes['after'][field] = new_value

    return changes if changes['before'] else None


def sanitize_sensitive_data(data, sensitive_fields=None):
    """
    Remove or mask sensitive data from a dictionary.

    Args:
        data: Dictionary to sanitize
        sensitive_fields: List of field names to mask (default: common sensitive fields)

    Returns:
        dict: Sanitized dictionary
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password',
            'token',
            'secret',
            'api_key',
            'access_token',
            'refresh_token',
            'ssn',
            'credit_card',
        ]

    if not isinstance(data, dict):
        return data

    sanitized = data.copy()

    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'

    return sanitized
