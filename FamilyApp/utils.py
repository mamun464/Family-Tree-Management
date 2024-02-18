# utils.py

from rest_framework.views import exception_handler
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None and response.status_code == 401:
        response.data = {
            'success': False,
            'status': status.HTTP_401_UNAUTHORIZED,
            'message': 'User is not authenticated.',
        }
    
    return response
