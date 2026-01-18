"""
Custom exception handlers for ONG ADJAHI Platform
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler that provides consistent error responses"""
    
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize error response format
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'code': response.status_code,
            }
        }
        
        # Add field-specific errors if available
        if isinstance(response.data, dict):
            custom_response_data['error']['details'] = response.data
        
        response.data = custom_response_data
    
    return response
