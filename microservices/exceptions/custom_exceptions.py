from datetime import datetime


class ApiException(Exception):

    def __init__(self, message, status_code):
        super().__init__(self)
        self.message = message
        self.status_code = 400 if status_code is None else status_code


    def to_dict(self):
        result = dict()

        result['result'] = 'ERR'
        result['info'] = self.message
        result['status_code'] = self.status_code
        result['timestamp'] = str(datetime.now())

        return result

    def to_json(self):
        return self.to_dict(), self.status_code

    def get_response(self):
        return self.to_dict(), self.status_code


class ResourceNotFoundException(ApiException):
    def __init__(self, message):
        super().__init__(message, 404)