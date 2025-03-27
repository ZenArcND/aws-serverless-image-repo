import json
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

    def to_json(self):
        return json.dumps(self.to_dict())

    def get_response(self):
        result = self.to_dict()
        json_response = json.dumps(result)
        return json_response, result['status_code']
    

class ResourceNotFoundException(ApiException):
    def __init__(self, message):
        super().__init__(message, 404)