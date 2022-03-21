import json

class Error(Exception):
    status_code = 500

    def _as_json(self):
        return json.dumps({
            'message': f'{self.status_code}: {self.args[0]}',
            'code': 0
        })

class Forbidden(Error):
    status_code = 403

class InvalidData(Error):
    status_code = 400
