"""
Standardized JSON Response Helper (Pure Python Standard Library)
"""

def success_response(data=None, message="Operation successful", code=200):
    return {
        "status": "success",
        "message": message,
        "data": data if data is not None else {}
    }, code

def error_response(message="An error occurred", code=400, data=None):
    return {
        "status": "error",
        "message": message,
        "data": data if data is not None else {}
    }, code
