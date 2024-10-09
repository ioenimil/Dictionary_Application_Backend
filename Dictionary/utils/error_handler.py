from rest_framework.exceptions import APIException

class CustomValidationError(APIException):
    status_code = 400  # You can change this based on the error type
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __init__(self, detail, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        self.detail = {'detail': detail}
