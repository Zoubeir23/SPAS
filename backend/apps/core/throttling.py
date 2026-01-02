"""
Custom throttling classes for rate limiting by user role.

Different user roles have different rate limits:
- ADMIN: Highest rate limits
- DS: High rate limits
- PEDAGOGICAL: Medium rate limits
- TEACHER: Standard rate limits
- Anonymous: Lowest rate limits
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class RoleBasedThrottle(UserRateThrottle):
    """
    Base class for role-based throttling.

    This class allows different rate limits based on user roles.
    """

    def get_cache_key(self, request, view):
        """
        Generate cache key based on user role.

        This allows different rate limits for different roles.
        """
        if not request.user or not request.user.is_authenticated:
            return super().get_cache_key(request, view)

        # Get user role
        user_role = getattr(request.user, 'role', 'unknown')
        ident = request.user.pk

        return self.cache_format % {
            'scope': f"{self.scope}_{user_role}",
            'ident': ident
        }


class AdminRateThrottle(RoleBasedThrottle):
    """
    Rate throttle for admin users.

    Rate: 10000 requests per hour (very high limit)
    """
    scope = 'admin'

    def allow_request(self, request, view):
        """Allow request if user is admin, otherwise use default throttling."""
        if request.user and request.user.is_authenticated and request.user.is_admin():
            # Set very high rate for admins
            self.rate = '10000/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)


class DSRateThrottle(RoleBasedThrottle):
    """
    Rate throttle for DS (Directeur des Études) users.

    Rate: 5000 requests per hour (high limit)
    """
    scope = 'ds'

    def allow_request(self, request, view):
        """Allow request with high rate for DS users."""
        if request.user and request.user.is_authenticated and request.user.is_ds():
            self.rate = '5000/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)


class PedagogicalRateThrottle(RoleBasedThrottle):
    """
    Rate throttle for pedagogical advisor users.

    Rate: 3000 requests per hour (medium-high limit)
    """
    scope = 'pedagogical'

    def allow_request(self, request, view):
        """Allow request with medium-high rate for pedagogical users."""
        if request.user and request.user.is_authenticated and request.user.is_pedagogical():
            self.rate = '3000/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)


class TeacherRateThrottle(RoleBasedThrottle):
    """
    Rate throttle for teacher users.

    Rate: 2000 requests per hour (standard limit)
    """
    scope = 'teacher'

    def allow_request(self, request, view):
        """Allow request with standard rate for teachers."""
        if request.user and request.user.is_authenticated and request.user.is_teacher():
            self.rate = '2000/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)


class BurstRateThrottle(UserRateThrottle):
    """
    Burst rate throttle to prevent rapid-fire requests.

    Rate: 60 requests per minute
    This prevents users from overwhelming the system with rapid requests.
    """
    scope = 'burst'
    rate = '60/min'


class SustainedRateThrottle(UserRateThrottle):
    """
    Sustained rate throttle for overall request limits.

    Rate: 1000 requests per hour (default for authenticated users)
    This is the baseline for all authenticated users.
    """
    scope = 'sustained'
    rate = '1000/hour'


class MLPredictionThrottle(UserRateThrottle):
    """
    Special throttle for ML prediction endpoints.

    ML predictions are resource-intensive, so they have stricter limits:
    - ADMIN/DS: 100 requests per hour
    - Others: 20 requests per hour

    Usage:
        throttle_classes = [MLPredictionThrottle]
    """
    scope = 'ml_prediction'

    def allow_request(self, request, view):
        """Apply strict rate limits for ML predictions."""
        if request.user and request.user.is_authenticated:
            if request.user.is_admin() or request.user.is_ds():
                self.rate = '100/hour'
            else:
                self.rate = '20/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        else:
            # Very low limit for unauthenticated users
            self.rate = '5/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)


class DataExportThrottle(UserRateThrottle):
    """
    Special throttle for data export endpoints.

    Data exports can be resource-intensive:
    - ADMIN/DS: 50 exports per hour
    - PEDAGOGICAL: 20 exports per hour
    - TEACHER: 10 exports per hour

    Usage:
        throttle_classes = [DataExportThrottle]
    """
    scope = 'data_export'

    def allow_request(self, request, view):
        """Apply rate limits based on user role for data exports."""
        if request.user and request.user.is_authenticated:
            if request.user.is_admin() or request.user.is_ds():
                self.rate = '50/hour'
            elif request.user.is_pedagogical():
                self.rate = '20/hour'
            elif request.user.is_teacher():
                self.rate = '10/hour'
            else:
                self.rate = '5/hour'
            self.num_requests, self.duration = self.parse_rate(self.rate)
        else:
            # No exports for unauthenticated users
            return False

        return super().allow_request(request, view)


class StrictAnonRateThrottle(AnonRateThrottle):
    """
    Strict rate limiting for anonymous users.

    Rate: 20 requests per hour
    This prevents abuse from unauthenticated users.
    """
    scope = 'anon_strict'
    rate = '20/hour'
