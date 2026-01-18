"""
Custom middleware for ONG ADJAHI Platform
"""

from django.utils.deprecation import MiddlewareMixin
from apps.common.models import AuditLog


class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log user actions for audit trail"""
    
    EXEMPT_PATHS = [
        '/api/schema/',
        '/api/docs/',
        '/static/',
        '/media/',
        '/admin/jsi18n/',
    ]
    
    def process_request(self, request):
        """Store request start time"""
        request._audit_start = None
        
        # Skip exempt paths
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return None
        
        return None
    
    def process_response(self, request, response):
        """Log successful requests"""
        
        # Skip if user not authenticated or exempt path
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        if any(request.path.startswith(path) for path in self.EXEMPT_PATHS):
            return response
        
        # Log only specific actions
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and response.status_code < 400:
            action_map = {
                'POST': 'CREATE',
                'PUT': 'UPDATE',
                'PATCH': 'UPDATE',
                'DELETE': 'DELETE',
            }
            
            try:
                AuditLog.objects.create(
                    user=request.user,
                    action=action_map.get(request.method, 'VIEW'),
                    model_name=self._extract_model_name(request.path),
                    description=f"{request.method} {request.path}",
                    ip_address=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                )
            except Exception:
                pass  # Don't fail request if audit log fails
        
        return response
    
    @staticmethod
    def _extract_model_name(path):
        """Extract model name from API path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 2 and parts[0] == 'api':
            return parts[1].replace('-', '_')
        return 'unknown'
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
