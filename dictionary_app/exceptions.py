from rest_framework.exceptions import APIException

class CustomValidationError(APIException):
    status_code = 400
    default_detail = 'Validation error occurred.'
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
